#!/usr/bin/env python3
"""Build BF-owned Android code, validate on a device, then time equal byte transfers.

NDK/Rust/Java compile benchmark infrastructure and baselines only. The two
existing independent BF seeds execute the six unmodified BF compiler stages.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests')]
from run_android_loops import STAGES, compile_source
from reference import execute
from verify_android_aarch64_subset import check_elf, emulate

REMOTE = '/data/local/tmp/brainfuck-bench'
BUILD = ROOT / 'build/android_benchmark'


def run(command, **kwargs):
    return subprocess.run([str(x) for x in command], capture_output=True,
                          check=True, timeout=60, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--sdk', type=Path, default=Path(os.environ['LOCALAPPDATA']) / 'Android/Sdk')
    parser.add_argument('--java-home', type=Path, default=Path(r'C:\Program Files\Android\Android Studio\jbr'))
    parser.add_argument('--rustc', default=str(Path.home() / '.cargo/bin/rustc.exe'))
    args = parser.parse_args()
    devices = run([args.adb, 'devices']).stdout.decode().splitlines()[1:]
    connected = [line.split()[0] for line in devices if line.endswith('\tdevice')]
    if len(connected) != 1:
        raise SystemExit(f'Expected one authorized Android device; found {len(connected)}')
    adb = [args.adb, '-s', connected[0]]

    def shell(command):
        return run(adb + ['shell', '-T', command])

    def push(local, name):
        run(adb + ['push', local, f'{REMOTE}/{name}'])

    def text(command):
        return shell(command).stdout.decode(errors='replace').strip()

    if text('getprop ro.product.cpu.abi') != 'arm64-v8a':
        raise SystemExit('This prototype requires an arm64-v8a device')
    frequencies = text('for cpu in /sys/devices/system/cpu/cpu[0-9]*; do '
                       'if [ -r "$cpu/cpufreq/cpuinfo_max_freq" ]; then '
                       'printf "%s " "$cpu"; cat "$cpu/cpufreq/cpuinfo_max_freq"; fi; done')
    cores = [(int(freq), int(cpu)) for cpu, freq in re.findall(r'/cpu(\d+)\s+(\d+)', frequencies)]
    if not cores:
        raise SystemExit('CPU maximum frequencies unavailable; cannot select a common benchmark core')
    max_khz, cpu = max(cores)
    BUILD.mkdir(parents=True, exist_ok=True)
    shell(f'mkdir -p {REMOTE}')
    versions = lambda folder: max((p for p in folder.iterdir() if p.is_dir() and p.name[0].isdigit()),
                                  key=lambda p: tuple(int(x) for x in p.name.split('.')))
    ndk = versions(args.sdk / 'ndk')
    clang = ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    builds = {}

    def build_c(name, source, optimization, *extra):
        start = time.perf_counter_ns()
        run([clang, '--target=aarch64-linux-android26', optimization, *extra, '-Wall', '-Wextra',
             source, '-o', BUILD / name])
        builds[name] = {'compile_ms': (time.perf_counter_ns() - start) / 1e6,
                        'bytes': (BUILD / name).stat().st_size, 'sha256': digest(BUILD / name)}
        push(BUILD / name, name)
        shell(f'chmod 700 {REMOTE}/{name}')

    for name, source in [('seed', 'seed_interpreter.c'), ('seed_alt', 'seed_interpreter_alt.c')]:
        build_c(name, ROOT / 'bootstrap' / source, '-O2')
    for name, (source, _) in STAGES.items():
        push(ROOT / source, f'{name}.bf')

    def stage(seed):
        def execute_stage(name, payload):
            (BUILD / 'payload').write_bytes(payload)
            push(BUILD / 'payload', 'payload')
            # File redirection avoids ADB stdin EOF and binary shell-stream quirks.
            shell(f'{REMOTE}/{seed} {REMOTE}/{name}.bf < {REMOTE}/payload > {REMOTE}/stage.out')
            run(adb + ['pull', f'{REMOTE}/stage.out', BUILD / 'stage.out'])
            return (BUILD / 'stage.out').read_bytes()
        return execute_stage

    source = (ROOT / 'examples/android_loop_demo.bf').read_bytes()
    start = time.perf_counter_ns()
    image = compile_source(source, stage_runner=stage('seed'))
    bf_compile_ms = (time.perf_counter_ns() - start) / 1e6
    assert image == compile_source(source, stage_runner=stage('seed_alt')), 'Independent seeds disagree'
    assert image == (ROOT / 'build/android_aarch64_loop_demo.elf').read_bytes(), 'Archived image differs'
    check_elf(image)
    (BUILD / 'brainfuck').write_bytes(image)
    push(BUILD / 'brainfuck', 'brainfuck')
    shell(f'chmod 700 {REMOTE}/brainfuck')
    builds['brainfuck'] = {'compile_ms': bf_compile_ms, 'bytes': len(image),
                          'sha256': digest(BUILD / 'brainfuck')}
    print('PASS: both independent BF seeds on Android emit the archived loop image', flush=True)

    build_c('c', ROOT / 'benchmarks/baselines/android_transfer.c', '-O3')
    build_c('c_static', ROOT / 'benchmarks/baselines/android_transfer.c', '-O3',
            '-static', '-Wl,--gc-sections', '-s')
    objdump = clang.with_name('llvm-objdump.exe')
    disassembly = run([objdump, '-d', '--disassemble-symbols=main', BUILD / 'c']).stdout
    (BUILD / 'c_main_disassembly.txt').write_bytes(disassembly)
    build_c('sample', ROOT / 'benchmarks/android_process_sample.c', '-O2')
    start = time.perf_counter_ns()
    run([args.rustc, '-O', '--target=aarch64-linux-android',
         '-C', f'linker={clang}', '-C', 'link-arg=--target=aarch64-linux-android26',
         ROOT / 'benchmarks/baselines/android_transfer.rs', '-o', BUILD / 'rust'])
    builds['rust'] = {'compile_ms': (time.perf_counter_ns() - start) / 1e6,
                      'bytes': (BUILD / 'rust').stat().st_size, 'sha256': digest(BUILD / 'rust')}
    push(BUILD / 'rust', 'rust')
    shell(f'chmod 700 {REMOTE}/rust')
    java = args.java_home / 'bin/java.exe'
    javac = args.java_home / 'bin/javac.exe'
    start = time.perf_counter_ns()
    run([javac, '--release', '8', '-d', BUILD, ROOT / 'benchmarks/baselines/AndroidTransfer.java'])
    d8 = versions(args.sdk / 'build-tools') / 'lib/d8.jar'
    run([java, '-cp', d8, 'com.android.tools.r8.D8', '--release', '--min-api', '26',
         '--output', BUILD, BUILD / 'AndroidTransfer.class'])
    builds['java_dex'] = {'compile_ms': (time.perf_counter_ns() - start) / 1e6,
                          'bytes': (BUILD / 'classes.dex').stat().st_size,
                          'sha256': digest(BUILD / 'classes.dex')}
    push(BUILD / 'classes.dex', 'classes.dex')
    programs = {'brainfuck': f'{REMOTE}/brainfuck', 'c': f'{REMOTE}/c',
                'c_static': f'{REMOTE}/c_static', 'rust': f'{REMOTE}/rust',
                'java_art_jit_enabled': f'dalvikvm -Xusejit:true -cp {REMOTE}/classes.dex AndroidTransfer',
                'java_art_interpreted': f'dalvikvm -Xint -cp {REMOTE}/classes.dex AndroidTransfer'}

    def sample(name, value):
        result = text(f'taskset -c {cpu} {REMOTE}/sample {value} {programs[name]}').split()
        assert len(result) == 2, result
        elapsed, rss = map(int, result)
        assert elapsed > 0 and rss > 0, result
        return elapsed / 1e6, rss

    for value, command, status in [(256, programs['brainfuck'], 64),
                                    (173, '/system/bin/true', 65),
                                    (173, '/system/bin/false', 65)]:
        invalid = subprocess.run(adb + ['shell', '-T', f'{REMOTE}/sample {value} {command}'],
                                 capture_output=True, timeout=30)
        assert invalid.returncode == status, (value, command, invalid)

    # Differential contract checks and an untimed startup warmup for every mode.
    correctness = 0
    for value in [-1, 0, 1, 10, 13, 65, 173, 255]:
        data = b'' if value < 0 else bytes([value])
        expected, _ = execute(source, data)
        simulated, status, _ = emulate(image, 0, input_bytes=data, max_steps=100000)
        assert simulated == expected == bytes([max(value, 0)]) and status == 0
        for name in programs:
            sample(name, value)
            correctness += 1

    witnesses = []
    for label, program, status in [('empty', b'', 0), ('nested', b'[[]]', 0),
                                    ('left_boundary', b'<', 2), ('right_boundary', b'+[>+]', 2)]:
        artifact = compile_source(program, stage_runner=stage('seed'))
        check_elf(artifact)
        local = BUILD / label
        local.write_bytes(artifact)
        push(local, label)
        shell(f'chmod 700 {REMOTE}/{label}')
        result = subprocess.run(adb + ['shell', '-T', f'{REMOTE}/{label}'],
                                capture_output=True, timeout=30)
        assert result.returncode == status and result.stdout == b'', (label, result)
        witnesses.append({'case': label, 'exit_status': status, 'sha256': digest(local)})
    for rejected in (b'[', b'+' * 11):
        try:
            compile_source(rejected, stage_runner=stage('seed'))
        except ValueError:
            pass
        else:
            raise AssertionError(f'Invalid source accepted: {rejected!r}')
    print(f'PASS: {correctness} baseline byte checks, 4 native witnesses, 2 compilation rejections', flush=True)

    before = text('dumpsys battery')
    samples = {name: [] for name in programs}
    memory = {name: [] for name in programs}
    rng = random.Random(20261012)
    for _ in range(31):
        order = list(programs)
        rng.shuffle(order)
        for name in order:
            ms, rss = sample(name, 173)
            samples[name].append(ms)
            memory[name].append(rss)
    data = {name: {'raw_ms': values, 'median_ms': statistics.median(values),
                   'peak_rss_kib': max(memory[name]), 'command': programs[name]}
            for name, values in samples.items()}
    fastest = min((name for name in programs if name != 'brainfuck'), key=lambda name: data[name]['median_ms'])
    bf_ms = data['brainfuck']['median_ms']
    baseline_ms = data[fastest]['median_ms']
    ratio = baseline_ms / bf_ms
    # Bootstrap the median ratio; this still cannot fix startup/thermal confounding.
    ratios = []
    for _ in range(10000):
        base = statistics.median(rng.choices(samples[fastest], k=31))
        bf = statistics.median(rng.choices(samples['brainfuck'], k=31))
        ratios.append(base / bf)
    ratios.sort()
    ci = [ratios[250], ratios[9749]]
    report = {'date': '2026-10-12', 'classification': 'MEASURED Android fresh-process byte-transfer workload',
              'performance_objective': 'Brainfuck speed greater than the fastest same-device baseline',
              'objective_status': 'NOT_ESTABLISHED',
              'sample_status': 'BF_FASTER_WITH_95_PERCENT_INTERVAL' if ci[0] > 1 else 'BF_NOT_PROVEN_FASTER',
              'fastest_baseline': fastest, 'speed_ratio_baseline_ms_over_bf_ms': ratio,
              'speed_ratio_bootstrap_95_percent_interval': ci,
              'device': {'model': text('getprop ro.product.model'), 'android': text('getprop ro.build.version.release'),
                         'api': text('getprop ro.build.version.sdk'), 'kernel': text('uname -a'),
                         'benchmark_cpu': cpu, 'cpu_max_frequency_khz': max_khz,
                         'cpu_governor': text(f'cat /sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'),
                         'page_size': text('getconf PAGESIZE'),
                         'battery_before': before, 'battery_after': text('dumpsys battery')},
              'toolchains': {'clang': run([clang, '--version']).stdout.decode().splitlines()[0],
                             'rustc': run([args.rustc, '--version']).stdout.decode().strip(),
                             'java': run([java, '-version']).stderr.decode().strip(),
                             'd8': run([java, '-cp', d8, 'com.android.tools.r8.D8', '--version']).stdout.decode().strip()},
              'compiler_source_sha256': digest(ROOT / 'compiler/core.bf'),
              'bf_stages': {name: digest(ROOT / src) for name, (src, _) in STAGES.items()},
              'workload_source_sha256': digest(ROOT / 'examples/android_loop_demo.bf'),
              'baseline_source_sha256': {name: digest(ROOT / 'benchmarks/baselines' / name)
                                         for name in ['android_transfer.c', 'android_transfer.rs', 'AndroidTransfer.java']},
              'harness_source_sha256': digest(ROOT / 'benchmarks/android_process_sample.c'),
              'diagnosis': 'C -O3 eliminates the byte-transfer loop; BF retains the loop and checked pointer moves in 48-byte slots',
              'c_main_disassembly_sha256': digest(BUILD / 'c_main_disassembly.txt'),
              'builds': builds, 'correctness_checks': correctness, 'harness_rejections': 3,
              'device_witnesses': witnesses,
              'independent_bf_seed_images_identical': True, 'archived_native_image_identical': True,
              'compilation_rejections': 2, 'input_hex': 'ad', 'output_hex': 'ad', 'rounds': 31,
              'warmup': 'Eight contract executions per mode; fresh VM each sample, no steady-state JIT warmup',
              'data': data,
              'limitations': ['Only a ten-command byte-transfer workload, not a full application or APK',
                             'Includes fork/exec, loader, allocation, byte I/O and shutdown; excludes ADB transport',
                             'JIT enabled does not prove this short Java method was JIT compiled',
                             'DEX is bytecode executed by ART, not an independent execution engine',
                             'No same-device HotSpot JVM available; host JVM timings are not comparable',
                             'No Android-native compiler self-hosting; BF stages run under independent interpreters',
                             'All variants pinned to the highest rated frequency core; frequency, background load and thermal state uncontrolled',
                             'Median bootstrap interval is exploratory, not general performance proof',
                             'Peak RSS includes runtime; BF compile time includes device transport',
                             'No Linux release gates rerun: WSL/Linux unavailable and core.bf unchanged']}
    destination = ROOT / 'benchmarks/results/android_transfer.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    for name, result in data.items():
        print(f"{name}: {result['median_ms']:.4f} ms, peak RSS {result['peak_rss_kib']} KiB")
    print(f'BF speed / {fastest} speed: {ratio:.4f}x; bootstrap 95% interval {ci}; broader goal NOT ESTABLISHED')
    return report


if __name__ == '__main__':
    main()

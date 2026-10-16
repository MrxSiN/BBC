#!/usr/bin/env python3
"""Rebuild and measure equal byte transfers on Android; no compiler logic here."""
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
sys.path.insert(0, str(ROOT / 'bootstrap'))
from local_seed import LocalSeedRunner
from run_android_optimized import compile_optimized_source


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    return subprocess.run([str(x) for x in command], check=True, capture_output=True, timeout=60)


def interval(samples, bf, baselines, rng):
    count = len(samples[bf])
    ratios = []
    for _ in range(10000):
        indexes = rng.choices(range(count), k=count)
        best = min(statistics.median(samples[name][i] for i in indexes) for name in baselines)
        measured = statistics.median(samples[bf][i] for i in indexes)
        ratios.append(best / measured)
    ratios.sort()
    return [ratios[250], ratios[9749]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--serial', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rounds', type=int, default=101)
    args = parser.parse_args()
    if args.rounds < 31:
        parser.error('at least 31 rounds required')
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output must be absent or empty; preserve prior measurements')
    out.mkdir(parents=True, exist_ok=True)
    adb = [args.adb, '-s', args.serial]
    remote = '/data/local/tmp/bfc_followup_20261013'

    def shell(command):
        return run(adb + ['shell', '-T', command]).stdout.decode(errors='replace').strip()

    def push(path):
        run(adb + ['push', path, f'{remote}/{path.name}'])
        # Hash the device bytes independently of adb's transfer status.
        assert shell(f'sha256sum {remote}/{path.name}').split()[0] == digest(path)

    props = {key: shell('getprop ' + key) for key in
             ('ro.product.model', 'ro.product.cpu.abi', 'ro.build.version.release',
              'ro.build.version.sdk', 'ro.build.fingerprint')}
    assert props['ro.product.cpu.abi'] == 'arm64-v8a'
    frequencies = shell('for c in /sys/devices/system/cpu/cpu[0-9]*; do '
                        'if [ -r "$c/cpufreq/cpuinfo_max_freq" ]; then '
                        'printf "%s " "$c"; cat "$c/cpufreq/cpuinfo_max_freq"; fi; done')
    max_khz, cpu = max((int(freq), int(core)) for core, freq in
                      re.findall(r'/cpu(\d+)\s+(\d+)', frequencies))
    shell(f'mkdir -p {remote}')
    sdk = Path(os.environ['LOCALAPPDATA']) / 'Android/Sdk'
    latest = lambda folder: max((p for p in folder.iterdir() if p.is_dir() and p.name[0].isdigit()),
                                key=lambda p: tuple(int(x) for x in p.name.split('.')))
    clang = latest(sdk / 'ndk') / 'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    rustc = Path.home() / '.cargo/bin/rustc.exe'
    java_home = Path(r'C:\Program Files\Android\Android Studio\jbr')
    java = java_home / 'bin/java.exe'
    builds = {}
    sources = {}

    def build(name, source, command):
        started = time.perf_counter_ns()
        result = run(command + ['-o', out / name])
        if result.stderr:
            (out / (name + '.build.stderr')).write_bytes(result.stderr)
        builds[name] = {'sha256': digest(out / name), 'bytes': (out / name).stat().st_size,
                        'compile_ms': (time.perf_counter_ns() - started) / 1e6,
                        'command': [str(x) for x in command]}
        sources[str(source.relative_to(ROOT))] = digest(source)
        push(out / name)
        shell(f'chmod 700 {remote}/{name}')

    source = ROOT / 'examples/android_loop_demo.bf'
    runner = LocalSeedRunner()
    image = compile_optimized_source(source.read_bytes(), stage_runner=runner)
    runner.seed = 'seed_alt'
    assert image == compile_optimized_source(source.read_bytes(), stage_runner=runner)
    (out / 'brainfuck').write_bytes(image)
    builds['brainfuck'] = {'sha256': digest(out / 'brainfuck'), 'bytes': len(image),
                           'production_codegen': 'standard Brainfuck, two independent interpreter seeds agree'}
    sources[str(source.relative_to(ROOT))] = digest(source)
    push(out / 'brainfuck'); shell(f'chmod 700 {remote}/brainfuck')
    for name, filename, flags in (
        ('sample', 'benchmarks/android_process_sample.c', ['-O2']),
        ('c_dynamic', 'benchmarks/baselines/android_transfer.c', ['-O3']),
        ('c_static', 'benchmarks/baselines/android_transfer.c', ['-O3', '-static', '-s'])):
        src = ROOT / filename
        build(name, src, [clang, '--target=aarch64-linux-android26', *flags, src])
    src = ROOT / 'benchmarks/baselines/android_transfer_freestanding.c'
    for name, level, direct in [('c_freestanding_o3', '-O3', False),
                                 ('c_freestanding_oz', '-Oz', False), ('c_direct_echo', '-O3', True)]:
        flags = [level, '-flto', '-fno-stack-protector', '-fno-unwind-tables',
                 '-fno-asynchronous-unwind-tables', '-nostdlib', '-static',
                 '-Wl,-e,_start,--gc-sections,--no-rosegment', '-s']
        if direct: flags.append('-DDIRECT_ECHO')
        build(name, src, [clang, '--target=aarch64-linux-android26', *flags, src])
    for name, filename, freestanding in (
        ('rust_std', 'android_transfer.rs', False),
        ('rust_direct_echo', 'android_transfer_freestanding.rs', True)):
        src = ROOT / 'benchmarks/baselines' / filename
        flags = ['-O', '--target=aarch64-linux-android', '-C', f'linker={clang}',
                 '-C', 'link-arg=--target=aarch64-linux-android26']
        if freestanding:
            flags += ['--cfg', 'direct_echo', '-C', 'lto=fat', '-C', 'codegen-units=1',
                      '-C', 'panic=abort', '-C', 'strip=symbols', '-C', 'link-arg=-nostdlib',
                      '-C', 'link-arg=-static', '-C', 'link-arg=-Wl,-e,_start,--no-rosegment']
        build(name, src, [rustc, *flags, src])
    src = ROOT / 'benchmarks/baselines/AndroidTransfer.java'
    run([java_home / 'bin/javac.exe', '--release', '8', '-d', out, src])
    d8 = latest(sdk / 'build-tools') / 'lib/d8.jar'
    run([java, '-cp', d8, 'com.android.tools.r8.D8', '--release', '--min-api', '26',
         '--output', out, out / 'AndroidTransfer.class'])
    sources[str(src.relative_to(ROOT))] = digest(src)
    builds['java_dex'] = {'bytes': (out / 'classes.dex').stat().st_size, 'sha256': digest(out / 'classes.dex')}
    push(out / 'classes.dex')
    programs = {name: f'{remote}/{name}' for name in builds if name not in ('sample', 'java_dex')}
    programs.update(java_art_jit_enabled=f'dalvikvm -Xusejit:true -cp {remote}/classes.dex AndroidTransfer',
                    java_art_interpreted=f'dalvikvm -Xint -cp {remote}/classes.dex AndroidTransfer')
    checks = 0
    for name, command in programs.items():
        values = list(range(256)) + [-1] if not name.startswith('java') else [-1, 0, 1, 10, 13, 65, 173, 255]
        lines = shell('set -e; ' + '; '.join(f'{remote}/sample {v} {command}' for v in values)).splitlines()
        assert len(lines) == len(values), name
        checks += len(values)
    # A wrong output and invalid input must fail before timing can be trusted.
    for value, command, status in [(256, programs['brainfuck'], 64), (173, '/system/bin/true', 65),
                                   (173, '/system/bin/false', 65)]:
        result = subprocess.run(adb + ['shell', '-T', f'{remote}/sample {value} {command}'], capture_output=True)
        assert result.returncode == status
    print(f'PASS: {checks} byte/EOF checks and 3 harness rejection checks', flush=True)
    before = shell('dumpsys battery')
    rng = random.Random(20261013)
    samples = {name: [] for name in programs}
    rss = {name: [] for name in programs}
    raw = []
    for block in range(0, args.rounds, 10):
        commands = ['set -e']
        for _ in range(min(10, args.rounds - block)):
            order = list(programs); rng.shuffle(order)
            commands += [f'printf "{name} "; taskset -c {cpu} {remote}/sample 173 {programs[name]}' for name in order]
        schedule = out / 'schedule.sh'
        schedule.write_bytes(('\n'.join(commands) + '\n').encode())
        push(schedule)
        lines = shell(f'sh {remote}/schedule.sh').splitlines()
        for line in lines:
            name, ns, memory = line.split()
            assert int(ns) > 0 and int(memory) > 0
            samples[name].append(int(ns) / 1e6); rss[name].append(int(memory))
        raw.extend(lines)
        (out / 'raw_process_samples.txt').write_text('\n'.join(raw) + '\n')
        print(f'Completed {len(raw)}/{args.rounds * len(programs)} samples', flush=True)
    assert all(len(x) == args.rounds for x in samples.values())
    data = {name: {'median_ms': statistics.median(x), 'raw_ms': x, 'peak_rss_kib': max(rss[name]),
                   'command': programs[name]} for name, x in samples.items()}
    baselines = [name for name in programs if name != 'brainfuck']
    best = min(baselines, key=lambda n: data[n]['median_ms'])
    ci = interval(samples, 'brainfuck', baselines, rng)
    assert interval({'bf': [2] * 31, 'c': [1] * 31}, 'bf', ['c'], random.Random(1)) == [0.5, 0.5]
    report = {'date': '2026-10-13', 'classification': 'ANDROID_DEVICE_EXECUTED fresh-process byte transfer',
              'device_properties': props, 'serial': args.serial, 'cpu': cpu, 'max_frequency_khz': max_khz,
              'page_bytes': int(shell('getconf PAGESIZE')), 'rounds': args.rounds, 'correctness_checks': checks,
              'harness_rejection_checks': 3, 'builds': builds, 'sources': sources, 'data': data,
              'fastest_baseline': best, 'speed_ratio_baseline_over_bf': data[best]['median_ms'] / data['brainfuck']['median_ms'],
              'paired_bootstrap_95_percent_interval': ci,
              'sample_status': 'BF_FASTER_ON_THIS_WORKLOAD' if ci[0] > 1 else 'NOT_PROVEN_FASTEST',
              'general_performance_objective': 'NOT_ESTABLISHED',
              'compiler_source_sha256': digest(ROOT / 'compiler/core.bf'),
              'harness_sha256': digest(Path(__file__)),
              'toolchains': {'clang': run([clang, '--version']).stdout.decode().splitlines()[0],
                             'rustc': run([rustc, '--version']).stdout.decode().strip(),
                             'java': run([java, '-version']).stderr.decode().strip(),
                             'd8': run([java, '-cp', d8, 'com.android.tools.r8.D8', '--version']).stdout.decode().strip()},
              'battery_before': before, 'battery_after': shell('dumpsys battery'),
              'limitations': ['Includes fork/exec, loader, byte I/O and shutdown; excludes ADB transport',
                              'Java fresh VM with JIT enabled does not establish warmed JIT performance',
                              'DEX executes under ART; no same-device HotSpot JVM comparison',
                              'Single nine-command transfer workload; separate from APK policy benchmark',
                              'CPU affinity selected; frequency, thermal and background load uncontrolled',
                              'BF compiler stages interpreted on Windows; no Android-native compiler or S2',
                              'Paired bootstrap and fastest-baseline reselection are exploratory']}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, rec in data.items(): print(f'{name}: {rec["median_ms"]:.4f} ms')
    print(f'{report["sample_status"]}: speed ratio {report["speed_ratio_baseline_over_bf"]:.4f}, interval {ci}')


if __name__ == '__main__':
    main()

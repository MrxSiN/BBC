#!/usr/bin/env python3
"""Interleave original/optimized BF against strengthened native baselines.

GM is measured separately under its unchanged bounded request ABI. Its policy
work is not equated to the byte-transfer workload and is not called BF parity.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap')]
import android_device
from android_device import DeviceRunner, BUILD, REMOTE, run
from run_android_optimized import compile_optimized_source, OPTIMIZERS
from local_seed import LocalSeedRunner


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gm', type=Path, default=Path(r'D:\Android\AndroidStudioProjects\GM'))
    args = parser.parse_args()
    device = DeviceRunner()
    device_info = {key: device.shell(f'getprop {prop}').stdout.decode().strip()
                   for key, prop in [('model', 'ro.product.model'),
                                     ('android', 'ro.build.version.release'), ('api', 'ro.build.version.sdk')]}
    device_info['page_bytes'] = int(device.shell('getconf PAGE_SIZE').stdout)
    device_info['benchmark_cpu'] = 8
    sdk = Path(os.environ['LOCALAPPDATA']) / 'Android/Sdk'
    ndk = max((p for p in (sdk / 'ndk').iterdir() if p.is_dir() and p.name[0].isdigit()),
              key=lambda p: tuple(int(x) for x in p.name.split('.')))
    clang = ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    objdump = clang.with_name('llvm-objdump.exe')
    rustc = Path.home() / '.cargo/bin/rustc.exe'
    builds = {}
    source = (ROOT / 'examples/android_loop_demo.bf').read_bytes()
    image = compile_optimized_source(source, stage_runner=LocalSeedRunner())
    path = BUILD / 'brainfuck_optimized'
    path.write_bytes(image)
    device.push(path, path.name)
    device.shell(f'chmod 700 {REMOTE}/{path.name}')
    builds[path.name] = {'bytes': len(image), 'sha256': digest(path)}

    for name, level in [('c_freestanding_o3', '-O3'), ('c_freestanding_oz', '-Oz'), ('c_direct_echo', '-O3')]:
        flags = [level, '-flto', '-fno-stack-protector', '-fno-unwind-tables',
                 '-fno-asynchronous-unwind-tables', '-nostdlib', '-static',
                 '-Wl,-e,_start,--gc-sections,--no-rosegment', '-s']
        if name == 'c_direct_echo':flags.append('-DDIRECT_ECHO')
        start = time.perf_counter_ns()
        run([clang, '--target=aarch64-linux-android26', *flags,
             ROOT / 'benchmarks/baselines/android_transfer_freestanding.c', '-o', BUILD / name])
        builds[name] = {'bytes': (BUILD / name).stat().st_size, 'sha256': digest(BUILD / name),
                        'flags': flags, 'compile_ms': (time.perf_counter_ns() - start) / 1e6}
        device.push(BUILD / name, name)
        device.shell(f'chmod 700 {REMOTE}/{name}')
        (BUILD / f'{name}.disassembly.txt').write_bytes(run([objdump, '-d', BUILD / name]).stdout)

    flags = ['-O', '-C', 'lto=fat', '-C', 'codegen-units=1', '-C', 'panic=abort',
             '-C', 'strip=symbols', '-C', f'linker={clang}',
             '-C', 'link-arg=--target=aarch64-linux-android26',
             '-C', 'link-arg=-nostdlib', '-C', 'link-arg=-static', '-C', 'link-arg=-Wl,-e,_start,--no-rosegment']
    for name in ('rust_freestanding', 'rust_direct_echo'):
        variant_flags = flags + (['--cfg', 'direct_echo'] if name == 'rust_direct_echo' else [])
        start = time.perf_counter_ns()
        run([rustc, '--target=aarch64-linux-android', *variant_flags,
             ROOT / 'benchmarks/baselines/android_transfer_freestanding.rs', '-o', BUILD / name])
        builds[name] = {'bytes': (BUILD / name).stat().st_size, 'sha256': digest(BUILD / name),
                        'flags': variant_flags, 'compile_ms': (time.perf_counter_ns() - start) / 1e6}
        device.push(BUILD / name, name)
        device.shell(f'chmod 700 {REMOTE}/{name}')
        (BUILD / f'{name}.disassembly.txt').write_bytes(run([objdump, '-d', BUILD / name]).stdout)

    original = json.loads((ROOT / 'benchmarks/results/android_transfer.json').read_text())
    old_dir = ROOT / 'build/android_benchmark'
    for name in ('brainfuck', 'c', 'c_static', 'rust', 'sample'):
        assert digest(old_dir / name) == original['builds'][name]['sha256'], name
    programs = {'brainfuck_original': '/data/local/tmp/brainfuck-bench/brainfuck',
                'brainfuck_optimized': f'{REMOTE}/brainfuck_optimized',
                'c_dynamic': '/data/local/tmp/brainfuck-bench/c',
                'c_static': '/data/local/tmp/brainfuck-bench/c_static',
                'rust_std': '/data/local/tmp/brainfuck-bench/rust',
                'c_freestanding_o3': f'{REMOTE}/c_freestanding_o3',
                'c_freestanding_oz': f'{REMOTE}/c_freestanding_oz',
                'c_direct_echo': f'{REMOTE}/c_direct_echo',
                'rust_freestanding': f'{REMOTE}/rust_freestanding',
                'rust_direct_echo': f'{REMOTE}/rust_direct_echo'}
    # Every byte and EOF checked against the original output contract on-device.
    for name in ('brainfuck_optimized', 'c_freestanding_o3', 'c_freestanding_oz', 'c_direct_echo', 'rust_freestanding', 'rust_direct_echo'):
        result = device.shell(f'for v in $(seq 0 255); do '
                              f'/data/local/tmp/brainfuck-bench/sample "$v" {programs[name]} || exit; done')
        assert len(result.stdout.splitlines()) == 256, name
        device.shell(f'/data/local/tmp/brainfuck-bench/sample -1 {programs[name]}')
    print('PASS 1542 optimized BF/C/Rust byte and EOF checks', flush=True)

    # Batch the randomized schedule on-device: avoid wireless/host pacing noise.
    rng = random.Random(20261012)
    commands = ['set -e']
    for _ in range(101):
        order = list(programs)
        rng.shuffle(order)
        for name in order:
            commands.append(f'printf "{name} "; taskset -c 8 '
                            f'/data/local/tmp/brainfuck-bench/sample 173 {programs[name]}')
    before = device.shell('dumpsys battery').stdout.decode()
    schedule = BUILD / 'schedule.sh'
    output_lines = []
    for start in range(1, len(commands), 64):
        block = ['set -e'] + commands[start:start + 64]
        schedule.write_bytes(('\n'.join(block) + '\n').encode())
        device.push(schedule, schedule.name)
        result = device.shell(f'sh {REMOTE}/{schedule.name}')
        output_lines.extend(result.stdout.decode().splitlines())
        (BUILD / 'raw_process_samples.txt').write_text('\n'.join(output_lines) + '\n')
        print(f'Completed {len(output_lines)} / {101 * len(programs)} process samples', flush=True)
    samples = {name: [] for name in programs}
    memory = {name: [] for name in programs}
    for line in output_lines:
        name, ns, rss = line.split()
        samples[name].append(int(ns) / 1e6)
        memory[name].append(int(rss))
    assert all(len(values) == 101 for values in samples.values())
    data = {name: {'raw_ms': values, 'median_ms': statistics.median(values),
                   'peak_rss_kib': max(memory[name])} for name, values in samples.items()}
    fastest = min((name for name in programs if not name.startswith('brainfuck')),
                  key=lambda name: data[name]['median_ms'])
    ratio = data[fastest]['median_ms'] / data['brainfuck_optimized']['median_ms']
    ratios = []
    baseline_names = [name for name in programs if not name.startswith('brainfuck')]
    for _ in range(10000):
        indexes = rng.choices(range(101), k=101)
        baseline = min(statistics.median(samples[name][i] for i in indexes) for name in baseline_names)
        bf = statistics.median(samples['brainfuck_optimized'][i] for i in indexes)
        ratios.append(baseline / bf)
    ratios.sort()
    ci = [ratios[250], ratios[9749]]
    print(f'BF speed / fastest ({fastest}): {ratio:.4f}x, interval {ci}', flush=True)

    # Compile GM's committed generated policies as a separately labelled baseline.
    gm = args.gm
    cpp = gm / 'app/src/main/cpp'
    flags = ['-O3', '-flto', '-I', str(cpp)]
    run([clang, '--target=aarch64-linux-android26', *flags,
         ROOT / 'benchmarks/gm_policy_sample.c', cpp / 'bf_engine.c',
         cpp / 'generated/bf_programs.generated.c', '-o', BUILD / 'gm_policy_sample'])
    device.push(BUILD / 'gm_policy_sample', 'gm_policy_sample')
    device.shell(f'chmod 700 {REMOTE}/gm_policy_sample')
    sys.path.insert(0, str(gm / 'tests/compiler'))
    import frames
    ids = {row['name']: row['id'] for row in json.loads((gm / 'brainfuck/programs.json').read_text())['programs']}
    cases = [('scope', ids['scope'], frames.scope('com.google.android.gm', 'com.google.android.gm'), 1),
             ('ad_row', ids['row'], frames.ad_row(['com.google.android.gm.ads.adteaser.BasicAdTeaserItemView']), 1),
             ('ordinary_row', ids['row'], frames.ad_row(['android.widget.FrameLayout', 'android.view.View']), 0)]
    gm_results = {}
    for name, program, payload, expected in cases:
        path = BUILD / f'gm_{name}.request'
        path.write_bytes(payload)
        device.push(path, path.name)
        observations = []
        for _ in range(11):
            output = device.shell(f'taskset -c 8 {REMOTE}/gm_policy_sample {program} {REMOTE}/{path.name}')
            sample = json.loads(output.stdout)
            response = bytes.fromhex(sample['output_hex'])
            op = frames.C['OP_SCOPE'] if program == ids['scope'] else frames.C['OP_AD_ROW']
            assert frames.parse(response, op, 1) == bytes([expected]), name
            assert sample['checksum'] == sum(response) * 20000
            observations.append(sample['ns_per_call'])
        gm_results[name] = {'raw_ns_per_call': observations, 'median_ns_per_call': statistics.median(observations),
                            'input_hex': payload.hex(), 'output_hex': response.hex()}
    gm_sources = {name: {'source_sha256': digest(gm / 'brainfuck/src' / f'{name}.bf'),
                         'commands': sum(c in b'><+-.,[]' for c in (gm / 'brainfuck/src' / f'{name}.bf').read_bytes())}
                  for name in ('row', 'scope')}
    report = {'date': time.strftime('%Y-%m-%d'), 'device': device_info,
              'objective': 'BF faster than the strongest measured native baseline on identical work',
              'status': 'MET_ON_BYTE_TRANSFER_ONLY' if ci[0] > 1 else 'NOT_PROVEN_FASTEST',
              'fastest_baseline': fastest, 'bf_speed_ratio': ratio, 'bootstrap_95_percent_interval': ci,
              'old_to_optimized_bf_time_ratio': data['brainfuck_original']['median_ms'] / data['brainfuck_optimized']['median_ms'],
              'rounds': 101, 'timing': 'on-device fresh process, randomized interleaving, excludes ADB, includes startup/I/O',
              'correctness_checks': 1542,
              'raw_process_samples_sha256': digest(BUILD / 'raw_process_samples.txt'),
              'builds': builds, 'data': data, 'battery_before': before,
              'optimizer_source_sha256': {name: digest(ROOT / source) for name, (source, _) in OPTIMIZERS.items()},
              'compiler_source_sha256': digest(ROOT / 'compiler/core.bf'),
              'baseline_source_sha256': {name: digest(ROOT / 'benchmarks/baselines' / name)
                                         for name in ['android_transfer_freestanding.c', 'android_transfer_freestanding.rs']},
              'toolchains': {'clang': run([clang, '--version']).stdout.decode().splitlines()[0],
                             'rustc': run([rustc, '--version']).stdout.decode().strip()},
              'bootstrap_method': 'Paired round resampling; fastest baseline reselected per resample',
              'transport_retries': android_device.TRANSPORT_RETRIES,
              'battery_after': device.shell('dumpsys battery').stdout.decode(),
              'gm': {'path': str(gm), 'classification': 'Separate warmed C AOT policy baseline, not a BF-native parity result',
                     'sources': gm_sources, 'generated_c_sha256': digest(cpp / 'generated/bf_programs.generated.c'),
                     'sample_sha256': digest(BUILD / 'gm_policy_sample'), 'flags': flags,
                     'warmup_calls': 20000, 'calls_per_sample': 20000, 'samples': 11, 'cases': gm_results},
              'limitations': ['Only ten-command native BF source; full GM policies cannot compile here',
                              'No steady-state Java/JVM ranking or full APK benchmark',
                              'Compiler stages run under independent BF interpreters; no Android native selfhosting',
                              'No frequency locking; benchmark CPU/background/thermal effects remain',
                              'Baseline selection and bootstrap interval are exploratory, not universal proof']}
    (ROOT / 'benchmarks/results/android_optimized.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, row in data.items():
        print(f"{name}: {row['median_ms']:.4f} ms")
    for name, row in gm_results.items():
        print(f"GM {name}: {row['median_ns_per_call']:.1f} ns per warmed policy call")
    print(report['status'])
    return report


if __name__ == '__main__':
    main()

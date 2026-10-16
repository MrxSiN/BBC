#!/usr/bin/env python3
"""Measure BF-owned compact native output against native baselines and warmed ART."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'bootstrap'), str(ROOT/'benchmarks')]
from run_android_native import NativeAndroidCompiler
import run_android_native
from android_device_followup import interval


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()): parser.error('output must be absent or empty')
    out.mkdir(parents=True, exist_ok=True)
    adb = [args.adb, '-s', args.serial]
    remote = '/data/local/tmp/bfc_compact_benchmark'
    def run(command): return run_android_native.run_checked(command)
    def shell(command): return run(adb + ['shell', '-T', command]).stdout.decode().strip()
    def push(path, name=None):
        name = name or path.name; run(adb + ['push', path, remote+'/'+name])
        assert shell(f'sha256sum {remote}/{name}').split()[0] == sha(path)
        shell(f'chmod 700 {remote}/{name}')
    shell('mkdir -p ' + remote)
    compiler = NativeAndroidCompiler(args.serial, out/'pipeline', args.adb)
    transfer = b',[>+<-]>.'; stream_source = b',[.,]'
    for name, source, compact in [('bf_compact', transfer, True), ('bf_generic', transfer, False),
                                   ('bf_stream', stream_source, True)]:
        (out / name).write_bytes(compiler.compile(source, compact)); push(out / name)
    old = ROOT/'evidence/android_followup_20261013/native'
    previous = json.loads((old/'report.json').read_text())
    for name in ('brainfuck', 'sample', 'c_freestanding_o3', 'c_freestanding_oz', 'c_direct_echo', 'rust_direct_echo'):
        assert sha(old/name) == previous['builds'][name]['sha256']
        push(old/name, 'bf_old' if name == 'brainfuck' else name)
    # Exact source matching is BF-owned. The near miss must retain its generic ELF.
    checks = []
    for index, source in enumerate([b',[->+<]>.', b', [>+<-] > . ignored\x00\xff', b'+.',
                                    b',[>+<-]>.+', b'[[]]']):
        generic = compiler.compile(source, False); compact = compiler.compile(source, True)
        expected_size = 232 if index in (0, 1) else len(generic)
        assert len(compact) == expected_size
        if index > 1: assert compact == generic
        checks.append({'source_hex': source.hex(), 'generic_bytes': len(generic), 'optimized_bytes': len(compact),
                       'optimized_sha256': hashlib.sha256(compact).hexdigest()})
    for name in ('bf_compact', 'bf_generic'):
        lines = shell(f'set -e; for v in $(seq 0 255) -1; do {remote}/sample "$v" {remote}/{name}; done').splitlines()
        assert len(lines) == 257
    faults = {}
    for label, command, expected in [('read', f'{remote}/bf_compact <&- > /dev/null', 4),
                                     ('write', f'printf A | {remote}/bf_compact 1< /dev/null', 3)]:
        actual = int(shell(command + '; echo $?')); assert actual == expected; faults[label] = actual
    sdk = Path(os.environ['LOCALAPPDATA'])/'Android/Sdk'
    latest = lambda folder: max((p for p in folder.iterdir() if p.is_dir() and p.name[0].isdigit()),
                                key=lambda p: tuple(int(x) for x in p.name.split('.')))
    clang = latest(sdk/'ndk')/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    rustc = Path.home()/'.cargo/bin/rustc.exe'
    builds = {}
    for name, source, flags in [('stream_sample', ROOT/'benchmarks/android_stream_sample.c', ['-O2']),
                                ('c_stream_o3', ROOT/'benchmarks/baselines/android_stream_freestanding.c', ['-O3']),
                                ('c_stream_oz', ROOT/'benchmarks/baselines/android_stream_freestanding.c', ['-Oz'])]:
        if name != 'stream_sample': flags += ['-flto', '-fno-stack-protector', '-fno-unwind-tables',
                                              '-fno-asynchronous-unwind-tables', '-nostdlib', '-static',
                                              '-Wl,-e,_start,--gc-sections,--no-rosegment', '-s']
        command = [clang, '--target=aarch64-linux-android26', *flags, source, '-o', out/name]
        run(command); push(out/name)
        builds[name] = {'sha256': sha(out/name), 'bytes': (out/name).stat().st_size,
                        'source_sha256': sha(source), 'command': [str(x) for x in command]}
    source = ROOT/'benchmarks/baselines/android_stream_freestanding.rs'
    command = [rustc, '-O', '--target=aarch64-linux-android', '-C', f'linker={clang}',
               '-C', 'link-arg=--target=aarch64-linux-android26', '-C', 'lto=fat', '-C', 'codegen-units=1',
               '-C', 'panic=abort', '-C', 'strip=symbols', '-C', 'link-arg=-nostdlib', '-C', 'link-arg=-static',
               '-C', 'link-arg=-Wl,-e,_start,--no-rosegment', source, '-o', out/'rust_stream']
    run(command); push(out/'rust_stream')
    builds['rust_stream'] = {'sha256': sha(out/'rust_stream'), 'bytes': (out/'rust_stream').stat().st_size,
                            'source_sha256': sha(source), 'command': [str(x) for x in command]}
    jbr = Path(r'C:\Program Files\Android\Android Studio\jbr')
    source = ROOT/'benchmarks/baselines/AndroidStreamEcho.java'
    run([jbr/'bin/javac.exe', '--release', '8', '-d', out, source])
    run([jbr/'bin/java.exe', '-cp', latest(sdk/'build-tools')/'lib/d8.jar', 'com.android.tools.r8.D8',
         '--release', '--min-api', '26', '--output', out, out/'AndroidStreamEcho.class'])
    push(out/'classes.dex')
    builds['java_dex'] = {'sha256': sha(out/'classes.dex'), 'bytes': (out/'classes.dex').stat().st_size,
                         'source_sha256': sha(source)}
    props = {k: shell('getprop '+k) for k in ('ro.product.model','ro.build.version.release','ro.build.version.sdk','ro.build.fingerprint')}
    cpu = previous['cpu']; before = shell('dumpsys battery')
    fresh = {n: f'{remote}/{n}' for n in ('bf_compact','bf_generic','bf_old','c_freestanding_o3',
                                        'c_freestanding_oz','c_direct_echo','rust_direct_echo')}
    steady = {n: f'{remote}/{n}' for n in ('bf_stream','c_stream_o3','c_stream_oz','rust_stream')}
    steady.update(java_art_warmed=f'dalvikvm -Xusejit:true -cp {remote}/classes.dex AndroidStreamEcho',
                  java_art_interpreted=f'dalvikvm -Xint -cp {remote}/classes.dex AndroidStreamEcho')
    records = {}
    for name, command in steady.items():
        # EOF, zero termination and every nonzero byte must preserve exact output.
        for case, data in [('eof',b''), ('zero',b'\0\xff'), ('all',bytes(range(1,256))+b'\0\xff')]:
            p = out/'input.stdin'; p.write_bytes(data); push(p)
            shell(f'{command} < {remote}/input.stdin > {remote}/check.stdout')
            p = out/'check.stdout'; run(adb+['pull', remote+'/check.stdout',p])
            assert p.read_bytes() == (bytes(range(1,256)) if case=='all' else b'')
        # This timer must reject a non-responder before timings are accepted.
    bad = subprocess.run(adb+['shell','-T',f'{remote}/stream_sample /system/bin/true'],capture_output=True,timeout=30)
    assert bad.returncode != 0
    rng = random.Random(2026101302)
    for label, programs, rounds, timer, bf in [('fresh',fresh,101,'sample 173','bf_compact'),
                                              ('steady',steady,31,'stream_sample','bf_stream')]:
        values = {n: [] for n in programs}; raw = []
        for round_index in range(rounds):
            order = list(programs); rng.shuffle(order)
            for name in order:
                lines = shell(f'taskset -c {cpu} {remote}/{timer} {programs[name]}').splitlines()
                if label == 'fresh':
                    assert len(lines)==1
                    ns, rss = map(int,lines[0].split()); assert ns>0 and rss>0
                    values[name].append(ns/1e6); raw.append(f'{round_index} {name} {ns} {rss}')
                else:
                    assert len(lines)==64
                    ns = [int(x) for x in lines]; assert all(x>0 for x in ns)
                    values[name].append(statistics.median(ns)/256)
                    raw.extend(f'{round_index} {name} {i} {x}' for i,x in enumerate(ns))
            (out/(label+'.raw.txt')).write_text('\n'.join(raw)+'\n')
            if (round_index+1)%10==0: print(f'{label}: {round_index+1}/{rounds} rounds',flush=True)
        baselines = [n for n in programs if not n.startswith('bf_')]
        best = min(baselines,key=lambda n: statistics.median(values[n])); ci=interval(values,bf,baselines,rng)
        records[label]={'rounds':rounds,'units':'ms/process' if label=='fresh' else 'ns/request',
                        'data':{n:{'median':statistics.median(v),'raw':v} for n,v in values.items()},
                        'fastest_baseline':best,'speed_ratio_baseline_over_bf':statistics.median(values[best])/statistics.median(values[bf]),
                        'paired_bootstrap_95_percent_interval':ci,
                        'status':'BF_FASTER_ON_THIS_WORKLOAD' if ci[0]>1 else 'NOT_PROVEN_FASTEST'}
        print(label,records[label]['status'],records[label]['speed_ratio_baseline_over_bf'],ci,flush=True)
    report={'date':datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
            'classification':'MEASURED BF-owned native Android backend; no BF-to-C/JNI',
            'device':props,'cpu':cpu,'fresh':records['fresh'],'steady':records['steady'],
            'native_compiler_source_sha256':sha(ROOT/'compiler/android_core.bf'),
            'optimizer_source_sha256':sha(ROOT/'experiments/android_compact_optimize.bf'),
            'builds':builds,'bf_images':{n:{'bytes':(out/n).stat().st_size,'sha256':sha(out/n)} for n in ('bf_compact','bf_generic','bf_stream')},
            'optimization_cases':checks,'byte_eof_checks':514,'runtime_fault_statuses':faults,
            'stream_contract_cases':18,'steady_warmup_requests_per_process':16384,'steady_timed_requests_per_process':16384,
            'battery_before':before,'battery_after':shell('dumpsys battery'),'harness_sha256':sha(Path(__file__)),
            'general_performance_objective':'NOT_ESTABLISHED',
            'adb_transport_retries':run_android_native.TRANSPORT_RETRIES,
            'limitations':['One Pixel 8 Pro/API37; uncontrolled frequency/background/thermal state',
                           'Fresh timer includes process start and excludes ADB; steady timer excludes startup/warmup',
                           'Steady timer includes byte syscalls and parent/child pipe scheduling, not computation alone',
                           'ART JIT enabled plus warmup does not prove method-level JIT compilation; no HotSpot JVM',
                           'Only exact small proven patterns are compacted; generic compiler retains 64-byte slots',
                           'C/Rust steady baselines are freestanding O3/Oz/LTO; Java uses unbuffered FileInput/OutputStream',
                           'Single-session paired bootstrap is exploratory, not universal language superiority']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()

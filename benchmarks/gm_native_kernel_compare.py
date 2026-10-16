"""Profile the BF-native GM kernels against the original optimized C test oracle."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--native-build', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--gm', type=Path, default=Path(r'D:\Android\AndroidStudioProjects\GM'))
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()): parser.error('preserve earlier evidence; use an empty output')
    out.mkdir(parents=True, exist_ok=True)
    adb = [r'D:\Android\platform-tools\adb.exe', '-s', args.serial]
    remote = '/data/local/tmp/bfc_gm_kernel_20261014'
    def run(command): return subprocess.run([str(x) for x in command], capture_output=True, check=True, timeout=90)
    def shell(command): return run(adb + ['shell','-T',command]).stdout.decode().strip()
    def push(path):
        run(adb + ['push',path,remote+'/'+path.name])
        assert shell('sha256sum '+remote+'/'+path.name).split()[0] == sha(path)
    clang = Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    cpp = args.gm/'app/src/main/cpp'
    sources = [ROOT/'benchmarks/policy_native_sample.c',cpp/'bf_engine.c',cpp/'generated/bf_programs.generated.c']
    command = [clang,'--target=aarch64-linux-android26','-O3','-flto','-I',cpp,'-I',cpp/'generated',
               *sources,'-o',out/'sample']
    run(command); shell('mkdir -p '+remote); push(out/'sample'); shell('chmod 700 '+remote+'/sample')
    build = json.loads((args.native_build/'build.json').read_text())
    for name in ('row','scope'):
        path = args.native_build/(name+'.elf')
        assert sha(path) == build['sources'][name]['elf_sha256']
        push(path)
    letters = '.comglearndistwATIV'
    codes = dict(zip(letters, (1,2,3,4,5,6,7,8,11,9,10,12,13,14,15,16,17,18,19), strict=True))
    assert [codes[c] for c in 'rnd'] == [11,9,10]
    def name(value):
        assert len(value) < 256
        return bytes([len(value)])+bytes(codes.get(c,0) for c in value)+b'\0'
    cases = [('row_ad',0,b'\1'+name('com.google.android.gm.ads.adteaser.BasicAdTeaserItemView')),
             ('row_miss',0,b'\1'+name('java.util.concurrent.ConcurrentHashMap')),
             ('scope_yes',1,b'\1'+name('com.google.android.gm')+b'\1'+name('com.google.android.gm'))]
    checks = {}; programs = {}; fuzz_checks = {}
    for label, program, payload in cases:
        wire = bytes([1,0,16 if program==0 else 32,0,len(payload),0,52,18])+payload
        path = out/(label+'.stdin'); path.write_bytes(wire); push(path)
        call = f'{remote}/sample {program} {remote}/{"row" if program==0 else "scope"}.elf {remote}/{path.name}'
        checked = shell(call+' check'); checks[label] = json.loads(checked)
        expected = bytes([1,0,(16 if program==0 else 32)|128,0,1,0,52,18,label!='row_miss'])
        assert checks[label]['status'] == 0 and checks[label]['output_hex'] == expected.hex(), label
        programs[label] = call
    for label in ('row_ad','scope_yes'):
        fuzz_checks[label] = json.loads(shell(programs[label]+' fuzz'))
        assert fuzz_checks[label]['random_frame_checks'] == 4096
    samples = {label: {'bf': [],'c': []} for label in programs}
    rng = random.Random(20261014); raw = []
    before = shell('dumpsys battery')
    for round_index in range(31):
        order = [(label,variant) for label in programs for variant in ('bf','c')]; rng.shuffle(order)
        for label, variant in order:
            line = shell(f'taskset -c 8 {programs[label]} {variant}')
            row = json.loads(line)
            assert row['variant'] == variant and row['ns_per_call'] > 0
            samples[label][variant].append(row['ns_per_call']); raw.append(f'{round_index} {label} {line}')
        (out/'samples.txt').write_text('\n'.join(raw)+'\n')
    report = {'date':datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
              'classification':'ANDROID_DEVICE_EXECUTED_DIRECT_KERNEL_BF_VS_C_BASELINE',
              'rounds':31,'warmup_calls_per_sample':20000,'timed_calls_per_sample':20000,
              'checks':checks,'random_frame_checks':fuzz_checks,'samples':samples,
              'medians_ns':{label:{variant:statistics.median(values) for variant,values in variants.items()}
                            for label,variants in samples.items()},
              'sample_build_command':[str(x) for x in command],
              'sample_sha256':sha(out/'sample'),'sources':{str(p):sha(p) for p in sources},
              'bf_policies':build['sources'],'cpu':8,'battery_before':before,'battery_after':shell('dumpsys battery'),
              'limitations':['C is a disclosed comparison oracle only; it is not linked into the native GM APK',
                             'Three fixed timed frames; randomized byte/status checks are a bounded corpus, not a proof',
                             'Includes tape initialization and output checksum; excludes Java, JNI and process startup',
                             'Kernel and APK timings are separate sessions; no subtraction to claim exact JNI cost',
                             'Uncontrolled frequency, thermal and background load; no GM Rust or JVM kernel baseline']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['medians_ns'],indent=2),flush=True)


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Install the isolated existing GM benchmark APK and preserve ART test evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import statistics
import subprocess
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'io.github.mrxsin.gmailhideads.codexbench'
TEST_PACKAGE = PACKAGE + '.test'
CLASS = 'my.MrxSiN.gmailhideads.policy.'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(log):
    rows = {}
    for name, p50, p95, p99 in re.findall(r'([^\n]*?)\s+p50\s+([\d.]+)\s+p95\s+([\d.]+)\s+p99\s+([\d.]+)\s+us', log):
        # logcat's time/PID/tag prefix precedes the policy case name.
        for case in ('legacy ordinary class', 'brainfuck ordinary class', 'legacy derived ad row',
                     'brainfuck derived ad row', 'legacy scope', 'brainfuck scope',
                     'cached verdict (the addView path)'):
            if name.endswith(case):
                rows[case] = {'p50_us': float(p50), 'p95_us': float(p95), 'p99_us': float(p99)}
    if len(rows) != 7:
        raise ValueError(f'expected 7 fresh benchmark rows, found {len(rows)}')
    return rows


def main():
    global PACKAGE, TEST_PACKAGE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--serial', required=True)
    parser.add_argument('--gm', type=Path, default=Path(r'D:\Android\AndroidStudioProjects\GM'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native-build', type=Path, help='Direct BF-native build from tools/build_gm_native.py')
    args = parser.parse_args()
    build = None
    if args.native_build:
        build = json.loads((args.native_build / 'build.json').read_text())
        PACKAGE = 'io.github.mrxsin.gmailhideads.nativebf'
        TEST_PACKAGE = PACKAGE + '.test'
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output must be absent or empty; preserve earlier evidence')
    out.mkdir(parents=True, exist_ok=True)
    adb = [args.adb, '-s', args.serial]

    def run(command, name):
        result = subprocess.run([str(x) for x in command], capture_output=True, timeout=180)
        (out / (name + '.stdout')).write_bytes(result.stdout)
        (out / (name + '.stderr')).write_bytes(result.stderr)
        result.check_returncode()
        return result.stdout.decode(errors='replace')

    apks = {'app.apk': args.gm / 'app/build/outputs/apk/release/GmailHideAds-v2.1.0.apk',
            'test.apk': args.gm / 'app/build/outputs/apk/androidTest/release/app-release-androidTest.apk'}
    if build:
        apks = {name: args.native_build / name for name in apks}
        assert digest(apks['app.apk']) == build['apk_sha256']
        assert digest(apks['test.apk']) == build['test_apk_sha256']
    for name, source in apks.items():
        shutil.copyfile(source, out / name)
        assert 'Success' in run(adb + ['install', '-r', out / name], name + '.install')
    modes = {}
    for mode in ('verify', 'speed'):
        for package in (PACKAGE, TEST_PACKAGE):
            if mode == 'verify':
                run(adb + ['shell', 'cmd', 'package', 'compile', '--reset', package], mode + '.' + package + '.reset')
            compiled = run(adb + ['shell', 'cmd', 'package', 'compile', '-m', mode, '-f', package],
                           mode + '.' + package + '.compile')
            assert 'Success' in compiled
        results = []
        for repeat in range(3):
            label = f'{mode}.{repeat}'
            run(adb + ['shell', 'am', 'force-stop', PACKAGE], label + '.force-stop')
            start = int(run(adb + ['shell', 'date', '+%s'], label + '.start').strip())
            classes = CLASS + 'PolicyBenchmarkTest'
            if mode == 'verify' and repeat == 0:
                classes += ',' + CLASS + 'PolicyParityTest,' + CLASS + 'PolicyRobustnessTest'
            instrument = run(adb + ['shell', 'am', 'instrument', '-w', '-r', '-e', 'class', classes,
                                    TEST_PACKAGE + '/androidx.test.runner.AndroidJUnitRunner'], label + '.instrument')
            passed = re.search(r'OK \((\d+) tests?\)', instrument)
            assert passed and int(passed[1]) == (16 if mode == 'verify' and repeat == 0 else 1), instrument
            log = run(adb + ['logcat', '-d', '-v', 'epoch', '-s', 'System.out:I'], label + '.logcat')
            fresh = '\n'.join(line for line in log.splitlines()
                              if re.match(r'^\s*\d+\.\d+', line) and float(line.split()[0]) >= start)
            (out / (label + '.benchmark.txt')).write_text(fresh + '\n')
            rows = parse(fresh)
            results.append({'tests_passed': int(passed[1]), 'rows': rows})
            print(f'{label}: {passed[1]} tests passed; BF/Java ordinary p50 '
                  f'{rows["brainfuck ordinary class"]["p50_us"]}/{rows["legacy ordinary class"]["p50_us"]} us', flush=True)
        modes[mode] = {'runs': results, 'median_p50_us': {
            case: statistics.median(rec['rows'][case]['p50_us'] for rec in results) for case in results[0]['rows']}}
        run(adb + ['shell', 'dumpsys', 'package', PACKAGE], mode + '.package')
    report = {'date': datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
              'serial': args.serial, 'package': PACKAGE, 'test_package': TEST_PACKAGE,
              'classification': ('ANDROID_DEVICE_EXECUTED direct BF-owned native GM policies' if build else
                                 'ANDROID_DEVICE_EXECUTED existing GM BF-to-C AOT plus JNI; separate from BrainfuckCC backend'),
              'build_command': build['build_command'] if build else 'gradlew.bat -I D:/GitHub/BrainfuckCC/benchmarks/gm_benchmark.init.gradle -PbenchmarkRelease :app:assembleRelease :app:assembleReleaseAndroidTest --console=plain',
              'apk_sha256': {name: digest(out / name) for name in apks}, 'art_modes': modes,
              'instrumentation_tests_passed': 21, 'warmup_calls_per_case': 20000, 'timed_calls_per_case': 20000,
              'native_build': build,
              'source_sha256': build['sources'] if build else {str(p.relative_to(args.gm)): digest(p) for p in (
                  args.gm / 'app/src/main/cpp/generated/bf_programs.generated.c',
                  args.gm / 'app/src/main/cpp/bf_engine.c', args.gm / 'app/src/main/cpp/bf_jni.c',
                  args.gm / 'app/src/test/java/my/MrxSiN/gmailhideads/policy/PolicyBenchmarkTest.java')},
              'logs_sha256': {p.name: digest(p) for p in out.iterdir() if p.suffix in ('.stdout', '.stderr', '.txt')},
              'harness_sha256': digest(Path(__file__)),
              'limitations': ['verify mode plus warmup permits JIT but does not prove method-level JIT compilation',
                              'speed mode explicitly requests ART AOT for both packages',
                              'Three process runs per mode; fixed inputs and case order; uncontrolled frequency/thermals',
                              'Per-call timer, volatile sink, encoding, JNI and validation are included',
                              'Cached verdict performs no new BF execution',
                              ('New JNI bridge embeds BF-produced callable bytes; NDK only builds the platform library' if build else
                               'Existing GM compiler emits C; this run is a baseline using that backend'),
                              'No same-device HotSpot JVM, no actual Gmail/Xposed hook execution']}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()

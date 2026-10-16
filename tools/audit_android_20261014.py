"""Audit persisted device outputs; do not synthesize device execution."""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT / 'tools')]
import audit_android_native_selfhost_evidence as selfhost
from source_check import check_source


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    selfhost.BASE = ROOT / 'evidence/android_native_selfhost_20261014_v2'
    native = selfhost.audit()
    device_dir = ROOT / 'evidence/gm_native_device_20261014_v4'
    device = json.loads((device_dir / 'report.json').read_text())
    build_dir = ROOT / 'evidence/gm_native_20261014_v4'
    build = json.loads((build_dir / 'build.json').read_text())
    assert device['native_build'] == build
    assert not build['old_bf_to_c_backend_linked'] and build['compiler_stages_android_native']
    for name, info in build['sources'].items():
        source = build_dir / 'GM/brainfuck/src' / (name + '.bf')
        assert sha(source) == info['source_sha256']
        assert sha(build_dir / (name + '.elf')) == info['elf_sha256']
    for name, info in build['stages'].items():
        source = ROOT / 'experiments' / (name + '.bf')
        assert sha(source) == info['source_sha256'] and len(check_source(source.read_bytes())) <= 16128
        assert sha(build_dir / 'pipeline' / (name + '.elf')) == info['android_native_elf_sha256']
    for name, key in [('app.apk','apk_sha256'),('test.apk','test_apk_sha256')]:
        assert sha(build_dir / name) == build[key] == sha(device_dir / name)
    with zipfile.ZipFile(build_dir / 'app.apk') as archive:
        library = archive.read('lib/arm64-v8a/libgmailbf.so')
        assert hashlib.sha256(library).hexdigest() == build['native_library_sha256']
        assert all((build_dir / (name + '.elf')).read_bytes() in library for name in build['sources'])
    tests = 0
    for mode in ('verify','speed'):
        for i in range(3):
            text = (device_dir / f'{mode}.{i}.instrument.stdout').read_text()
            match = re.search(r'OK \((\d+) tests?\)', text)
            assert match and 'FAILURES!!!' not in text
            tests += int(match[1])
    assert tests == device['instrumentation_tests_passed'] == 21
    parity = re.search(r'PolicyParityTest: (\d+) old-vs-new comparisons',
                       (device_dir / 'verify.0.benchmark.txt').read_text())
    assert parity and int(parity[1]) == 634229
    bundle = ROOT / 'evidence/android53_device_20261014'
    fixtures = json.loads((bundle / 'manifest.json').read_text())['fixtures']
    assert (bundle / 'results.txt').read_text().splitlines() == [
        f"PASS {r['name']} status={r['expected_exit_code']}" for r in fixtures]
    for r in fixtures:
        assert sha(bundle / r['native_elf']) == r['elf_sha256']
        assert (bundle / (r['name'] + '.got')).read_bytes() == (bundle / r['expected_stdout_file']).read_bytes()
        assert (bundle / (r['name'] + '.stderr')).read_bytes() == b''
    benchmark = json.loads((ROOT / 'evidence/android_compact_benchmark_20261014/report.json').read_text())
    for kind, rounds in [('fresh',101),('steady',31)]:
        assert benchmark[kind]['rounds'] == rounds
        assert all(len(row['raw']) == rounds for row in benchmark[kind]['data'].values())
    kernel_path = ROOT / 'evidence/gm_native_kernel_20261014_v3/report.json'
    kernel = json.loads(kernel_path.read_text())
    assert sum(r['random_frame_checks'] for r in kernel['random_frame_checks'].values()) == 8192
    for label, expected in [('row_ad','010090000100341201'),('row_miss','010090000100341200'),
                            ('scope_yes','0100a0000100341201')]:
        assert kernel['checks'][label]['status'] == 0 and kernel['checks'][label]['output_hex'] == expected
        assert all(len(values) == 31 for values in kernel['samples'][label].values())
    return {'date':'2026-10-14', 'classification':'PERSISTED_ANDROID_DEVICE_RESULTS_AUDITED',
            'device':device['serial'], 'native_selfhost_stages_identical':native['native_compiler_stages_checked'],
            'native_selfhost_programs':native['native_program_output_cases_checked'],
            'native_selfhost_rejections':native['malformed_source_records_checked'],
            'dynamic_elf_device_cases':len(fixtures), 'gm_instrumentation_tests':tests,
            'gm_parity_comparisons':int(parity[1]), 'bf_native_gm_policies':build['sources'],
            'gm_native_stage_count':len(build['stages']),
            'gm_kernel_random_frame_checks':8192, 'gm_kernel_medians_ns':kernel['medians_ns'],
            'gm_art_speed_median_us':device['art_modes']['speed']['median_p50_us'],
            'fresh_native_status':benchmark['fresh']['status'], 'steady_native_status':benchmark['steady']['status'],
            'performance_target':'NOT_ACHIEVED', 'actual_gmail_xposed_hooks_tested':False,
            'evidence_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in (
                selfhost.BASE / 'report.json',device_dir / 'report.json',build_dir / 'build.json',
                ROOT / 'evidence/android_compact_benchmark_20261014/report.json',kernel_path,bundle / 'results.txt')}}


if __name__ == '__main__':
    result = audit()
    (ROOT / 'evidence/android_execution_20261014.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

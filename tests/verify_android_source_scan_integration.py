#!/usr/bin/env python3
"""Check opt-in BF source scanner against the historical ten-slot Android BF pipeline."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from run_android_loops import compile_source


def main():
    sources = (
        b'', b'+.', b'+++.', b'[]', b'[[]]', b'++[>+<-]>.',
        b'noise\0\xff ++[--]', b'\xff\x00+', b'++[-].',
    )
    matches = []
    for source in sources:
        image_old = compile_source(source, source_filter='filter')
        image_new = compile_source(source, source_filter='scan')
        assert image_old == image_new
        matches.append({'source_sha256': hashlib.sha256(source).hexdigest(),
                        'aarch64_image_sha256': hashlib.sha256(image_new).hexdigest()})

    rejection_cases = (b'[', b']', b'+' * 11, b'[]' * 6)
    for source in rejection_cases:
        for which in ('filter', 'scan'):
            try:
                compile_source(source, source_filter=which)
            except ValueError:
                pass
            else:
                raise AssertionError(('legacy Android back end incorrectly accepted', source, which))

    with tempfile.TemporaryDirectory(prefix='bf-android-scan-cli-') as td:
        src = Path(td) / 'input.bf'
        target = Path(td) / 'out.elf'
        target.write_bytes(b'preserve-existing')
        src.write_bytes(b'[')
        cmd = [sys.executable, str(ROOT / 'bootstrap/run_android_loops.py'),
               str(src), str(target), '--scanner']
        p = subprocess.run(cmd, capture_output=True, timeout=35)
        assert p.returncode and target.read_bytes() == b'preserve-existing'
        src.write_bytes(b'+++.')
        p = subprocess.run(cmd, capture_output=True, timeout=35)
        assert p.returncode == 0 and target.read_bytes() == compile_source(b'+++.', source_filter='filter')

    report = {'date': '2026-10-13', 'iteration': 27,
              'classification': 'EXECUTED_LINUX_HOSTED_OPT_IN_SCANNER_PARITY_NOT_GENERAL_ANDROID_CODEGEN',
              'stage_source': 'experiments/android_source_scan.bf',
              'pipeline': 'bootstrap/run_android_loops.py --scanner',
              'identical_fixed_size_aarch64_images': len(matches),
              'identical_rejection_cases': len(rejection_cases),
              'atomic_cli_preservation': True,
              'legacy_output_source_ceiling': 10,
              'device_execution': 'NOT_RERUN',
              'self_hosting_android': 'NOT_IMPLEMENTED',
              'matches': matches}
    (ROOT / 'evidence/iteration27_scan_integration.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS',len(matches),'native AArch64 image parity cases,',len(rejection_cases),
          'rejected source cases and atomic scanner CLI')


if __name__ == '__main__':
    main()

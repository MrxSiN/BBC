#!/usr/bin/env python3
"""Offline integrity tests for Android acceptance transport, NOT device execution."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
from android_device_acceptance import prepare, audit, inspect_elf, digest, expected_behavior, fixtures
from verify_android_aarch64_subset import emulate


def main():
    with tempfile.TemporaryDirectory(prefix='bf_android_acceptance_') as td:
        p = Path(td)
        bundle = p / 'bundle'; results = p / 'results'; results.mkdir()
        manifest = prepare(bundle)
        assert manifest['device_execution_claim'] is False
        assert manifest['evidence_class'] == 'PREPARED_NOT_EXECUTED'
        assert len(manifest['cases']) == 13
        cases = {name: (program, stdin) for name, program, stdin in fixtures()}
        shells = (bundle / 'run.sh').read_text()
        sims = 0
        for rec in manifest['cases']:
            name = rec['id']
            source, data = cases[name]
            elf = (bundle / (name + '.elf')).read_bytes()
            assert digest(elf) == rec['elf_sha256']
            assert digest(data) == rec['stdin_sha256']
            assert digest(source) == rec['source_sha256']
            assert inspect_elf(elf, len(source))['rw_offset'] == rec['rw_offset']
            assert (bundle / (name + '.stdin')).read_bytes() == data
            assert name + '.stdout' in shells and name + '.stderr' in shells and name + '.exitcode' in shells
            expected, status = expected_behavior(source, data)
            assert rec['expected_stdout_hex'] == expected.hex()
            assert rec['expected_exit_code'] == status
            # Device script results are not available here. Synthetic files
            # test the auditor, and must NEVER be recorded as a device run.
            (results / (name + '.stdout')).write_bytes(expected)
            (results / (name + '.stderr')).write_bytes(b'')
            (results / (name + '.exitcode')).write_text(str(status) + '\n')
            if name != 'right_trap':
                for base in (0, 0x40000000):
                    output, code, _ = emulate(elf, base,
                        tape_base_rva=rec['rw_offset'] + 0x60,
                        code_limit=rec['rx_bytes'], input_bytes=data,
                        max_steps=400_000)
                    assert (output, code) == (expected, status), (name, base, code, output)
                    sims += 1
        ok = audit(manifest, results)
        assert ok['all_passed'] and ok['passed'] == 13
        # Binary stdout must be compared byte-for-byte, including embedded NUL.
        (results / 'binary_echo.stdout').write_bytes(b'\0\xff')
        failed = audit(manifest, results)
        assert not failed['all_passed'] and failed['passed'] == 12
        (results / 'binary_echo.stdout').write_bytes(bytes([0, 255, 127]))
        (results / 'left_trap.exitcode').write_text('126\n')
        failed = audit(manifest, results)
        assert not failed['all_passed'] and failed['passed'] == 12
        (results / 'left_trap.exitcode').unlink()
        failed = audit(manifest, results)
        assert not failed['all_passed'] and failed['passed'] == 12
        # Verify no tool reports device success without a configured adb.
        probe = subprocess.run([sys.executable, str(ROOT / 'tools/android_device_acceptance.py'),
                                'run-device', str(bundle), str(p / 'no-device'),
                                '--adb', 'nonexistent-adb-iteration37'],
                               text=True, capture_output=True, timeout=30)
        assert probe.returncode == 2 and 'adb unavailable' in probe.stderr
        assert not (p / 'no-device').exists()
        # A one-byte ELF mutation must be rejected before any device dispatch.
        mut = bytearray((bundle / 'loop_2000.elf').read_bytes())
        mut[0x200] ^= 1
        try:inspect_elf(bytes(mut), 2000)
        except ValueError:pass
        else:raise AssertionError('invalid startup instruction accepted')
        counts = {r['command_count'] for r in manifest['cases']}
        assert {0,331,672,1013,1355,1696,2000}.issubset(counts)
        summary={'prepared_fixtures':len(manifest['cases']),
                 'simulator_runs':sims,
                 'size_class_boundaries_covered': 6,
                 'expected_traps':2,
                 'binary_stdout_including_nul': True,
                 'synthetic_audit_success_and_failures_tested': True,
                 'no_adb_refusal_verified': True,
                 'android_device_execution':'NOT_RUN',
                 'native_android_selfhosting':'NOT_RUN'}
        print('ITERATION 37 DEVICE ACCEPTANCE OFFLINE PASS', json.dumps(summary, sort_keys=True))
        return summary


if __name__=='__main__':
    main()

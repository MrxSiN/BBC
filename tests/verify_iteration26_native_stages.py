#!/usr/bin/env python3
"""Revalidate installed Linux native BF Stage 1 -> Stage 2 without cold seed.

This does not replace tests/verify_selfhost.py's independent Stage 0 run.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = (ROOT / 'compiler/core.bf').read_bytes()
    installed = ROOT / 'build/compiler_x86_64_linux.elf'
    expected = installed.read_bytes()
    historic = json.loads((ROOT / 'evidence/selfhost.json').read_text())
    assert sha(source) == historic['source_sha256']
    assert sha(expected) == historic['artifact_elf_sha256']
    records = []
    with tempfile.TemporaryDirectory(prefix='brainfuckcc-native-stage-') as tmp:
        previous = installed
        for stage in (1, 2):
            result = subprocess.run([str(previous)], input=encode_source(source), capture_output=True, timeout=90)
            assert result.returncode == 0 and not result.stderr, (stage, result.returncode, result.stderr[-100:])
            native = extract_artifact(result.stdout)
            assert native == expected, (stage, 'compiler output not byte-identical to installed')
            path = Path(tmp) / f'stage{stage}.elf'
            path.write_bytes(native)
            path.chmod(0o700)
            records.append({'stage': stage, 'executed_binary_sha256': sha(previous.read_bytes()),
                            'emitted_compiler_sha256': sha(native), 'artifact_bytes': len(native),
                            'byte_identical_to_installed': True})
            previous = path
    (ROOT / 'evidence/iteration26_native_stages.json').write_text(json.dumps({
        'date': '2026-10-13', 'iteration': 26,
        'classification': 'EXECUTED native Linux Stage 1 then generated Stage 2; independent cold Stage 0 NOT rerun',
        'source_sha256': sha(source), 'installed_compiler_sha256': sha(expected),
        'stages': records, 'cold_stage0': 'NOT_RERUN',
        'android_stage_execution': 'NOT_RERUN_ON_DEVICE',
    }, indent=2) + '\n')
    print('PASS native Linux Stage 1 -> Stage 2: both regenerated ELF images match installed bytes')


if __name__ == '__main__':
    main()

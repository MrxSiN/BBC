#!/usr/bin/env python3
"""Iteration 26: exercise the existing BF-only Android stage/transport contract.

This is an independent test oracle and byte transport, not compiler logic.
The scalable V1 compiler described in docs is NOT implemented here.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tools'), str(ROOT / 'tests')]
from run_android_loops import STAGES, compile_source, run_stage
from run_android_optimized import OPTIMIZERS
from transport import encode_source
from source_check import check_source
from reference import execute
from verify_android_aarch64_subset import emulate

OPS = b'><+-.,[]'
STUFFED = {0: b'\xff\x01', 255: b'\xff\x02'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_bf_filter(wire):
    output = run_stage('filter', wire)
    assert output and output[-1] == 1, ('malformed encoding passed', wire, output[-10:])


def main():
    inventory = {}
    historical = json.loads((ROOT / 'evidence/android_loop_pipeline.json').read_text())
    for stage, (source, elf) in STAGES.items():
        src, exe = ROOT / source, ROOT / elf
        expected = historical['stages'][stage]
        assert src.is_file() and exe.is_file()
        assert digest(src) == expected['source_sha256'], (stage, 'BF source changed')
        assert digest(exe) == expected['elf_sha256'], (stage, 'native stage changed')
        assert os.access(exe, os.X_OK), (stage, 'native BF stage is not executable')
        instructions = len(check_source(src.read_bytes()))
        assert instructions <= 16128, (stage, 'stage exceeds Linux compiler input capacity')
        inventory[stage] = dict(source=source, native_host_elf=elf, source_instructions=instructions,
                                source_sha256=digest(src), elf_sha256=digest(exe))
    optimization_history = json.loads((ROOT / 'evidence/android_native_optimization.json').read_text())
    for stage, (source, elf) in OPTIMIZERS.items():
        src, exe = ROOT / source, ROOT / elf
        expected = optimization_history['optimizers'][stage]
        assert digest(src) == expected['source_sha256']
        assert digest(exe) == expected['linux_optimizer_sha256']
        assert os.access(exe, os.X_OK)
        instructions = len(check_source(src.read_bytes()))
        assert instructions <= 16128
        inventory[stage] = dict(source=source, native_host_elf=elf, source_instructions=instructions,
                                source_sha256=digest(src), elf_sha256=digest(exe), optional=True)

    # The transport escapes only zero and FF. The Brainfuck filter must recover
    # the eight instructions and ignore everything else, including both escapes.
    raw = bytes(range(256))
    expected_wire = b''.join(STUFFED.get(b, bytes([b])) for b in raw)
    assert encode_source(raw) == expected_wire
    assert run_stage('filter', expected_wire) == bytes(c for c in raw if c in OPS) + b'\0'
    assert run_stage('filter', b'') == b'\0'
    assert run_stage('filter', encode_source(b'noise\0\xff + [] -')) == b'+[]-' + b'\0'
    for malformed in (b'\xff', b'\xff\0', b'\xff\x03', b'\xff\xff',
                      b'+\xff\x09-', b'\xff\x01\xff'):
        reject_bf_filter(malformed)

    # These are existing ten-command BF backends, not evidence of large capacity.
    programs = (b'', b'+.', b'[]', b'[[[]]]', b'+++++.', b',[.-]',
                b'++[>+<-]>.', b'+\0.\xff', b'ignored\0\xff ++[--]')
    images = []
    for raw_src in programs:
        image = compile_source(raw_src)
        assert image[:4] == b'\x7fELF' and len(image) == 4192
        assert struct.unpack_from('<H', image, 18)[0] == 183  # EM_AARCH64
        images.append(hashlib.sha256(image).hexdigest())
    assert compile_source(b'++.') == compile_source(b'ignored\0\xff+ noise + .')
    simulated = 0
    for source, data in ((b'', b''), (b'+.', b''), (b',.', b'\xff'),
                         (b',[-]', b'\x07'), (b'++[>+<-]>.', b''),
                         (b'[]', b''), (b'+++++.', b'')):
        image = compile_source(source)
        output, _ = execute(source, data, max_steps=20_000)
        for load_bias in (0, 0x4000_0000):
            observed, status, _ = emulate(image, load_bias, input_bytes=data, max_steps=30_000)
            assert (observed, status) == (output, 0), (source, data, load_bias)
            simulated += 1

    rejected = (b'[', b']', b'[[]', b'[]]', b'+' * 11, b'[]' * 6)
    for source in rejected:
        try:
            compile_source(source)
        except ValueError:
            pass
        else:
            raise AssertionError(f'invalid or >10-command input accepted: {source!r}')
    try:
        compile_source(b'+' * 1_048_577)
    except ValueError as e:
        assert '1 MiB' in str(e)
    else:
        raise AssertionError('legacy transport failed to reject oversized raw source')

    # Existing CLI must not replace a valid output with any rejected result.
    with tempfile.TemporaryDirectory(prefix='android-contract-v1-') as tmp:
        src, target = Path(tmp) / 'source.bf', Path(tmp) / 'result.elf'
        target.write_bytes(b'keep-this-existing-artifact')
        src.write_bytes(b'[+'); bad = subprocess.run(
            [sys.executable, str(ROOT / 'bootstrap/run_android_loops.py'), str(src), str(target)],
            capture_output=True, timeout=30)
        assert bad.returncode and target.read_bytes() == b'keep-this-existing-artifact'
        src.write_bytes(b'++[>+<-]>.'); good = subprocess.run(
            [sys.executable, str(ROOT / 'bootstrap/run_android_loops.py'), str(src), str(target)],
            capture_output=True, timeout=30)
        assert good.returncode == 0, good.stderr[-300:]
        assert target.read_bytes() == compile_source(src.read_bytes())

    report = {
        'date': '2026-10-13', 'iteration': 26,
        'classification': 'EXECUTED Linux-hosted BF stage and transport contract tests; not Android execution',
        'contract': 'docs/ANDROID_COMPILER_PROTOCOL_V1.md',
        'canonical_compiler_sha256': digest(ROOT / 'compiler/core.bf'),
        'canonical_linux_compiler_sha256': digest(ROOT / 'build/compiler_x86_64_linux.elf'),
        'stage_inventory': inventory,
        'transport_all_256_raw_byte_values': 'PASS',
        'invalid_wire_inputs_rejected': 6,
        'bounded_elf_cases': len(programs),
        'rejected_source_cases': len(rejected),
        'one_mib_raw_source_limit_rejected': True,
        'bounded_elf_image_sha256': images,
        'aarch64_load_base_simulation_differentials': simulated,
        'cli_atomic_preservation': 'PASS',
        'large_source_compilation': 'UNIMPLEMENTED',
        'android_native_compiler': 'UNIMPLEMENTED',
        'android_native_selfhosting': 'UNIMPLEMENTED',
    }
    (ROOT / 'evidence/iteration26_contract.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS I26 Android contract: 8 BF-owned stages, 256 raw bytes, 6 wire rejections, '
          f'{len(programs)} ELF images, {simulated} simulated AArch64 reference differentials, '
          f'{len(rejected)} negative source cases, atomic CLI')


if __name__ == '__main__':
    main()

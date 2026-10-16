#!/usr/bin/env python3
"""Iteration 63 BF-emitted DSO fail-closed validation and bounded fuzz gate.

The reference and AArch64 instruction simulator are independent of the BF
compiler stages. This test does not execute an Android device or dynamic loader.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile
from unittest.mock import patch

from bootstrap.android_callable_elf_validate63 import validate_dso
from bootstrap.android_dynamic_callable59 import compile_shared
from bootstrap.android_dynamic_callable58 import STAGES, ROOT
from tests.verify_android_dynamic_callable58 import emulate_callable, reference

# Deterministic nested-source generator, with no unbounded recursive expansion.
SEED = 63
MUTATIONS = (
    0, 4, 5, 16, 18, 24, 32, 40, 52, 54, 56, 60, 62, 64, 68,
    96, 104, 112, 120, 124, 144, 152, 0xc0, 0xc4, 0xc8,
    0xd0, 0xf8, 0xfc, 0x100, 0x108, 0x110, 0x120, 0x128,
    0x180, 0x184, 0x190, 0x240, 0x2c0, 0x340, 0x360,
)


def construct(rng: random.Random, level: int = 0) -> bytes:
    pieces = []
    for _ in range(rng.randrange(8)):
        if level < 2 and rng.random() < 0.17:
            pieces.append(b'[' + construct(rng, level + 1) + b']')
        else:
            pieces.append(bytes((rng.choice(b'+-<>.,'),)))
    return b''.join(pieces)


def verify() -> dict:
    rng = random.Random(SEED)
    result = {
        'iteration': 63,
        'classification': 'LOCAL_BF_DSO_ELF_VALIDATION_AND_AARCH64_SIMULATION',
        'BF_authoritative_compiler_modified': False,
        'host_transport_postflight_validation': True,
        'BF_generated_cases': 0, 'simulator_reference_comparisons': 0,
        'header_corruption_rejections': 0, 'truncation_rejections': 0,
        'atomic_corrupt_header_rejection': False,
        'wide_sparse_structural_test_bytes': None,
        'android_dlopen_executed': False, 'android_ART_JNI_executed': False,
        'android_native_compiler_selfhosted': False,
    }
    with tempfile.TemporaryDirectory(prefix='bfc63-') as td:
        d = Path(td); source = d / 'source.bf'; output = d / 'policy.so'
        for case in range(240):
            program = construct(rng)
            source.write_bytes(program)
            meta = compile_shared(source, output)
            image = output.read_bytes()
            checked = validate_dso(output)
            assert meta['elf_bytes'] == checked['bytes'] == len(image)
            assert meta['fixed_source_limit'] is None
            assert meta['fixed_record_limit'] is None
            assert meta['fixed_bracket_depth_limit'] is None
            for tape_size in (1, 2, 8, 32):
                inp = rng.randbytes(rng.randrange(5))
                cap = rng.randrange(6)
                budget = rng.randrange(5)
                expected = reference(program, inp, tape_size, cap, budget)
                observed = emulate_callable(image, inp, tape_size, cap, budget)
                assert (observed[0], observed[1], observed[3], observed[4]) == expected, (
                    case, program, tape_size, budget, cap)
                result['simulator_reference_comparisons'] += 1
            result['BF_generated_cases'] += 1

        good = output.read_bytes()
        for i in MUTATIONS:
            bad = bytearray(good)
            bad[i] ^= 0x01
            target = d / 'mutated.so'
            target.write_bytes(bad)
            try:
                validate_dso(target)
            except ValueError:
                result['header_corruption_rejections'] += 1
            else:
                raise AssertionError(f'corrupted BF DSO header was accepted: byte {i:#x}')
        for change in (-4, 4, -1, 1):
            target = d / 'truncated.so'
            target.write_bytes(good[:change] if change < 0 else good + bytes(change))
            try:
                validate_dso(target)
            except ValueError:
                result['truncation_rejections'] += 1
            else:
                raise AssertionError(f'mismatched ELF length accepted: {change}')

        # Inject a corrupted BF header as if an emission stage regressed.
        # The old output must not be replaced by an ELF with broken metadata.
        from bootstrap import android_dynamic_callable58 as backend
        original = backend._native_stage
        source.write_bytes(b'++[->+<]>.' )
        output.write_bytes(b'UNCHANGED')
        def damaged(name, incoming, outgoing, timeout):
            original(name, incoming, outgoing, timeout)
            if name == 'android_callable_dso_header59':
                with outgoing.open('r+b') as stream:
                    stream.seek(0xf8)
                    stream.write(b'\xff')
        with patch.object(backend, '_native_stage', damaged):
            try:
                compile_shared(source, output)
            except ValueError as exc:
                assert 'BF DSO' in str(exc)
            else:
                raise AssertionError('corrupted BF header was installed')
        assert output.read_bytes() == b'UNCHANGED'
        result['atomic_corrupt_header_rejection'] = True

        # No huge allocation: ELF header bytes come from the BF header stage.
        # A sparse file tests 64-bit declared extents and constant RAM reads;
        # it is NOT a claim to have compiled 4GiB of Brainfuck code.
        code_size = (1 << 32) + 68
        stage = STAGES / 'android_callable_dso_header59.elf'
        generated = subprocess.run([str(stage)], input=code_size.to_bytes(8, 'little'),
                                   check=True, capture_output=True, timeout=30).stdout
        assert len(generated) == 1025 and generated[-1] == 0
        sparse = d / 'sparse.so'
        with sparse.open('wb') as stream:
            stream.write(generated[:-1])
            stream.truncate(code_size + 1024)
        assert validate_dso(sparse)['bytes'] == code_size + 1024
        result['wide_sparse_structural_test_bytes'] = code_size + 1024
    result['source_sha256'] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT/'compiler/core.bf', ROOT/'experiments/android_callable_dso_header59.bf',
                  ROOT/'experiments/android_callable_slots58.bf',
                  ROOT/'experiments/android_callable_ledger58.bf')
    }
    return result


def main() -> None:
    result = verify()
    path = ROOT/'evidence/iteration63_dynamic_callable_integrity.json'
    path.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()

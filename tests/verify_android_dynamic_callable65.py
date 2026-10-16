#!/usr/bin/env python3
"""Iteration 65: growing callable relocation with file-backed duplicate indices.

Compiler decisions and native bytes still come from standard BF stages. This
suite checks host-side duplicate storage, prior-release binary parity, safe
failure, and many BF-generated loop relocations. No device run is implied.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import tracemalloc
from unittest.mock import patch

from bootstrap import android_compact_far_relocated53 as relocated
from bootstrap.android_dynamic_callable58 import ROOT
from bootstrap.android_dynamic_callable59 import compile_shared
from bootstrap.android_callable_code_validate64 import validate_code
from bootstrap.android_callable_elf_validate63 import validate_dso
from tests.verify_android_dynamic_callable58 import emulate_callable, reference

BASELINE = json.loads((ROOT / 'tests/iteration64_callable_baseline65.json').read_text())
PROGRAMS = {
    'empty': b'',
    'nested': b'++[>++[>+<-]<-]>>.',
    'adjacent512': b'[]' * 512,
    'deep1030': b'[' * 1030 + b']' * 1030,
    'io': b',.,.',
}


def verify() -> dict:
    result = {
        'iteration': 65,
        'classification': 'LINUX_BF_NATIVE_AARCH64_SIMULATOR_AND_TRANSPORT_STORAGE',
        'authoritative_BF_compiler_modified': False,
        'host_relocation_storage': 'SPARSE_TEMPORARY_FILE_ONE_BIT_PER_NATIVE_WORD',
        'baseline_iteration64_sha256_matches': 0,
        'large_BF_source_loop_pairs': 0,
        'large_BF_generated_code_bytes': 0,
        'large_source_simulator_reference_matches': 0,
        'duplicate_patch_rejected_transactionally': False,
        'file_backed_storage_marks': 0,
        'overlapping_two_word_patch_rejections': 0,
        'file_backed_peak_tracemalloc_bytes': 0,
        'android_device_executed': False,
        'android_native_dynamic_selfhosting': False,
    }
    with tempfile.TemporaryDirectory(prefix='bfc65-relocation-') as td:
        d = Path(td)
        with tempfile.TemporaryFile('w+b') as used:
            # No proportional Python set or array, including an index beyond 32 bits.
            words = (0, 2, 6, 8, 16, 24, 1048576, (1 << 35) + 3)
            for word in words:
                relocated._mark_patch_once(used, word)
            for word in words:
                try:
                    relocated._mark_patch_once(used, word)
                except ValueError as exc:
                    assert 'duplicate' in str(exc)
                else:
                    raise AssertionError(f'duplicate relocation accepted: {word}')
            # A second eight byte literal cannot begin one native word into
            # an existing literal, even when both first-literal words are zero.
            for offset in (1, 7, 9, 17):
                try:
                    relocated._mark_patch_once(used, offset)
                except ValueError as exc:
                    assert 'overlapping' in str(exc)
                    result['overlapping_two_word_patch_rejections'] += 1
                else:
                    raise AssertionError(f'overlapping native literal accepted: {offset}')
            result['file_backed_storage_marks'] += len(words)

        # Produce indices one by one. A Python set of these records would be
        # externally observable as linear heap growth.
        tracemalloc.start()
        try:
            with tempfile.TemporaryFile('w+b') as used:
                for k in range(50000):
                    relocated._mark_patch_once(used, 256 * k + (k % 13))
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        assert peak < 1_000_000, peak
        result['file_backed_storage_marks'] += 50000
        result['file_backed_peak_tracemalloc_bytes'] = peak

        src = d / 'program.bf'
        output = d / 'policy.so'
        for label, program in PROGRAMS.items():
            src.write_bytes(program)
            meta = compile_shared(src, output)
            actual = hashlib.sha256(output.read_bytes()).hexdigest()
            expected = BASELINE[label]
            assert actual == meta['elf_sha256'] == expected['elf_sha256'], label
            assert meta['elf_bytes'] == expected['bytes']
            assert meta['bracket_pairs'] == expected['bracket_pairs']
            assert validate_code(output)['bracket_pairs'] == meta['bracket_pairs']
            result['baseline_iteration64_sha256_matches'] += 1

        # Deliberately replay the same BF-emitted native patch index twice.
        # The output must remain unchanged, just as with a broken BF stage.
        src.write_bytes(b'[][]')
        output.write_bytes(b'PREVIOUS_GOOD_OUTPUT')
        original = relocated.records
        def duplicate_second_patch(*args, **kwargs):
            first = None
            for i, payload in enumerate(original(*args, **kwargs)):
                if args[5] == b'P':
                    if i == 0:
                        first = payload
                    elif i == 1:
                        payload = first
                yield payload
        with patch.object(relocated, 'records', duplicate_second_patch):
            try:
                compile_shared(src, output)
            except ValueError as exc:
                assert 'duplicate' in str(exc), exc
            else:
                raise AssertionError('reused BF patch index accepted')
        assert output.read_bytes() == b'PREVIOUS_GOOD_OUTPUT'
        result['duplicate_patch_rejected_transactionally'] = True

        # Adjacent zero-cell loops test many independent relocation pairs and
        # executable-code growth rather than synthetic patch-storage only.
        large_pairs = 12000
        program = b'[]' * large_pairs + b'+.'
        src.write_bytes(program)
        meta = compile_shared(src, output)
        assert meta['bracket_pairs'] == large_pairs
        assert meta['wide_relocation_patches'] == large_pairs * 2
        assert validate_code(output)['bracket_pairs'] == large_pairs
        assert validate_dso(output)['bytes'] == meta['elf_bytes']
        image = output.read_bytes()
        for tape_size, gas in ((1, 0), (4, 1)):
            expect = reference(program, b'', tape_size, 2, gas)
            actual = emulate_callable(image, b'', tape_size, 2, gas)
            assert (actual[0], actual[1], actual[3], actual[4]) == expect
            result['large_source_simulator_reference_matches'] += 1
        result['large_BF_source_loop_pairs'] = large_pairs
        result['large_BF_generated_code_bytes'] = meta['native_code_bytes']
        result['large_elf_sha256'] = meta['elf_sha256']

    result['compiler_source_sha256'] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT/'compiler/core.bf', ROOT/'experiments/android_callable_slots58.bf',
                  ROOT/'experiments/android_callable_ledger58.bf',
                  ROOT/'experiments/android_callable_dso_header59.bf')
    }
    return result


def main() -> None:
    report = verify()
    path = ROOT / 'evidence/iteration65_dynamic_relocation_storage.json'
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

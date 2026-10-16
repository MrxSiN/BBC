#!/usr/bin/env python3
"""Trace BF compiler tape accesses with an audit-only build of the BF seed.

The interpreter executes existing Brainfuck. Expected input bytes and native
compiler output are test oracles; no compilation logic lives in this harness.
Observed tape footprints are dynamic evidence, not a whole-program proof.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source

CORE = ROOT / 'compiler/core.bf'
SEED = ROOT / 'bootstrap/seed_interpreter.c'
NATIVE = ROOT / 'build/compiler_x86_64_linux.elf'
NOTES = ROOT / 'compiler/core.bf.notes.md'
REPORT = ROOT / 'evidence/compiler_tape_audit.json'
LIMIT = 16128
BASE = 68
STRIDE = 4
TAPE_SIZE = 65536
AUDIT_LINE = re.compile(
    rb'TAPE_AUDIT phase=(\d+) steps=(\d+) accesses=(\d+) writes=(\d+) '
    rb'source_lane_writes=(\d+) low=(\d+) high=(\d+)')


def read_offsets(source):
    notes = NOTES.read_text()
    digest = hashlib.sha256(source).hexdigest()
    assert f'Source SHA-256: `{digest}`' in notes, 'source annotations changed'
    ranges = [(int(a), int(b)) for a, b in re.findall(r'^\| `(\d+):(\d+)` \|', notes, re.M)]
    assert len(ranges) >= 6 and ranges[0][0] == 0 and ranges[-1][1] == len(check_source(source))
    assert all(ranges[i][1] == ranges[i+1][0] for i in range(len(ranges)-1))
    return ranges[0][1], ranges[-2][1], ranges[2]


def run_compiler(args, source, timeout=65):
    return subprocess.run(args, input=encode_source(source), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=timeout, check=True)


def trace_case(seed, name, source):
    args = [str(seed), str(CORE), '15000000000', source.hex()]
    observed = run_compiler(args, source)
    audit_output = observed.stderr
    assert b'AUDIT_FAIL' not in audit_output, (name, audit_output[-300:])
    matches = AUDIT_LINE.findall(audit_output)
    assert len(matches) == 2, (name, audit_output[-300:])
    phases = [dict(zip(('phase', 'steps', 'accesses', 'writes',
                        'source_lane_writes', 'low', 'high'), map(int, match)))
              for match in matches]
    header_match = re.search(rb'HEADER_SCRATCH_AUDIT entries=(\d+) exits=(\d+) pointer=(\d+) scratch=(\d+)', audit_output)
    assert header_match is not None, (name, 'missing header scratch trace')
    assert tuple(map(int, header_match.groups())) == (1, 1, 60, 0)
    assert [p['phase'] for p in phases] == [0, 1]
    filtered = bytes(c for c in source if c in b'><+-.,[]')
    assert f'TAPE_AUDIT preserved_source_bytes={len(filtered)}\n'.encode() in audit_output
    assert phases[0]['source_lane_writes'] == 0
    assert phases[0]['low'] == 0 and phases[1]['low'] >= 60
    # A bounded high-water witness tied to the current 4-cell source layout.
    # Even at the largest supported input there must be room for scratch.
    upper = max(77, BASE + STRIDE*len(filtered) + 27)
    assert all(0 <= p['low'] <= p['high'] <= upper < TAPE_SIZE for p in phases), (name, phases)
    assert all(p['accesses'] <= p['steps'] for p in phases)
    assert phases[1]['source_lane_writes'] > 0 if filtered else True
    # Compare every emitted byte against the production native compiler.
    native = run_compiler([str(NATIVE)], source)
    assert observed.stdout == native.stdout, (name, 'BF seed and native compiler differ')
    artifact = extract_artifact(observed.stdout)
    assert len(artifact) == 215 + 32*len(filtered)
    return {'case': name, 'input_bytes': len(source), 'filtered_commands':len(filtered),
            'compiler_elf_bytes': len(artifact),
            'emitted_binary_sha256': hashlib.sha256(artifact).hexdigest(),
            'phase_trace': phases, 'normalized_source_verified_after_decode_and_at_exit': True,
            'byte_identical_to_native_compiler': True,
            'header_scratch_entry_and_exit_clean': True,
            'header_scratch_checkpoints': 2}


def main():
    source = CORE.read_bytes()
    assert len(check_source(source)) == 14859
    decode_end, compile_end, (header_begin, header_end) = read_offsets(source)
    assert (header_begin, header_end) == (2848, 4277)
    assert 0 < decode_end < compile_end < len(source)
    assert NATIVE.is_file()
    with tempfile.TemporaryDirectory(prefix='bf-compiler-tape-') as td:
        seed = pathlib.Path(td) / 'audit_seed'
        subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-DBF_TAPE_AUDIT', f'-DBF_DECODE_END={decode_end}',
                        f'-DBF_COMPILE_END={compile_end}',
                        f'-DBF_HEADER_BEGIN={header_begin}',
                        f'-DBF_HEADER_END={header_end}', str(SEED), '-o', str(seed)],
                       check=True, capture_output=True)
        cases = [
            ('empty', b''),
            ('simple', b'+++++[->+++++++++++++<]>.'),
            ('comments_and_binary', b'notes\x00\xff  ++[>+<-]>.  ignored\x7f'),
            ('deep_loops', b'['*255 + b']'*255 + b'+.'),
            ('compiler_self_source', source),
            ('source_ceiling_commands', b'+'*LIMIT),
            ('source_ceiling_comments', b'!'*(LIMIT*2)),
            ('source_ceiling_zero_and_ff', b'\x00\xff'*LIMIT),
        ]
        records = [trace_case(seed, name, program) for name, program in cases]
        # Negative test: the witness must actually reject a deliberately wrong
        # source-cell oracle; otherwise a "PASS" would prove nothing.
        mismatch = subprocess.run([str(seed), str(CORE), '15000000000', '2d'],
                                  input=encode_source(b'+'), capture_output=True, timeout=10)
        assert mismatch.returncode == 90 and b'AUDIT_FAIL source_byte=' in mismatch.stderr
    report = {
        'date': '2026-10-12',
        'classification': 'EXECUTED compiler tape access witnesses; bounded phase footprints, not a formal nonoverlap proof',
        'source_sha256': hashlib.sha256(source).hexdigest(),
        'native_compiler_sha256': hashlib.sha256(NATIVE.read_bytes()).hexdigest(),
        'audit_only_seed': str(SEED.relative_to(ROOT)),
        'header_scratch_audit': {
            'cases_with_clean_entry_exit': len(records),
            'header_bf_offsets': [header_begin, header_end],
            'entry_and_exit_pointer': 60,
            'scratch_cell': 61,
            'entry_and_exit_scratch_value': 0,
            'header_entry_exit_checks': 2 * len(records),
            'classification': 'EXECUTED witnesses, not a proof of the entry precondition for all possible source',
        },
        'source_buffer_base_cell': BASE,
        'source_buffer_stride_cells': STRIDE,
        'compiler_tape_cells': TAPE_SIZE,
        'source_storage_normalization': 'Only the eight command bytes are retained; escaped 00 and FF are discarded',
        'decode_end_bf_instruction': decode_end,
        'generation_end_bf_instruction': compile_end,
        'cases_passed': len(records),
        'source_oracle_mutations_rejected': 1,
        'limitations': [
            'Observed high-water cells on the listed executions are not static proof for every possible source',
            'Compacted command lanes are temporarily written during native emission and restored; the audit checks only phase boundaries',
            'Other scratch metadata, loop stack and compiler-internal capacity separation are not proven disjoint',
            'Scratch cell 61 header-entry precondition is only witnessed, not statically proven from decoder control flow',
            'C audit seed is a test-only Brainfuck interpreter and does not generate native machine code',
        ],
        'cases': records,
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS {len(records)} compiler tape witnesses, 1 wrong-source oracle rejected; '
          f'max observed pointer cell {max(p["high"] for r in records for p in r["phase_trace"])}')


if __name__ == '__main__':
    main()

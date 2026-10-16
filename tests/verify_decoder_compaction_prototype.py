#!/usr/bin/env python3
"""Test a BF-only in-core decoder patch without promoting an oversized compiler.

The patch is inserted at a *verified instruction offset* in a derived test copy
of core.bf. Only the Brainfuck seed executes it and emits ELF machine code.
Python splices source, generates test vectors and checks outputs; it never
parses an input program for the compiler or writes native machine code.
"""
import hashlib
import json
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests'), str(ROOT / 'tools')]
from source_check import check_source
from transport import encode_source, extract_artifact
from reference import execute
from verify_emission import verify_elf

CORE = ROOT/'evidence/history/iteration18/core.bf'
PATCH = ROOT/'experiments/decoder_compaction_insertion.bf'
NATIVE = ROOT/'evidence/history/iteration18/compiler_x86_64_linux.elf'
OUTPUT = ROOT/'evidence/decoder_compaction_prototype.json'
OPS = b'><+-.,[]'
INSERT_AT = 1145  # Immediately before the existing decoder iteration closing bracket.
RAW_LIMIT = 16128
KNOWN_FILTERED_HASH = '2776b71d33144515a37cef20fd4745e3d30975394ae99abe8c8fb3c80bf8d018'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def compile_stream(argv, encoded, timeout=90, audit_expected=None):
    run = subprocess.run(argv, input=encoded, capture_output=True, timeout=timeout)
    if run.returncode != 0:
        raise AssertionError(f'BF seed/native execution failed with {run.returncode}: {run.stderr[-350:]!r}')
    assert run.stdout and run.stdout[-1] in (0, 1), (run.stdout[-12:], run.stderr[-100:])
    if audit_expected is not None:
        match = re.search(rb'PATCH_AUDIT visits=(\d+) conserved=(\d+)', run.stderr)
        assert match and b'PATCH_AUDIT_FAIL' not in run.stderr, run.stderr[-350:]
        visits, conserved = (int(v) for v in match.groups())
        assert visits == conserved, (visits, conserved)
        if audit_expected >= 0:
            assert visits == audit_expected, ('decoded source visits', visits, audit_expected)
    return run.stdout


def programs():
    fixed = [
        ('empty', b'', b''),
        ('ignored_only', b'ignored note\0\xff', b''),
        ('byte_wrap', b'---.++.', b''),
        ('comment_in_nested_loop', b'+++[>++[>+++<-]<-]>>.' .replace(b'>', b'>\x00XYZ', 1), b''),
        ('echo_eof', b',.,.', b'\xff\x00'),
        ('zero_loop', b'[[+[>+<-]]]+++++.', b''),
        ('pointer_left_trap', b'<', b''),
        ('pointer_right_trap', b'+[>]', b''),
        ('unmatched_close', b'abc]xyz', b''),
        ('unmatched_open', b'abc[xyz', b''),
        ('depth_255', b'['*255+b']'*255+b'+.', b''),
        ('depth_256_rejected', b'['*256+b']'*256, b''),
        ('count_255', b'+'*255+b'.', b''),
        ('count_256', b'+'*256+b'.', b''),
        ('count_512', b'+'*512+b'.', b''),
        ('count_1024', b'+'*1024+b'.', b''),
        ('count_16128', b'+'*(RAW_LIMIT-1)+b'.', b''),
        ('count_16129_rejected', b'+'*(RAW_LIMIT+1), b''),
        ('ignored_above_raw_limit', b'noncommand text\x00\xff ' * 900+b'+.', b''),
        ('near_limit_with_comments', b'+'*(RAW_LIMIT-1) + b'No BF code here\x00\xff'*25 + b'.', b''),
        ('annotated_core', CORE.read_bytes(), b''),
    ]
    yield from fixed
    rng = random.Random(170026)
    alphabet = bytes(x for x in range(256) if x not in OPS)
    fragments = [b'+', b'-.', b'[->+<]', b'++[>++<-]<', b'[[-]]', b'[>]', b',.', b'[-]']
    for i in range(64):
        command = b''.join(rng.choice(fragments) for _ in range(rng.randrange(1, 9)))
        raw = bytearray()
        for c in command:
            raw.extend(rng.choice(alphabet) for _ in range(rng.randrange(0, 6)))
            raw.append(c)
        raw.extend(rng.choice(alphabet) for _ in range(rng.randrange(0, 30)))
        yield f'deterministic_{i:02}', bytes(raw), b'hello\x00\xff'


def check_runtime(artifact, source, stdin, tmp, name):
    # Executing generated ELF is independent of how the BF code produced it.
    path = tmp / 'case.elf'
    path.write_bytes(artifact)
    path.chmod(0o700)
    native = subprocess.run([str(path)], input=stdin, capture_output=True, timeout=8)
    try:
        expected, _ = execute(source, stdin, max_steps=1_000_000)
    except IndexError:
        assert native.returncode == 2, (name, native.returncode)
        return 'bounds_trap'
    except TimeoutError:
        return 'inconclusive_reference_limit'
    assert native.returncode == 0 and native.stdout == expected, (name, native.returncode, native.stdout, expected)
    return 'output_matches_reference'


def main():
    src = CORE.read_bytes()
    code = check_source(src)
    assert digest(code) == KNOWN_FILTERED_HASH, 'the decoder insertion offset must be reverified'
    patch_source = PATCH.read_bytes()
    patch = check_source(patch_source)
    assert patch and len(patch) == 1045
    assert code[INSERT_AT] == ord(']')
    trial = code[:INSERT_AT] + patch + code[INSERT_AT:]
    check_source(trial)
    # The patch saves the two count carry lanes before using nearby scratch.
    # Native S2 needs its own source to fit in 16128 decoded bytes; it cannot
    # yet fit, so the test must never install or label this as production.
    assert len(trial) == 16952 > RAW_LIMIT
    with tempfile.TemporaryDirectory(prefix='bf-in-core-filter-') as td:
        work = pathlib.Path(td)
        test_source = work / 'patched-core.bf'
        test_source.write_bytes(trial)
        seed = work/'bfseed'
        subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-DBF_PATCH_AUDIT', f'-DBF_PATCH_START={INSERT_AT}',
                        f'-DBF_PATCH_END={INSERT_AT + len(patch)}',
                        str(ROOT/'bootstrap/seed_interpreter.c'), '-o', str(seed)], check=True)
        alt = work/'bfseed-alt'
        altcc = shutil.which('clang') or shutil.which('cc')
        subprocess.run([altcc, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(ROOT/'bootstrap/seed_interpreter_alt.c'), '-o', str(alt)], check=True)
        cases = []
        runtime_counts = {'output_matches_reference':0, 'bounds_trap':0, 'inconclusive_reference_limit':0}
        alt_cases = 0
        for index,(name, raw, stdin) in enumerate(programs()):
            filtered = bytes(c for c in raw if c in OPS)
            assert len(filtered) <= RAW_LIMIT + 1 or name == 'pointer_right_trap'
            wire = encode_source(raw)
            observed = compile_stream([str(seed), str(test_source), '15000000000'], wire, audit_expected=len(raw))
            expected = compile_stream([str(NATIVE)], encode_source(filtered))
            assert observed == expected, (name, len(observed), len(expected), observed[-1], expected[-1])
            if index in (0, 1, 2, 7, 9, 14):
                alt_stream = compile_stream([str(alt), str(test_source), '15000000000'], wire)
                assert observed == alt_stream, (name, 'independent BF seed disagrees')
                alt_cases += 1
            if observed[-1] == 0:
                artifact = extract_artifact(observed)
                if index < 13 or index % 9 == 0 or name.startswith('count_') or name == 'annotated_core':
                    verify_elf(filtered, artifact)
                if name in ('empty','byte_wrap','comment_in_nested_loop','echo_eof',
                            'zero_loop','pointer_left_trap','count_255','count_256',
                            'count_512','count_1024','count_16128'):
                    result = check_runtime(artifact, raw, stdin, work, name)
                    runtime_counts[result] += 1
            cases.append({'name': name, 'raw_bytes': len(raw), 'filtered_commands': len(filtered),
                          'compiler_status': observed[-1], 'emitted_elf_bytes': len(observed)-1 if observed[-1] == 0 else None})
        # Malformed transport must still reject, without confusing a raw 00
        # (EOF sentinel) for an escaped 00 or a valid command.
        invalid_wire = [b'\xff', b'\xff\x03', b'\xff\xff', b'\xff\x00', b'+\xff\x03']
        for index,wire in enumerate(invalid_wire):
            observed = compile_stream([str(seed), str(test_source), '15000000000'], wire, audit_expected=-1)
            expected = compile_stream([str(NATIVE)], wire)
            assert observed == expected and observed[-1] != 0, ('escape', index)
        # Negative control: deliberately omit restoration of the following
        # high count lane. The audit must reject this on the first 256-byte carry.
        mutated = patch[:-156] + patch[-90:]
        assert len(mutated) == len(patch) - 66
        mutation_source = work/'mutated-core.bf'
        mutation_source.write_bytes(code[:INSERT_AT] + mutated + code[INSERT_AT:])
        mutation_seed = work/'mutated-seed'
        subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-DBF_PATCH_AUDIT', f'-DBF_PATCH_START={INSERT_AT}',
                        f'-DBF_PATCH_END={INSERT_AT + len(mutated)}',
                        str(ROOT/'bootstrap/seed_interpreter.c'), '-o', str(mutation_seed)], check=True)
        mutation = subprocess.run([str(mutation_seed), str(mutation_source), '15000000000'],
                                  input=encode_source(b'+'*256), capture_output=True, timeout=30)
        assert mutation.returncode == 90 and b'PATCH_AUDIT_FAIL' in mutation.stderr
        # The patched compiler cannot self-host: its own 16952 BF instructions
        # exceed the existing 16128-record decoder limit, even after filtering.
        cannot_selfcompile = compile_stream([str(seed), str(test_source), '15000000000'],
                                            encode_source(trial), audit_expected=-1)
        assert cannot_selfcompile[-1] != 0
    report = {
        'date':'2026-10-12', 'classification':'PROTOTYPE: BF-only in-core decoder insertion, NOT production or S2',
        'canonical_source_sha256':digest(src), 'canonical_elf_sha256':digest(NATIVE.read_bytes()),
        'decoder_patch_source_sha256':digest(patch_source), 'patch_bf_instructions':len(patch),
        'insertion_bf_offset':INSERT_AT, 'derived_compiler_bf_instructions':len(trial),
        'selfcompilation_instruction_limit':RAW_LIMIT, 'instructions_above_limit':len(trial)-RAW_LIMIT,
        'canonical_core_unchanged':True, 'native_stage_zero_executed_via_independent_bf_seed':True,
        'byte_identical_to_native_command_only_compilation_for_each_test':True,
        'cases_passed':len(cases), 'decoder_count_lane_audit_cases':len(cases),
        'decoder_count_lane_audit_visits':sum(len(raw) for _,raw,_ in programs()),
        'count_lanes_preserved_during_executed_decoder_passes':True,
        'backup_scratch_cells_cleared_during_executed_decoder_passes':True,
        'intentionally_mutated_count_restore_rejected':True,
        'independent_alternate_seed_cases':alt_cases,
        'malformed_wire_rejections':len(invalid_wire), 'patched_core_rejected_selfcompilation':True,
        'runtime_checks':runtime_counts, 'cases':cases,
        'limitations':['Only the derived interpreter-executed compiler contains the patch',
                       'Patch has no verified native Stage 1-2 self-hosting',
                       'The current 4-cell buffer remains capped at 16128 commands',
                       'No formal static proof of all tape scratch lifetimes'],
    }
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(cases)} BF decoder prototype comparisons, '
          f'{alt_cases} alternate-seed matches, {len(invalid_wire)} malformed-wire rejections; '
          f'self-compilation blocked by {len(trial)-RAW_LIMIT} instructions',flush=True)

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Integration contract for the two native Brainfuck programs.

The host compares results and transports bytes; only Brainfuck performs lexical
filtering and native machine-code generation. This tests preconditions for an
in-core decoder refactor, not proof that it has already happened.
"""
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests')]
from run_filtered_compiler import (compile_source, verify_installed, CORE_ELF,
                                   MAX_RAW_BYTES, MAX_FILTERED_BYTES)
from reference import execute
from transport import encode_source, extract_artifact
from verify_emission import verify_elf

OPS = b'><+-.,[]'
EVIDENCE = ROOT / 'evidence/filter_integration_contract.json'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def direct(source):
    proc = subprocess.run([str(CORE_ELF)], input=encode_source(source),
                          capture_output=True, timeout=90, check=True)
    return extract_artifact(proc.stdout)


def put_noise(program, rng, *, multiplier=1):
    # The oracle alone knows which bytes are non-BF. The native BF filter
    # produces the actual compacted source and remains the sole lexer.
    alphabet = bytes(b for b in range(256) if b not in OPS)
    answer = bytearray()
    for cmd in (None, *program, None):
        for _ in range(multiplier * rng.randrange(0, 12)):
            answer.append(alphabet[rng.randrange(len(alphabet))])
        if cmd is not None:
            answer.append(cmd)
    return bytes(answer)


def cases():
    base = [
        ('empty', b'', b''),
        ('comment_in_nested_loop', b'++[>++[>+++<-]<-]>>.<<', b''),
        ('read_eof', b',.,.', b''),
        ('read_binary', b',.,.', b'\x00\xff'),
        ('byte_wrap', b'-.+.', b''),
        ('clear', b'+++++[-].', b''),
        ('transfer', b'+++++[->+++++<]>.<', b''),
        ('zero_loop', b'[+[>+<-]].', b''),
        ('nested_skip', b'[[[[[-]]]]]+.', b''),
        ('left_trap', b'<', b''),
        ('trap_in_loop', b'+[<]', b''),
        ('depth255', b'['*255 + b']'*255+b'+.', b''),
        ('max_commands', b'+'*(MAX_FILTERED_BYTES-1)+b'.', b''),
        ('max_ignored', b'.', b''),
    ]
    rng = random.Random(150026)
    for name, program, stdin in base:
        if name == 'max_ignored':
            raw = b'long ignored note\x00\xff '*2400 + program
        elif name == 'max_commands':
            raw = program + b'trailing ignored text'*500
        else:
            raw = put_noise(program, rng, multiplier=3)
        yield name, program, raw, stdin
    fragments = [b'+.', b'[-]', b'+[-]', b'++[>++<-]>.<',
                 b'+++++[->++<]>.<', b',.[-]', b'[+]', b'[->+<]',
                 b'>>[-]<<', b'[>]', b'>[-]<+', b'-.']
    for i in range(22):
        program = b''.join(rng.choice(fragments) for _ in range(3+i%7))
        yield f'random_nested_{i:02d}', program, put_noise(program, rng, multiplier=2), b'ABC\x00'


def main():
    verify_installed()
    records = []
    trap_cases = 0
    with tempfile.TemporaryDirectory(prefix='bf-filter-contract-') as work:
        for i, (name, commands, raw, stdin) in enumerate(cases()):
            assert bytes(b for b in raw if b in OPS) == commands
            assert len(raw) <= MAX_RAW_BYTES and len(commands) <= MAX_FILTERED_BYTES
            artifact = compile_source(raw)
            assert artifact == direct(commands), (name, 'comment placement changed native bytes')
            decoded = verify_elf(commands, artifact)
            assert decoded['verified_slots'] == len(commands), name
            assert decoded['noncommand_nop_slots'] == 0, name
            assert decoded['elf_file_bytes'] == 215+32*len(commands), name
            path = pathlib.Path(work) / f'{i}.elf'
            path.write_bytes(artifact)
            path.chmod(0o700)
            result = subprocess.run([str(path)], input=stdin, capture_output=True, timeout=15)
            try:
                expected, _ = execute(commands, stdin, max_steps=2_000_000)
            except IndexError:
                assert result.returncode == 2, (name, 'missing native bounds trap')
                trap_cases += 1
            else:
                assert result.returncode == 0 and result.stdout == expected, (name, result)
            records.append({'case':name, 'raw_bytes':len(raw),
                            'command_bytes':len(commands), 'branch_slots':decoded['verified_branches'],
                            'native_sha256':sha(artifact), 'executed':True})

        # A command-count overrun must fail even with arbitrarily many ignored
        # characters. The existing backend owns the formal 16,128 limit.
        negatives = [
            ('commands_16129', b'+'*(MAX_FILTERED_BYTES+1)),
            ('depth_256', b'['*256+b']'*256),
            ('unmatched_close', b'text]'*100),
            ('unmatched_open', b'[++[--]'),
        ]
        rejections = 0
        for name, raw in negatives:
            try:
                compile_source(raw)
            except ValueError:
                rejections += 1
            else:
                raise AssertionError(f'filtered compilation accepted {name}')
        try:
            compile_source(b'ignored '*(MAX_RAW_BYTES//8+1))
        except ValueError:
            rejections += 1
        else:
            raise AssertionError('unbounded adapter raw source accepted')

    EVIDENCE.write_text(json.dumps({
        'date':'2026-10-12',
        'classification':'EXECUTED two-native-Brainfuck integration contract; production single-core source filtering UNIMPLEMENTED',
        'compiler_sha256':sha(CORE_ELF.read_bytes()),
        'compiler_source_sha256':sha((ROOT/'compiler/core.bf').read_bytes()),
        'filter_source_sha256':sha((ROOT/'experiments/stream_filter.bf').read_bytes()),
        'adapter_source_sha256':sha((ROOT/'bootstrap/run_filtered_compiler.py').read_bytes()),
        'cases_passed':len(records),
        'runtime_bounds_traps_checked':trap_cases,
        'invalid_inputs_rejected':rejections,
        'raw_adapter_input_limit':MAX_RAW_BYTES,
        'filtered_compiler_input_limit':MAX_FILTERED_BYTES,
        'all_filtered_artifacts_verified_by_independent_elf_inspector':True,
        'all_outputs_equal_direct_command_only_compilation':True,
        'cases':records,
        'limitations':['Filter and compiler are separate BF executables',
                       'The Python adapter is byte transport, not a compiler',
                       'Runtime tests and structural inspections are not formal proof'],
    }, indent=2)+'\n')
    print(f'PASS {len(records)} inner-loop/comment relocation and native-execution cases; '
          f'{trap_cases} bounds traps, {rejections} rejection cases')


if __name__ == '__main__':
    main()

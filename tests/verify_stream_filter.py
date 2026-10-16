#!/usr/bin/env python3
"""Exercise the standalone BF-only EOF-stream lexer against the real transport.

The filter and compiler are two independent Brainfuck executables. Python is
only test orchestration and byte transport; this is NOT a production frontend.
"""
import hashlib
import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source
sys.path.insert(0, str(ROOT / 'tests'))
from verify_emission import verify_elf
from reference import execute

OPS = b'><+-.,[]'
SOURCE = ROOT / 'experiments/stream_filter.bf'
CORE = ROOT / 'compiler/core.bf'
COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'


def run(args, payload, timeout=30):
    proc = subprocess.run([str(x) for x in args], input=payload,
                          capture_output=True, timeout=timeout)
    if proc.returncode:
        raise AssertionError((args[0], 'nonzero exit', proc.returncode, proc.stderr[-100:]))
    return proc.stdout


def test_cases():
    yield 'empty', b''
    yield 'all_bytes', bytes(range(256))
    yield 'all_commands', OPS * 27
    yield 'all_noncommands', bytes(c for c in range(256) if c not in OPS)
    yield 'nul_ff_escape', b'\0\xff\x01\x02+\0-\xff[\0].'
    yield 'repetitive_comments', b'prose ' * 3500 + b'+++++.'
    yield 'large_program', b'+' * 16000 + b'.'
    yield 'large_mixed', (b'abc+\0\xff and prose ' * 1500) + b'++[-].'
    yield 'core_annotated', CORE.read_bytes()
    rng = random.Random(13102026)
    for i in range(180):
        n = rng.randrange(0, 850)
        yield f'random_{i:03d}', rng.randbytes(n)


def main():
    source = SOURCE.read_bytes()
    code = check_source(source)
    assert len(code) == 816, f'unexpected experiment BF command count: {len(code)}'
    with tempfile.TemporaryDirectory(prefix='bf-stream-filter-') as td:
        temp = pathlib.Path(td)
        artifact = extract_artifact(run([COMPILER], encode_source(source)))
        verify_elf(source, artifact)
        native = temp / 'stream-filter.elf'
        native.write_bytes(artifact)
        native.chmod(0o700)
        installed = ROOT/'build/stream_filter_x86_64_linux.elf'
        installed.write_bytes(artifact)
        installed.chmod(0o700)
        seeds = []
        for path, cc in [('bootstrap/seed_interpreter.c', 'cc'),
                         ('bootstrap/seed_interpreter_alt.c', shutil.which('clang') or 'cc')]:
            dest = temp / ('seed_' + str(len(seeds)))
            subprocess.run([cc, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            str(ROOT / path), '-o', str(dest)], check=True, capture_output=True)
            seeds.append(dest)
        records = []
        independent_checks = 0
        for i, (name, src) in enumerate(test_cases()):
            observed = extract_artifact(run([native], encode_source(src)))
            expected = bytes(c for c in src if c in OPS)
            assert observed == expected, (name, len(src), observed[:50], expected[:50])
            if i < 5 or i in (30, 80, 140):
                # The two seeds independently interpret the same BF source.
                for seed in seeds:
                    assert extract_artifact(run([seed, SOURCE, '100000000'], encode_source(src), 60)) == expected, name
                    independent_checks += 1
            records.append({'name':name, 'raw_bytes':len(src), 'commands':len(expected)})

        # Invalid byte-stuffing is a first-class BF error status. Previously
        # the streaming prototype silently accepted a malformed FF escape.
        malformed = [b'\xff', b'\xff\x00', b'\xff\x03', b'\xff\xff',
                     b'++\xff\x03++++', b'+\xff\x01+\xff\x09']
        rejected = 0
        for payload in malformed:
            result = run([native], payload)
            assert result and result[-1] == 1, ('invalid framing was accepted', payload)
            for seed in seeds:
                assert run([seed, SOURCE, '100000000'], payload, 60)[-1] == 1
            rejected += 1

        # Prototype-only chaining: the host merely forwards bytes between two
        # BF executables. No Python parsing is involved in this pipeline.
        # The front filter has no valid-framing error reporting, so feed only
        # correctly encoded source and do not make this a shipping compiler.
        compiler_cases = [
            ('comment_invariance', b'+++.', b'ignored prose\0\xff ++ more prose +.'),
            ('large_comments', b'+++++.', b'comment ' * 3000 + b'+++++.'),
            ('core', CORE.read_bytes(), check_source(CORE.read_bytes())),
        ]
        paired_compilations = []
        for label, left, right in compiler_cases:
            filtered_left = extract_artifact(run([native], encode_source(left)))
            filtered_right = extract_artifact(run([native], encode_source(right)))
            assert filtered_left == filtered_right, label
            assert len(filtered_left) <= 16128
            direct = extract_artifact(run([COMPILER], encode_source(filtered_left), 90))
            via_other = extract_artifact(run([COMPILER], encode_source(filtered_right), 90))
            assert direct == via_other, label
            if label != 'core':
                test_executable = temp / (label + '.elf')
                test_executable.write_bytes(direct)
                test_executable.chmod(0o700)
                result = subprocess.run([str(test_executable)], capture_output=True, timeout=10)
                expected_left, _ = execute(left)
                expected_right, _ = execute(right)
                assert result.returncode == 0 and result.stdout == expected_left == expected_right, label
            paired_compilations.append({'case':label, 'filtered_bytes':len(filtered_left),
                                        'native_sha256':hashlib.sha256(direct).hexdigest(),
                                        'native_program_executed':label != 'core'})
            if label == 'core':
                filtered_compiler = temp / 'filtered-compiler.elf'
                filtered_compiler.write_bytes(direct)
                filtered_compiler.chmod(0o700)
                next_compiler = extract_artifact(run([filtered_compiler], encode_source(filtered_left), 90))
                assert next_compiler == direct, 'filtered compiler self-compilation mismatch'

        evidence = {
            'date':'2026-10-12',
            'classification':'EXECUTED separate BF stream filter and experimental BF-to-BF compiler chain; production integration now implemented separately inside core.bf',
            'source_sha256':hashlib.sha256(source).hexdigest(),
            'compiler_source_sha256':hashlib.sha256(CORE.read_bytes()).hexdigest(),
            'native_filter_sha256':hashlib.sha256(artifact).hexdigest(),
            'native_compiler_sha256':hashlib.sha256(COMPILER.read_bytes()).hexdigest(),
            'bf_command_count':len(code),
            'malformed_transport_rejections':rejected,
            'compiled_filter_elf_bytes':len(artifact),
            'cases_passed':len(records),
            'seed_comparisons':independent_checks,
            'byte_values_tested':256,
            'comment_invariant_pair_compilations':paired_compilations,
            'experimental_filtered_selfhost':True,
            'input_protocol':'existing FF01/FF02 byte-stuffed source; EOF terminates input',
            'limitations':[
                'The BF lexer is a second process, not part of compiler/core.bf',
                'Raw literal NUL is indistinguishable from EOF; only the FF01/FF02 transport is accepted',
                'Production compiler still emits slots for comments and counts decoded raw bytes',
                'The external stream chain is an experiment, not the accepted single-compiler entry point',
            ],
            'cases':records,
        }
        (ROOT / 'evidence/stream_filter.json').write_text(json.dumps(evidence, indent=2)+'\n')
        installed = ROOT / 'build/stream_filter_x86_64_linux.elf'
        installed.write_bytes(artifact)
        installed.chmod(0o700)
    print(f'PASS {len(records)} streaming BF filter cases, {independent_checks} independent seed checks, '
          f'{rejected} malformed transport rejections, '
          f'{len(compiler_cases)} paired native compilations and one experimental filtered self-host')


if __name__ == '__main__':
    main()

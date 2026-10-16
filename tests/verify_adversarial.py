#!/usr/bin/env python3
"""Deterministic native-versus-reference stress tests, separate from release corpus.

The compiler is still the Brainfuck executable. This harness generates input,
executes the native output, and compares defined behavior. It never creates or
patches machine-code instructions.
"""
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
from reference import execute
from verify_emission import verify_elf

CORE = (ROOT / 'compiler/core.bf').read_bytes()
COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'
OPS = b'><+-.,[]'


def generated_cases():
    rng = random.Random(9102026)
    for i in range(100):
        p = 0
        chars = []
        for _ in range(rng.randrange(10, 260)):
            ch = rng.choice(b'+-.,<>')
            if ch == ord('<') and p == 0:
                ch = ord('+')
            if ch == ord('>') and p >= 24:
                ch = ord('-')
            if ch == ord('>'):
                p += 1
            if ch == ord('<'):
                p -= 1
            chars.append(ch)
        yield f'linear_{i:03d}', bytes(chars), rng.randbytes(80)
    for i in range(80):
        a, b, c = (rng.randrange(1, 24), rng.randrange(0, 32), rng.randrange(0, 20))
        source = b'+' * a + b'[->' + b'+'*b + b'<]>.' + b'+' * c + b'.'
        if i % 4 == 0:
            source = source.replace(b'>', b'># not-a-command\x00\xff' , 1)
        yield f'transfer_{i:03d}', source, b''
    for i in range(80):
        a, b, c = (rng.randrange(0, 8), rng.randrange(0, 12), rng.randrange(0, 12))
        source = b'+'*a + b'[>' + b'+'*b + b'[>' + b'+'*c + b'<-]<-]>>.'
        if i % 5 == 0:
            source = b'abc\x00def\xff ' + source + b'ignored symbols'
        yield f'nested_{i:03d}', source, b''
    for i in range(40):
        length = rng.randrange(0, 400)
        source = b'[' + b'<[>+<]' * (length // 5) + b'[-]>+<' + b']+.'
        yield f'dead_loop_{i:03d}', source, b''
    for i in range(20):
        source = b'[' * rng.randrange(1, 60)
        source += b'+.' * rng.randrange(0, 10)
        source += b']' * source.count(b'[')
        yield f'balanced_depth_{i:03d}', source, b''
    for i in range(20):
        source = b'<', b'+[<]', b'><<', b'+[>+]'  # all terminate with native trap 2
        yield f'bounds_{i:03d}', source[i % len(source)], b''


def main():
    sys.path.insert(0, str(ROOT / 'tools'))
    from source_check import check_source
    assert len(check_source(CORE)) == 14859
    assert COMPILER.is_file()
    source_sha = hashlib.sha256(CORE).hexdigest()
    native_sha = hashlib.sha256(COMPILER.read_bytes()).hexdigest()
    records = []
    with tempfile.TemporaryDirectory(prefix='bf-adversarial-') as td:
        target = pathlib.Path(td) / 'case.elf'
        for name, source, stdin in generated_cases():
            proc = subprocess.run([str(COMPILER)], input=encode_source(source),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=True)
            artifact = extract_artifact(proc.stdout)
            if len(records) % 18 == 0:
                try:
                    verify_elf(source, artifact)
                except ValueError as exc:
                    raise AssertionError(f"{name}: {exc}, parsed={sum(c in OPS for c in source)}") from exc
            target.write_bytes(artifact)
            target.chmod(0o700)
            native = subprocess.run([str(target)], input=stdin, capture_output=True, timeout=3)
            try:
                expected, steps = execute(source, stdin, max_steps=2_000_000)
            except IndexError:
                assert native.returncode == 2, (name, 'wrong pointer trap', native.returncode)
                expected_hex = None
            except TimeoutError:
                raise AssertionError(f'{name}: reference could not determine semantics')
            else:
                assert native.returncode == 0 and native.stdout == expected, (name, native.returncode, native.stdout, expected)
                expected_hex = expected.hex()
            records.append({'case': name, 'source_commands': sum(c in OPS for c in source),
                            'exit': native.returncode, 'output_hex': expected_hex})
        for name, bad in [('closing',b']'),('opening',b'['),('nested',b'[[+]'),
                          ('extra_close',b'[]]'),('depth_256',b'['*256+b']'*256)]:
            proc = subprocess.run([str(COMPILER)],input=encode_source(bad),
                                  capture_output=True,check=True,timeout=15)
            assert proc.stdout and proc.stdout[-1] != 0, (name, 'bad source accepted')
            records.append({'case': 'reject_' + name, 'compiler_status': proc.stdout[-1]})
        # The integrated BF decoder now discards ignored bytes before
        # recording commands in the bounded source buffer.
        probe = b'!' * 16128 + b'.'
        proc = subprocess.run([str(COMPILER)],input=encode_source(probe),
                              capture_output=True,check=True,timeout=30)
        comments_accepted = bool(proc.stdout and proc.stdout[-1] == 0)
        assert comments_accepted, 'ignored comment bytes should not use command capacity'
    evidence = {
        'date': '2026-10-12',
        'classification': 'EXECUTED differential stress tests; in-core ignored-byte compaction verified',
        'compiler_source_sha256': source_sha,
        'native_compiler_sha256': native_sha,
        'cases_passed': len(records),
        'cases_failed': 0,
        'machine_code_templates_checked_for_every_18th_case': True,
        'known_limitations': [{'case':'large_comment_only_prefix',
                              'decoded_source_bytes':len(probe),
                              'executable_commands':1,
                              'actual':'accepted because only the trailing BF instruction consumes a source record',
                              'expected_under_current_profile':'accept source containing one command'}],
        'stress_details': records,
    }
    (ROOT / 'evidence/adversarial.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f'PASS {len(records)} adversarial tests; filtered-command capacity limit confirmed')


if __name__ == '__main__':
    main()

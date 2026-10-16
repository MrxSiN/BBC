#!/usr/bin/env python3
"""Test a standalone BF-only 24-bit ELF length calculator.

This is not part of the shipping compiler. It independently calculates the same
ELF length formula that the production BF compiler now computes while scanning
its buffered raw source bytes. Unlike production, this primitive reads canonical
command-only input and does not implement buffering or comment handling.
"""
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from reference import execute

PRIMITIVE = ROOT / 'experiments/elf_file_size.bf'
SOURCE = ROOT / 'compiler/core.bf'
OPS = b'><+-.,[]'


def main():
    bf = PRIMITIVE.read_bytes()
    assert bf and set(bf) <= set(OPS)
    rng = random.Random(20261012)
    counts = [0, 1, 2, 3, 7, 8, 9, 10, 255, 256, 257, 2040, 2041,
              2042, 2048, 4095, 4096, len(bf), len(SOURCE.read_bytes()),
              16000, 16127, 16128]
    counts += [rng.randrange(16129) for _ in range(40)]
    reports = []
    with tempfile.TemporaryDirectory(prefix='bf-size-primitive-') as d:
        d = pathlib.Path(d)
        binaries = []
        for name, source in [('primary', 'seed_interpreter.c'),
                             ('alternate', 'seed_interpreter_alt.c')]:
            binary = d / name
            subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            str(ROOT / 'bootstrap' / source), '-o', str(binary)], check=True)
            binaries.append(binary)
        for index, n in enumerate(counts):
            src = bytes(OPS[(i + index) % len(OPS)] for i in range(n))
            expected = (215 + 32*n).to_bytes(4, 'little')
            primary = subprocess.run([str(binaries[0]), str(PRIMITIVE), '30000000'],
                                     input=src, capture_output=True, check=True, timeout=20)
            if primary.stdout != expected:
                raise AssertionError(f'length at {n}: got {primary.stdout.hex()}, expected {expected.hex()}')
            if n <= 512:
                independent, steps = execute(bf, src, max_steps=30000000)
                assert independent == expected, (n, 'Python reference disagrees')
            else:
                steps = None
            if n in (0, 2, 2042, 4096, 16128):
                alternate = subprocess.run([str(binaries[1]), str(PRIMITIVE), '30000000'],
                                           input=src, capture_output=True, check=True, timeout=20)
                assert alternate.stdout == expected, (n, 'alternate seed disagrees')
            reports.append({'instructions': n, 'elf_file_bytes': int.from_bytes(expected, 'little'),
                            'python_reference_checked': steps is not None})
    evidence = {
        'date': '2026-10-12',
        'classification': 'EXECUTED: independent BF reference for the now-integrated exact-size calculation',
        'primitive_sha256': hashlib.sha256(bf).hexdigest(),
        'primitive_commands': len(bf),
        'source_purity': 'PASS',
        'cases': len(reports),
        'passed': len(reports),
        'formula': '206 + (32 * number_of_source_commands) + 9',
        'input_contract': 'canonical BF commands only; zero-valued EOF; noninstruction bytes not filtered',
        'production_status': 'Exact ELF size is implemented independently in core.bf. This experimental program is not linked, included, or authoritative.',
        'remaining_limitation': 'This standalone calculation counts nonzero input bytes; production counts buffered decoded bytes, including noncommands.',
        'cases_detail': reports,
    }
    (ROOT / 'evidence/elf_size_primitive.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f"PASS {len(reports)} independent BF-only ELF size calculations; {len(bf)} commands")


if __name__ == '__main__':
    main()

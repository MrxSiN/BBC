#!/usr/bin/env python3
"""Check the BF-owned scalable source scanner; no host-side source lexer.

The test oracle may count commands. The shipping scanner must not use it.
The emitted command stream is not yet accepted by the ten-slot Android emitter
for sources larger than ten instructions.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source

SOURCE = ROOT / 'experiments/android_source_scan.bf'
NATIVE = ROOT / 'build/android_source_scan_x86_64_linux.elf'
CORE = ROOT / 'compiler/core.bf'
COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'
OPERATIONS = b'><+-.,[]'


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run_native(native: pathlib.Path, wire: bytes, timeout: int = 60) -> bytes:
    p = subprocess.run([str(native)], input=wire, capture_output=True, timeout=timeout)
    assert p.returncode == 0 and not p.stderr, (p.returncode, p.stderr[:100])
    assert len(p.stdout) >= 4, 'missing three count bytes and final status'
    return p.stdout


def validate(wire: bytes, expected: bytes, native: pathlib.Path, *, timeout: int = 60) -> bytes:
    out = run_native(native, wire, timeout)
    assert out[-1] == 0, (out[-4:].hex(), 'BF source parser unexpectedly rejected wire')
    assert out[:-4] == expected, ('output differs from source oracle', len(out), len(expected))
    assert int.from_bytes(out[-4:-1], 'little') == len(expected), 'count byte overflow or mismatch'
    return out


def main() -> None:
    commands = check_source(SOURCE.read_bytes())
    assert len(commands) < 16_128
    core = CORE.read_bytes()
    # Linux S2 compiler, not an externally written code generator.
    native_bytes = extract_artifact(run_native(COMPILER, encode_source(SOURCE.read_bytes())))
    NATIVE.write_bytes(native_bytes)
    NATIVE.chmod(0o700)
    # Ignored explanatory comments must not be consumed as BF code.
    commented = SOURCE.read_bytes() + b'\n# Spare safe note for invariance\n'
    native_commented = extract_artifact(run_native(COMPILER, encode_source(commented)))
    assert native_bytes == native_commented

    fixtures = [
        ('empty', b''),
        ('byte_alphabet', bytes(range(256))),
        ('ignored_raw_binary', bytes(c for c in range(256) if c not in OPERATIONS)),
        ('core_with_comments', core),
        ('low_wrap', b'+' * 256),
        ('low_plus', b'+' * 257),
        ('prior_compiler_cap', b'+' * 16_128),
        ('beyond_prior_compiler_cap', b'+' * 16_129),
        ('byte_carry', b'+' * 65_535),
        ('word_carry', b'+' * 65_536),
        ('very_large', b'+' * 300_000),
        ('beyond_proposed_acceptance', b'+' * 300_001),
        ('comments_and_commands', (b'\0\xff ignored+' * 1000) + b'[+.-]'),
    ]
    rng = random.Random(27102026)
    for i in range(24):
        fixtures.append((f'random_{i:02d}', rng.randbytes(rng.randrange(0, 4096))))

    cases = []
    for name, raw in fixtures:
        expected = bytes(c for c in raw if c in OPERATIONS)
        start = time.monotonic()
        observed = validate(encode_source(raw), expected, NATIVE)
        cases.append({'name': name, 'raw_bytes': len(raw), 'commands': len(expected),
                      'output_sha256': sha(observed),
                      'wall_seconds': round(time.monotonic() - start, 3)})

    invalid = (b'\xff', b'\xff\0', b'\xff\xff', b'\xff\x03',
               b'++\xff\x09--', b'\xff\x01+\xff\x00')
    for wire in invalid:
        output = run_native(NATIVE, wire)
        assert output[-1] == 1, (wire, output[-4:])

    # Near-overflow is tested by a derived BF version with the count initially
    # set to 0xFFFFFF. This avoids running 16 million expensive BF commands.
    # The derived source is test instrumentation, not authoritative compiler code.
    with tempfile.TemporaryDirectory(prefix='android-scan-overflow-') as td:
        test_source = pathlib.Path(td) / 'scan_overflow.bf'
        preset = '>' * 8 + '-' + '>' + '-' + '>' + '-' + '<' * 10
        test_source.write_text(preset + commands.decode('ascii'))
        test_native = pathlib.Path(td) / 'scan_overflow.elf'
        test_native.write_bytes(extract_artifact(run_native(COMPILER, encode_source(test_source.read_bytes()))))
        test_native.chmod(0o700)
        overflow = run_native(test_native, encode_source(b'+'))
        assert overflow == b'+\x00\x00\x00\x02', (overflow[-5:].hex(), 'overflow')
        # 0xFFFFFF is still a representable 24 bit count without increment.
        no_overflow = run_native(test_native, encode_source(b'no commands'))
        assert no_overflow == b'\xff\xff\xff\x00', no_overflow

    # Cross-check one coherent short test under two independent BF seeds.
    seed_checks = 0
    with tempfile.TemporaryDirectory(prefix='android-scan-seed-') as td:
        for which, seed in enumerate(('bootstrap/seed_interpreter.c',
                                      'bootstrap/seed_interpreter_alt.c')):
            exe = pathlib.Path(td) / f'seed{which}'
            subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            str(ROOT / seed), '-o', str(exe)], check=True, capture_output=True)
            for src in (b'\x00\xff+.[-]', b'hello [nested] +', bytes(range(256))):
                p = subprocess.run([str(exe), str(SOURCE), '30000000'],
                                   input=encode_source(src), capture_output=True, timeout=25)
                assert p.returncode == 0 and p.stdout == run_native(NATIVE, encode_source(src)), (
                    seed, p.returncode, p.stdout[-6:])
                seed_checks += 1

    report = {
        'date': '2026-10-13', 'iteration': 27,
        'classification': 'EXECUTED LINUX native BF-owned source scanning; Android source capacity gate only; general Android codegen NOT IMPLEMENTED',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE.read_bytes()),
        'instructions': len(commands), 'native_linux_elf': str(NATIVE.relative_to(ROOT)),
        'native_linux_elf_sha256': sha(native_bytes),
        'canonical_compiler_sha256': sha(core),
        'canonical_compiler_elf_sha256': sha(COMPILER.read_bytes()),
        'source_comments_do_not_change_native_image': True,
        'scanner_protocol': 'filtered command bytes followed by uint24 LE command count and uint8 status',
        'source_capacity_commands_executed': 300_001,
        'status_on_24_bit_count_overflow': 2,
        'invalid_transport_rejections': len(invalid),
        'independent_seed_checks': seed_checks,
        'tests': cases,
        'not_verified': ['source_scan integration with a general Android AArch64 emitter',
                         'native Android execution of the scanner or compiler',
                         'Android self-hosting',
                         'a complete 300000-command native Android compilation',
                         'compiler-internal source buffering or bracket relocation'],
    }
    (ROOT / 'evidence/iteration27_source_scan.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS {len(cases)} BF source scan cases; {seed_checks} independent seed checks; '
          f'{len(invalid)} malformed input rejections; native 300001-command ingestion; '
          'instrumented 24-bit overflow rejection')


if __name__ == '__main__':
    main()

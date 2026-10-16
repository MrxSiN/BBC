#!/usr/bin/env python3
"""Test an isolated Brainfuck-only command filter against all byte values.

This is a native-compiled experiment, not a compiler pass. Python supplies
input vectors and compares output bytes; the filter itself is raw Brainfuck.
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
from verify_emission import verify_elf

OPS = b'><+-.,[]'
SOURCE = ROOT / 'experiments/command_filter.bf'
CORE = ROOT / 'compiler/core.bf'
COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'


def case_chunks():
    # A one-byte count covers 0..255 input bytes. The filter treats literal
    # NUL as data, unlike naive read-until-EOF loops in Brainfuck.
    yield ('empty', b'')
    yield ('all_0_to_254', bytes(range(255)))
    yield ('all_1_to_255', bytes(range(1, 256)))
    yield ('all_command_bytes', OPS * 24)
    yield ('noncommands_only', bytes(x for x in range(256) if x not in OPS)[:248])
    yield ('nul_ff_together', b'\x00\xff+\x00-\xff[\x00]\x00')
    yield ('profile_prose', b'No variables. Only weather. The pointer is somewhere.')
    rng = random.Random(10122026)
    for index in range(128):
        count = rng.randrange(0, 256)
        yield (f'random_{index:03d}', rng.randbytes(count))


def run(process, source, payload, timeout=10):
    proc = subprocess.run(process, input=bytes((len(payload),)) + payload,
                          capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f'{source}: failed with {proc.returncode}: {proc.stderr[:200]!r}')
    expected = bytes(c for c in payload if c in OPS)
    if proc.stdout != expected:
        raise AssertionError(f'{source}: got {proc.stdout!r}, expected {expected!r}')
    return expected


def main():
    source = SOURCE.read_bytes()
    assert source and set(source) <= set(OPS), 'filter source must be canonical BF'
    with tempfile.TemporaryDirectory(prefix='bf-filter-') as tmp:
        temp = pathlib.Path(tmp)
        proc = subprocess.run([str(COMPILER)], input=encode_source(source),
                              capture_output=True, check=True, timeout=45)
        artifact = extract_artifact(proc.stdout)
        verify_elf(source, artifact)
        native = temp / 'native-filter.elf'
        native.write_bytes(artifact)
        native.chmod(0o700)
        seed = temp / 'bfseed'
        alt = temp / 'bfseed-alt'
        for name, file, cc in [('main', seed, 'cc'), ('alternate', alt, shutil.which('clang') or 'cc')]:
            subprocess.run([cc, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            str(ROOT / 'bootstrap' / ('seed_interpreter.c' if name == 'main' else 'seed_interpreter_alt.c')),
                            '-o', str(file)], check=True)
        records = []
        for index, (label, payload) in enumerate(case_chunks()):
            expected = run([str(native)], label, payload)
            # Independent seeds spot-check the Brainfuck algorithm, not just
            # the native compiler output.
            if index < 7 or index % 23 == 0:
                for interpreter in (seed, alt):
                    run([str(interpreter), str(SOURCE), '10000000'], label, payload)
            records.append({'case': label, 'bytes_in':len(payload), 'commands_out':len(expected)})
        # Byte-count framing is a standalone experiment protocol, not a
        # change to the production compiler's existing FF-escape transport.
        report = {
            'date': '2026-10-12',
            'classification': 'EXECUTED standalone BF lexer prototype; not integrated into compiler/core.bf',
            'source_sha256': hashlib.sha256(source).hexdigest(),
            'native_sha256': hashlib.sha256(artifact).hexdigest(),
            'compiler_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
            'native_compiler_sha256': hashlib.sha256(COMPILER.read_bytes()).hexdigest(),
            'source_bytes':len(source),
            'native_elf_bytes':len(artifact),
            'cases_passed': len(records),
            'cases_failed':0,
            'independent_seed_spot_checks':sum(1 for i in range(len(records)) if i < 7 or i % 23 == 0)*2,
            'all_byte_values_covered':True,
            'input_protocol':'one byte length (0..255), followed by exactly that many raw bytes',
            'limitations':'Not wired into production compiler. It only filters BF commands, not source framing or 16,128-byte buffer management. No claim of production source capacity change.',
            'cases':records,
        }
        (ROOT/'evidence/command_filter.json').write_text(json.dumps(report,indent=2)+'\n')
        installed=ROOT/'build/command_filter_x86_64_linux.elf'
        installed.write_bytes(artifact)
        installed.chmod(0o700)
    print(f'PASS {len(records)} native command-filter tests, {report["independent_seed_spot_checks"]} independent seed comparisons; all 256 byte values tested')


if __name__ == '__main__':
    main()

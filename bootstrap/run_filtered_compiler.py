#!/usr/bin/env python3
"""Experimental two-native-BF-executable file adapter.

The filter is itself a standard Brainfuck program compiled by core.bf.
Python only transports framed bytes, verifies the installed BF executables,
checks their status bytes, and installs the emitted binary. It never scans
Brainfuck instructions, decides which bytes to discard, or generates code.

This is NOT an integrated source-filtering implementation in core.bf.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from transport import encode_source, extract_artifact

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'compiler/core.bf'
CORE_ELF = ROOT / 'build/compiler_x86_64_linux.elf'
FILTER = ROOT / 'experiments/stream_filter.bf'
FILTER_ELF = ROOT / 'build/stream_filter_x86_64_linux.elf'

# Adapter transport limits. These are not Brainfuck-language or compiler limits.
# Bound Python memory consumption while preserving >16 KiB comment-heavy input.
MAX_RAW_BYTES = 8 * 1024 * 1024
MAX_FILTERED_BYTES = 16128


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_installed() -> None:
    bootstrap = json.loads((ROOT / 'evidence/selfhost.json').read_text())
    lexer = json.loads((ROOT / 'evidence/stream_filter.json').read_text())
    if (sha(CORE.read_bytes()) != bootstrap['source_sha256'] or
            sha(CORE_ELF.read_bytes()) != bootstrap['artifact_elf_sha256'] or
            sha(FILTER.read_bytes()) != lexer['source_sha256'] or
            sha(FILTER_ELF.read_bytes()) != lexer['native_filter_sha256'] or
            sha(CORE_ELF.read_bytes()) != lexer['native_compiler_sha256']):
        raise ValueError('installed BF binaries or sources do not match verified evidence')


def execute_bf_program(path: Path, payload: bytes, timeout: int) -> bytes:
    proc = subprocess.run([str(path)], input=payload, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=timeout, check=False)
    if proc.returncode:
        raise ValueError(f'{path.name} exited {proc.returncode}: {proc.stderr[-160:]!r}')
    return extract_artifact(proc.stdout)


def compile_source(raw: bytes) -> bytes:
    if len(raw) > MAX_RAW_BYTES:
        raise ValueError(f'raw input exceeds optional adapter limit ({MAX_RAW_BYTES} bytes)')
    # The first executable owns byte filtering AND malformed transport handling.
    # Its trailing status must be checked before forwarding *any* output.
    filtered = execute_bf_program(FILTER_ELF, encode_source(raw), 90)
    if len(filtered) > MAX_FILTERED_BYTES:
        raise ValueError(f'BF filter produced more than {MAX_FILTERED_BYTES} commands')
    # The second executable is the unmodified, verified BF-owned native backend.
    return execute_bf_program(CORE_ELF, encode_source(filtered), 120)


def main() -> int:
    if len(sys.argv) != 3:
        print('usage: python3 bootstrap/run_filtered_compiler.py SOURCE.bf OUTPUT.elf', file=sys.stderr)
        return 64
    source, output = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        verify_installed()
        with source.open('rb') as infile:
            raw = infile.read(MAX_RAW_BYTES + 1)
        artifact = compile_source(raw)
        # Do not leave a truncated ELF if either BF program fails.
        output.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=f'.{output.name}.', suffix='.tmp', dir=output.parent)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(artifact)
            os.chmod(temp, 0o700)
            os.replace(temp, output)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    except (OSError, ValueError, subprocess.TimeoutExpired, KeyError) as exc:
        print(f'filtered compilation failed: {exc}', file=sys.stderr)
        return 1
    print(f'Native ELF from two verified Brainfuck executables: {output} ({len(artifact)} bytes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

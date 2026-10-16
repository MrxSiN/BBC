#!/usr/bin/env python3
"""Byte-preserving RLE transport to the Brainfuck-owned 32-bit source stage.

This helper does not tokenize Brainfuck, find loops, calculate positions, or
emit machine code. The compressed representation is generic for ALL byte values.
The Brainfuck program interprets the original bytes and owns source analysis.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / 'build/android_100m_rle_scan_x86_64_linux.elf'
MAX_RAW_BYTES = 200_000_000


def compress_bytes(src, out, *, mode=0, max_bytes=MAX_RAW_BYTES):
    """Pure transport: encode equal-byte runs without inspecting their meaning."""
    if mode not in (0, 1):
        raise ValueError('invalid transport mode')
    out.write(bytes([mode]))
    prior = None
    run = 0
    total = 0

    def write_run(n, b):
        while n:
            take = min(n, 0xffffffff)
            out.write(struct.pack('<IB', take, b))
            n -= take

    while True:
        data = src.read(1 << 20)
        if not data:
            break
        total += len(data)
        if max_bytes is not None and total > max_bytes:
            raise ValueError('raw source exceeds the configured transport limit')
        for byte, group in itertools.groupby(data):
            n = sum(1 for _ in group)
            if prior == byte:
                run += n
            else:
                if prior is not None:
                    write_run(run, prior)
                run, prior = n, byte
    if prior is not None:
        write_run(run, prior)
    out.write(b'\0\0\0\0')
    return total


def scan_file(path: Path, *, emit_positions=False, max_bytes=MAX_RAW_BYTES,
              native=BINARY, max_event_output=50_000_000):
    """Run the actual BF stage; report only measured output and frame status."""
    with tempfile.TemporaryFile() as wire, tempfile.TemporaryFile() as output:
        with path.open('rb') as source:
            raw_bytes = compress_bytes(source, wire, mode=int(emit_positions),
                                       max_bytes=max_bytes)
        wire.seek(0)
        p = subprocess.run([str(native)], stdin=wire, stdout=output,
                           stderr=subprocess.PIPE, timeout=180)
        if p.returncode or p.stderr:
            raise RuntimeError(f'BF scanner exited {p.returncode}: {p.stderr[:100]!r}')
        size = output.tell()
        if size < 9 or size > max_event_output + 9 or ((size-9) % 5):
            raise ValueError('unexpected BF output record size')
        output.seek(size-9)
        footer = output.read(9)
        count, depth, status = struct.unpack('<IIB', footer)
        return dict(raw_bytes=raw_bytes, filtered_commands=count,
                    remaining_bracket_depth=depth, status=status,
                    bracket_event_records=(size-9)//5,
                    bracket_positions_emitted=emit_positions,
                    verified_balanced=(status == 0 and depth == 0),
                    compiler_code_generation='NOT_PERFORMED')


def main():
    ap = argparse.ArgumentParser(description='BF-owned 32-bit source analysis with generic raw-byte compression')
    ap.add_argument('source', type=Path)
    ap.add_argument('--bracket-positions', action='store_true')
    ap.add_argument('--max-raw-bytes', type=int, default=MAX_RAW_BYTES)
    args = ap.parse_args()
    r = scan_file(args.source, emit_positions=args.bracket_positions,
                  max_bytes=args.max_raw_bytes)
    print(json.dumps(r, indent=2))
    if not r['verified_balanced']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()

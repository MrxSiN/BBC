#!/usr/bin/env python3
"""Generic byte transport between two independently compiled Brainfuck stages.

The first Brainfuck stage classifies all raw source bytes and emits bracket
positions; the second Brainfuck stage pairs those positions. Python transports
bytes and validates framing only. It does not recognize source instructions,
match brackets, compute offsets, or emit machine instructions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from android_100m_transport import MAX_RAW_BYTES, compress_bytes

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT/'build/android_100m_rle_scan_framed_x86_64_linux.elf'
PAIRER = ROOT/'build/android_100m_bracket_pairs_x86_64_linux.elf'
MAX_OUTPUT = 50_000_000


def pair_file(path: Path, *, pairs_path: Path | None = None,
              raw_limit: int = MAX_RAW_BYTES, output_limit: int = MAX_OUTPUT,
              scanner: Path = SCANNER, pairer: Path = PAIRER):
    with tempfile.TemporaryFile() as encoded, tempfile.TemporaryFile() as events, tempfile.TemporaryFile() as results:
        with path.open('rb') as src:
            raw_bytes = compress_bytes(src, encoded, mode=1, max_bytes=raw_limit)
        encoded.seek(0)
        proc = subprocess.run([str(scanner)], stdin=encoded, stdout=events,
                              stderr=subprocess.PIPE, timeout=180)
        if proc.returncode or proc.stderr:
            raise RuntimeError(f'BF source stage failed: {proc.returncode} {proc.stderr[:128]!r}')
        event_bytes = events.tell()
        if event_bytes < 10 or (event_bytes - 10) % 5 or event_bytes > output_limit:
            raise ValueError('BF bracket-event output exceeds the framed transport contract')
        events.seek(0)
        proc = subprocess.run([str(pairer)], stdin=events, stdout=results,
                              stderr=subprocess.PIPE, timeout=180)
        if proc.returncode or proc.stderr:
            raise RuntimeError(f'BF pairing stage failed: {proc.returncode} {proc.stderr[:128]!r}')
        result_bytes = results.tell()
        if result_bytes < 2 or (result_bytes - 2) % 9 or result_bytes > output_limit:
            raise ValueError('BF bracket-pair output exceeds the framed transport contract')
        results.seek(result_bytes - 2)
        sentinel_status = results.read(2)
        if sentinel_status != b'\0\0':
            raise ValueError(f'BF pairing rejected the source: status={sentinel_status.hex()}')
        # Validate framed stream headers and copy only on success.
        # No host-side bracket pairing or relocation occurs here.
        if pairs_path is not None:
            pairs_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='wb', prefix='.bf-pairs-',
                                             dir=pairs_path.parent, delete=False) as stage:
                temp_path = Path(stage.name)
                try:
                    results.seek(0)
                    left=result_bytes
                    while left:
                        chunk=results.read(min(left,1<<20))
                        stage.write(chunk)
                        left-=len(chunk)
                    stage.flush()
                except BaseException:
                    temp_path.unlink(missing_ok=True)
                    raise
            temp_path.replace(pairs_path)
        return {'raw_bytes': raw_bytes,
                'event_records': (event_bytes-10)//5,
                'pair_records': (result_bytes-2)//9,
                'position_width_bits': 32,
                'maximum_nesting': 255,
                'pair_status': 0,
                'native_machine_code_generated': False,
                'android_execution_performed': False}


def main():
    p=argparse.ArgumentParser(description='BF-owned 32-bit source and bracket pairing')
    p.add_argument('source', type=Path)
    p.add_argument('--pairs', type=Path)
    p.add_argument('--raw-limit', type=int, default=MAX_RAW_BYTES)
    args=p.parse_args()
    result=pair_file(args.source,pairs_path=args.pairs,raw_limit=args.raw_limit)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()

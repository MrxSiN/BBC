#!/usr/bin/env python3
"""Transport-only inspection of BF-owned Windows x64 loop displacement records.

This is NOT a PE image compiler for bracketed Brainfuck. The three
Brainfuck executables own metadata parsing, matching, and displacement encoding.
Python validates transport framing and atomically saves record bytes.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
import os
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from run_windows_linear_io import run_stage, SCAN, MAX_SOURCE_BYTES
from transport import encode_source

METADATA=ROOT/'build/android_wide_bracket_metadata_x86_64_linux.elf'
PAIRS=ROOT/'build/android_wide_bracket_pairs_x86_64_linux.elf'
ENCODER=ROOT/'build/windows_x64_loop_rel32_x86_64_linux.elf'
MAX_COMMANDS=64

def produce_records(source:bytes)->bytes:
    if len(source)>MAX_SOURCE_BYTES:
        raise ValueError('source exceeds 1 MiB transport limit')
    scan=run_stage(SCAN,encode_source(source))
    if len(scan)<4 or scan[-1]!=0:
        raise ValueError('BF scanner rejected source')
    commands=scan[:-4]
    if int.from_bytes(scan[-4:-1],'little') != len(commands):
        raise ValueError('BF scanner count mismatch')
    if len(commands)>MAX_COMMANDS:
        raise ValueError('bounded Windows loop recorder accepts up to 64 commands')
    metadata=run_stage(METADATA,commands)
    if len(metadata)<2 or metadata[-2]!=0 or metadata[-1]!=0:
        raise ValueError('BF bracket metadata rejected source')
    pair=run_stage(PAIRS,metadata)
    if len(pair)<2 or pair[-2]!=0 or pair[-1]!=0:
        raise ValueError('BF bracket matcher rejected source')
    # 7-byte pair records in input, 12-byte relocation records in output.
    if (len(pair)-2)%7:
        raise ValueError('BF bracket pair framing invalid')
    output=run_stage(ENCODER,pair)
    expected=(len(pair)-2)//7*12+1
    if len(output)!=expected or output[-1]!=0:
        raise ValueError('BF x64 rel32 stage failed or returned unexpected framing')
    return output[:-1]


def main():
    ap=argparse.ArgumentParser(description='BF-owned Windows x64 bracket displacement records (not executable PE)')
    ap.add_argument('source',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    try:
        raw=produce_records(args.source.read_bytes())
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.output.parent,prefix='.windows-rel32-',delete=False) as file:
            staging=Path(file.name);file.write(raw);file.flush();os.fsync(file.fileno())
        try: os.replace(staging,args.output)
        finally: staging.unlink(missing_ok=True)
        print(f'Saved {len(raw)} BF generated x64 relocation record bytes')
    except (ValueError, OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        print(f'Windows branch inspection rejected: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())

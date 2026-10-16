#!/usr/bin/env python3
"""Transport-only 192-command Windows x64 Brainfuck compiler frontend.

Every Brainfuck-specific operation (filtering, pairing, displacement encoding,
x64 slot generation and PE patching) is owned by standard .bf executables.
This script validates framing, coordinates stages, and publishes atomically.
Windows native loader execution is not established by using this adapter.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from run_windows_linear_io import SCAN,MAX_SOURCE_BYTES,run_stage
from run_windows_loop_records import METADATA,PAIRS,ENCODER
from transport import encode_source

WRITER=ROOT/'build/windows_loop_slots_pe_192_x86_64_linux.elf'
PATCH=ROOT/'build/windows_x64_loop_patch_pe_192_x86_64_linux.elf'
MAX_COMMANDS=192
PE_BYTES=3584


def compile_source(source:bytes)->bytes:
    if len(source)>MAX_SOURCE_BYTES:
        raise ValueError('source exceeds 1 MiB transport limit')
    scanned=run_stage(SCAN,encode_source(source))
    if len(scanned)<4 or scanned[-1]!=0:
        raise ValueError('Brainfuck source scanner rejected source')
    commands=scanned[:-4]
    if int.from_bytes(scanned[-4:-1],'little')!=len(commands):
        raise ValueError('Brainfuck source count frame mismatch')
    if len(commands)>MAX_COMMANDS:
        raise ValueError('Windows 192-slot backend supports at most 192 commands')
    metadata=run_stage(METADATA,commands)
    if len(metadata)<2 or metadata[-2:]!=b'\0\0':
        raise ValueError('Brainfuck bracket metadata rejected source')
    pairs=run_stage(PAIRS,metadata)
    if len(pairs)<2 or pairs[-2:]!=b'\0\0' or (len(pairs)-2)%7:
        raise ValueError('Brainfuck bracket pair framing failed')
    records=run_stage(ENCODER,pairs)
    if len(records)!=((len(pairs)-2)//7)*12+1 or records[-1]!=0:
        raise ValueError('Brainfuck x64 relocation stage rejected source')
    # Validate transport framing only. Positions and displacements are generated
    # by the Brainfuck stages, never calculated or modified by this adapter.
    for at in range(0,len(records)-1,6):
        if records[at] not in (91,93) or not 1<=records[at+1]<=len(commands):
            raise ValueError('Brainfuck relocation record out of profile bounds')
    base=run_stage(WRITER,commands)
    if len(base)!=PE_BYTES+1 or base[-1]!=0:
        raise ValueError('Brainfuck PE emitter rejected source')
    patched=run_stage(PATCH,records[:-1]+b'\0'+base[:-1])
    if len(patched)!=PE_BYTES+1 or patched[-1]!=0:
        raise ValueError('Brainfuck PE patcher rejected source')
    image=patched[:-1]
    if image[:2]!=b'MZ' or image[0x80:0x84]!=b'PE\0\0':
        raise ValueError('Brainfuck PE artifact failed transport framing')
    return image


def main():
    ap=argparse.ArgumentParser(description='Experimental BF-owned 192-slot PE32+ Windows compiler')
    ap.add_argument('source',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    try:
        image=compile_source(args.source.read_bytes())
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.output.parent,prefix='.windows192-',delete=False) as f:
            staging=Path(f.name)
            f.write(image);f.flush();os.fsync(f.fileno())
        try:os.replace(staging,args.output)
        finally:staging.unlink(missing_ok=True)
        print(f'BF Windows PE32+ 192-slot image: {len(image)} bytes, sha256={hashlib.sha256(image).hexdigest()}')
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        print('Windows 192-slot compilation rejected:',exc,file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())

#!/usr/bin/env python3
"""Transport-only frontend for eight-command BF-owned Windows x64 PE stages.

Native BF stages own source filtering, bracket matching, x64 displacement
arithmetic, all instruction slots, and final PE byte patching. This adapter
validates byte framing and publishes the artifact atomically.
"""
from pathlib import Path
import argparse
import hashlib
import os
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from run_windows_linear_io import SCAN,MAX_SOURCE_BYTES,run_stage
from run_windows_loop_records import produce_records
from transport import encode_source

WRITER=ROOT/'build/windows_loop_slots_pe_64_seed_x86_64_linux.elf'
PATCH=ROOT/'build/windows_x64_loop_patch_pe_x86_64_linux.elf'
MAX_COMMANDS=64

def compile_source(source:bytes)->bytes:
    if len(source)>MAX_SOURCE_BYTES:
        raise ValueError('source exceeds 1 MiB transport limit')
    scanned=run_stage(SCAN,encode_source(source))
    if len(scanned)<4 or scanned[-1]!=0:
        raise ValueError('Brainfuck source scanner rejected source')
    commands=scanned[:-4]
    if int.from_bytes(scanned[-4:-1],'little')!=len(commands):
        raise ValueError('Brainfuck scanner count mismatch')
    if len(commands)>MAX_COMMANDS:
        raise ValueError('bounded Windows backend supports at most 64 commands')
    reloc=produce_records(source)
    if len(reloc)%12:
        raise ValueError('Brainfuck branch relocation frame mismatch')
    # This is transport validation of record positions, not bracket matching.
    for offset in range(0,len(reloc),6):
        tag=reloc[offset]
        pos=reloc[offset+1]
        if tag not in (91,93) or not (1<=pos<=len(commands)):
            raise ValueError('Brainfuck branch relocation record rejected')
    base=run_stage(WRITER,commands)
    if len(base)!=2049 or base[-1]!=0:
        raise ValueError('Brainfuck PE slot writer rejected source')
    patched=run_stage(PATCH,reloc+b'\0'+base[:-1])
    if len(patched)!=2049 or patched[-1]!=0:
        raise ValueError('Brainfuck PE patcher rejected records')
    image=patched[:-1]
    if image[:2]!=b'MZ' or image[0x80:0x84]!=b'PE\0\0':
        raise ValueError('Brainfuck PE artifact failed transport framing')
    return image

def main():
    ap=argparse.ArgumentParser(description='Experimental BF-only Windows x64 eight-command native PE writer')
    ap.add_argument('source',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    try:
        image=compile_source(args.source.read_bytes())
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.output.parent,prefix='.windows-full64-',delete=False) as file:
            temp=Path(file.name)
            file.write(image);file.flush();os.fsync(file.fileno())
        try:os.replace(temp,args.output)
        finally:temp.unlink(missing_ok=True)
        print('Wrote BF-generated Windows PE32+ image',len(image),'bytes',hashlib.sha256(image).hexdigest())
    except (ValueError,OSError,subprocess.TimeoutExpired,subprocess.CalledProcessError) as exc:
        print('Windows BF compilation rejected:',exc,file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())

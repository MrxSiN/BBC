#!/usr/bin/env python3
"""Transport-only adapter: BF parser and BF PE writer own all compilation.

This host process forwards BF-produced filtered commands, checks status,
checks deterministic PE framing and atomically stores the executable.
It does not lower instructions, build PE headers, or repair machine code.
"""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT=Path(__file__).resolve().parents[1]
SCAN=ROOT/'build/android_source_scan_x86_64_linux.elf'
WRITER=ROOT/'build/windows_linear_pe_64_seed_x86_64_linux.elf'
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source

MAX_SOURCE_BYTES=1024*1024
MAX_COMMANDS=64


def run_stage(path:Path, data:bytes, timeout=45):
    proc=subprocess.run([str(path)],input=data,capture_output=True,timeout=timeout)
    if proc.returncode or proc.stderr:
        raise ValueError(f'BF stage failed: {path.name}, exit {proc.returncode}')
    return proc.stdout


def compile_source(source:bytes):
    if len(source)>MAX_SOURCE_BYTES:
        raise ValueError('source over transport limit of 1 MiB')
    scanned=run_stage(SCAN,encode_source(source))
    if len(scanned)<4 or scanned[-1]!=0:
        raise ValueError('BF-owned source scanner rejected input')
    count=int.from_bytes(scanned[-4:-1],'little')
    commands=scanned[:-4]
    if count!=len(commands):
        raise ValueError('BF-owned scanner count mismatch')
    # This cap is a transport/CPU guard. The writer independently rejects
    # over-limit programs through its BF-owned final status byte.
    if count>MAX_COMMANDS:
        raise ValueError('Windows bounded compiler supports at most 64 commands')
    framed=run_stage(WRITER,commands)
    if len(framed)!=2049 or framed[-1]!=0:
        raise ValueError('Windows BF-owned emitter rejected unsupported instructions')
    image=framed[:-1]
    if image[:2]!=b'MZ' or image[0x80:0x84]!=b'PE\0\0':
        raise ValueError('Windows BF-owned emitter returned malformed artifact')
    return image


def main():
    ap=argparse.ArgumentParser(description='BF-owned bounded Windows x64 linear PE compiler')
    ap.add_argument('source',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    try:
        data=args.source.read_bytes()
        artifact=compile_source(data)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix='.windows-bf-',dir=args.output.parent,delete=False) as f:
            staging=Path(f.name)
            f.write(artifact)
            f.flush();os.fsync(f.fileno())
        try: os.replace(staging,args.output)
        finally: staging.unlink(missing_ok=True)
        print(f'Wrote {len(artifact)} byte PE32+ image sha256={hashlib.sha256(artifact).hexdigest()}')
    except (ValueError,OSError,subprocess.TimeoutExpired) as e:
        print(f'Windows BF compilation rejected: {e}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())

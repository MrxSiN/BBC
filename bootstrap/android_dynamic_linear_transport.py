#!/usr/bin/env python3
"""Lossless byte framing and atomic output for a standard-Brainfuck native slot stage.

This is transport, not a compiler. It neither parses Brainfuck instructions nor
constructs machine code, relocations, or ELF headers. Each source byte is sent
unchanged inside a one-byte presence frame; Brainfuck decides what it means.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_STAGE=ROOT/'build/android_streaming_linear_slots_x86_64_linux.elf'


def emit_linear_slots(source:Path, output:Path, *, stage:Path=DEFAULT_STAGE,
                      max_output_bytes:int|None=None) -> dict:
    if max_output_bytes is not None and max_output_bytes < 0:
        raise ValueError('max_output_bytes must be nonnegative')
    raw_bytes=0
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryFile() as framed:
        with source.open('rb') as raw:
            while True:
                data=raw.read(1<<20)
                if not data:break
                raw_bytes+=len(data)
                pair=bytearray(2*len(data))
                pair[::2]=b'\x01'*len(data)
                pair[1::2]=data
                framed.write(pair)
        framed.write(b'\0')
        framed.seek(0)
        fd,tmp_name=tempfile.mkstemp(prefix='.bf-linear-',dir=output.parent)
        temporary=Path(tmp_name)
        slots=0
        size=0
        proc=None
        try:
            with os.fdopen(fd,'wb') as target:
                proc=subprocess.Popen([str(stage)],stdin=framed,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                assert proc.stdout is not None
                while True:
                    kind=proc.stdout.read(1)
                    if kind==b'\x01':
                        native=proc.stdout.read(48)
                        if len(native)!=48:raise ValueError('incomplete native slot record')
                        if max_output_bytes is not None and size+48>max_output_bytes:
                            raise ValueError('native slot output exceeds caller resource policy')
                        target.write(native)
                        slots+=1
                        size+=48
                    elif kind==b'\x00':
                        status=proc.stdout.read(1)
                        if status!=b'\0':
                            raise ValueError(f'Brainfuck native slot stage rejected source: status={status.hex()}')
                        if proc.stdout.read(1):raise ValueError('trailing bytes after native stage footer')
                        break
                    else:raise ValueError('truncated or malformed native slot stream')
                target.flush();os.fsync(target.fileno())
            assert proc is not None
            exit_code=proc.wait()
            if exit_code!=0:
                raise RuntimeError(f'Brainfuck native slot stage process failed: {exit_code}')
            temporary.replace(output)
            return {'raw_source_bytes':raw_bytes,'linear_instruction_slots':slots,
                    'native_code_bytes':size,'resource_limit':max_output_bytes,
                    'compilation_stage':'BRAINfuck_AARCH64_LINEAR_RAW_CODE_ONLY',
                    'elf_generated':False,'bracket_support':False,
                    'android_loader_executed':False}
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill();proc.wait()
            temporary.unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description='Dynamic raw AArch64 slots from Brainfuck source; no ELF output')
    p.add_argument('source',type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    p.add_argument('--max-output-bytes',type=int)
    p.add_argument('--stage',type=Path,default=DEFAULT_STAGE)
    a=p.parse_args()
    print(json.dumps(emit_linear_slots(a.source,a.output,stage=a.stage,
                                       max_output_bytes=a.max_output_bytes),indent=2))
if __name__=='__main__':main()

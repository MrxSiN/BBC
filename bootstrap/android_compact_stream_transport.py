#!/usr/bin/env python3
"""Generic lossless byte transport for the Brainfuck-owned compact AArch64 stage.

No source filtering, arithmetic optimization, assembly or ELF construction is
performed by this transport. Tag one gives an opaque length-prefixed instruction
record produced by Brainfuck; only its bytes are copied. The result is raw code.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_STAGE=ROOT/'build/android_streaming_compact_slots_x86_64_linux.elf'


def emit_compact_slots(source:Path, output:Path, *, stage:Path=DEFAULT_STAGE,
                       max_output_bytes:int|None=None)->dict:
    if max_output_bytes is not None and max_output_bytes < 0:
        raise ValueError('output byte quota must be nonnegative')
    raw_bytes=0
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryFile() as wire:
        with source.open('rb') as infile:
            while True:
                data=infile.read(1<<20)
                if not data:break
                raw_bytes+=len(data)
                frame=bytearray(2*len(data));frame[::2]=b'\1'*len(data);frame[1::2]=data
                wire.write(frame)
        wire.write(b'\0');wire.seek(0)
        fd,name=tempfile.mkstemp(prefix='.bf-compact-',dir=output.parent)
        temp_path=Path(name)
        child=None
        try:
            count=0;written=0
            with os.fdopen(fd,'wb') as out:
                child=subprocess.Popen([str(stage)],stdin=wire,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                assert child.stdout is not None
                while True:
                    tag=child.stdout.read(1)
                    if tag==b'\1':
                        length_raw=child.stdout.read(1)
                        if len(length_raw)!=1:raise ValueError('missing BF record length')
                        size=length_raw[0]
                        if size<4 or size>48 or size%4:raise ValueError('invalid BF native instruction record size')
                        chunk=child.stdout.read(size)
                        if len(chunk)!=size:raise ValueError('truncated BF native record')
                        if max_output_bytes is not None and written+size>max_output_bytes:
                            raise ValueError('native code exceeds caller output byte quota')
                        out.write(chunk);count+=1;written+=size
                    elif tag==b'\0':
                        status=child.stdout.read(1)
                        if status!=b'\0':raise ValueError(f'BF code emitter rejected input: {status.hex()}')
                        if child.stdout.read(1):raise ValueError('unexpected bytes after BF terminator')
                        break
                    else:raise ValueError('truncated BF instruction stream')
                out.flush();os.fsync(out.fileno())
            assert child is not None
            if child.wait()!=0:raise RuntimeError('BF code emitter process exited unsuccessfully')
            temp_path.replace(output)
            return {'raw_source_bytes':raw_bytes,'instruction_records':count,'native_code_bytes':written,
                    'output_resource_quota':max_output_bytes,
                    'bf_owned_instruction_encoding':True,'image_kind':'AARCH64_RAW_CODE_ONLY',
                    'loops_supported':False,'android_elf_generated':False,
                    'android_device_executed':False}
        finally:
            if child is not None and child.poll() is None:
                child.kill();child.wait()
            temp_path.unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description='BF-owned compact raw AArch64 code emitter; no ELF')
    p.add_argument('source',type=Path)
    p.add_argument('-o','--output',type=Path,required=True)
    p.add_argument('--stage',type=Path,default=DEFAULT_STAGE)
    p.add_argument('--max-output-bytes',type=int)
    a=p.parse_args()
    print(json.dumps(emit_compact_slots(a.source,a.output,stage=a.stage,
                                        max_output_bytes=a.max_output_bytes),indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Opt-in growing callable AArch64 ELF for loop-free ordinary Brainfuck.

The source-to-instruction and length-to-header transformations are performed by
standard BF executables. This adapter only provides raw-byte transport, file
storage, length framing and transactional output. Brackets are deliberately
rejected until scalable BF-owned loop relocation is connected.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / 'build' / 'iteration57_dynamic'


def _native_stage(name: str, incoming: Path, outgoing: Path, timeout: int) -> None:
    native = STAGES / (name + '.elf')
    if not native.is_file():
        raise FileNotFoundError(f'Native standard-BF stage not built: {native}')
    with incoming.open('rb') as source, outgoing.open('w+b') as sink:
        subprocess.run([str(native)], stdin=source, stdout=sink,
                       stderr=subprocess.PIPE, check=True, timeout=timeout)
        sink.flush()


def compile_callable(source: Path, output: Path, *, max_code_bytes: int | None = None,
                     timeout: int = 300) -> dict:
    """Transform streamed raw bytes to callable native image with atomic commit."""
    if max_code_bytes is not None and max_code_bytes < 0:
        raise ValueError('negative caller resource quota')
    source = Path(source); output = Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.callable57-',dir=output.parent) as folder:
        temp = Path(folder)
        stream = temp/'framed.bin'
        source_digest=hashlib.sha256()
        source_bytes=0
        with source.open('rb') as s, stream.open('wb') as sink:
            while data := s.read(1<<16):
                source_digest.update(data)
                source_bytes+=len(data)
                frame=bytearray(2*len(data))
                frame[::2]=b'\1'*len(data)
                frame[1::2]=data
                sink.write(frame)
            sink.write(b'\0')
        code=temp/'code.bin'
        _native_stage('android_callable_linear57',stream,code,timeout)
        code_bytes = code.stat().st_size
        if code_bytes < 69:
            raise ValueError('BF emitter emitted a truncated code frame')
        with code.open('r+b') as f:
            f.seek(-1,os.SEEK_END)
            status = f.read(1)[0]
            if status:raise ValueError('BF callable emitter rejected bracketed source; dynamic loop relocation not implemented')
            f.truncate(code_bytes-1)
        code_bytes -= 1
        if max_code_bytes is not None and code_bytes > max_code_bytes:
            raise ValueError('BF emitted code exceeds caller resource quota')
        if code_bytes > (1<<64)-129:
            raise ValueError('ELF 64-bit length overflow')
        length=temp/'length.bin'
        length.write_bytes(code_bytes.to_bytes(8,'little'))
        header=temp/'header.bin'
        _native_stage('android_callable_header57',length,header,timeout)
        h=header.read_bytes()
        if len(h)!=129 or h[-1]:
            raise ValueError('BF callable header stage rejected artifact length')
        if h[96:104] != (128+code_bytes).to_bytes(8,'little') or h[104:112]!=h[96:104]:
            raise ValueError('BF ELF header length differs from BF code byte count')
        if h[:4]!=b'\x7fELF' or h[120:124]!=b'BFP1':
            raise ValueError('invalid BF-generated ELF header')
        temp_target=temp/'image.elf'
        digest=hashlib.sha256()
        with temp_target.open('wb') as image:
            image.write(h[:-1]);digest.update(h[:-1])
            with code.open('rb') as native:
                while data:=native.read(1<<20):
                    image.write(data);digest.update(data)
            image.flush();os.fsync(image.fileno())
        temp_target.chmod(0o755)
        temp_target.replace(output)
        return {'format':'AARCH64_ET_DYN_CALLABLE_BFP1','mode':'DYNAMIC_LINEAR_NO_LOOPS',
                'source_bytes':source_bytes,'source_sha256':source_digest.hexdigest(),
                'native_code_bytes':code_bytes,
                'elf_bytes':output.stat().st_size,'elf_sha256':digest.hexdigest(),
                'fixed_source_limit':None,'fixed_record_limit':None,
                'fixed_nesting_limit':'NOT_APPLICABLE_BRACKETS_REJECTED','loops_supported':False,
                'BF_codegen':'STANDARD_BRAINFUCK','BF_ELF_header':'STANDARD_BRAINFUCK',
                'transport_role':'RAW_BYTE_FRAMES_FILE_STORAGE_AND_ATOMIC_COMMIT',
                'android_device_executed':False,'android_jni_integrated':False}


def main():
    parser=argparse.ArgumentParser(description='BF-owned growing callable AArch64 linear compiler')
    parser.add_argument('source',type=Path)
    parser.add_argument('-o','--output',required=True,type=Path)
    parser.add_argument('--max-code-bytes',type=int)
    a=parser.parse_args()
    print(json.dumps(compile_callable(a.source,a.output,max_code_bytes=a.max_code_bytes),indent=2))

if __name__=='__main__':main()

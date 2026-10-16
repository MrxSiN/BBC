#!/usr/bin/env python3
"""Disk-backed transport for three *standard Brainfuck* Android compiler stages.

Compiler decisions (the eight-command slot templates, native word offsets, and
nested bracket pairing) are made by BF programs. This host only frames raw
bytes, copies opaque code records, and stores opaque stack records. No machine
word patching, ELF construction, branch-distance calculation, or BF execution
is performed. Output is an atomic *relocation bundle*, NOT an executable.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_STAGE = ROOT/'build/android_streaming_compact_all8_x86_64_linux.elf'
LEDGER_STAGE = ROOT/'build/android_compact_native_offset_ledger51_x86_64_linux.elf'
PAIR_STAGE = ROOT/'build/android_dynamic_stack_pairs_x86_64_linux.elf'


def exact(reader, n):
    out=bytearray()
    while len(out)<n:
        b=reader.read(n-len(out))
        if not b:raise ValueError('truncated Brainfuck output frame')
        out.extend(b)
    return bytes(out)


def make_bundle(source: Path, bundle: Path, *, max_native_bytes=None, max_pairs=None,
                code_stage=CODE_STAGE, ledger_stage=LEDGER_STAGE, pair_stage=PAIR_STAGE):
    if max_native_bytes is not None and max_native_bytes<0:raise ValueError('negative code quota')
    if max_pairs is not None and max_pairs<0:raise ValueError('negative pair quota')
    try:
        from .android_dynamic_stack_transport import pair_events
    except ImportError:
        from android_dynamic_stack_transport import pair_events
    bundle.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.bf-compact-reloc-',dir=bundle.parent) as folder:
        tmp=Path(folder);wire=tmp/'source.frame';code=tmp/'code.bin';events=tmp/'events.bin';pairs=tmp/'pairs.bin'
        raw_sha=hashlib.sha256();raw_bytes=0
        with source.open('rb') as stream,wire.open('wb') as framed:
            while block:=stream.read(1<<19):
                raw_sha.update(block);raw_bytes+=len(block)
                frame=bytearray(len(block)*2);frame[::2]=b'\1'*len(block);frame[1::2]=block
                framed.write(frame)
            framed.write(b'\0')
        with wire.open('rb') as framed,code.open('wb') as dest:
            proc=subprocess.Popen([str(code_stage)],stdin=framed,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                assert proc.stdout is not None
                count=0;size=0
                while True:
                    tag=exact(proc.stdout,1)
                    if tag==b'\1':
                        n=exact(proc.stdout,1)[0]
                        if n<4 or n>252 or n%4:raise ValueError('invalid Brainfuck code record size')
                        chunk=exact(proc.stdout,n)
                        if max_native_bytes is not None and size+n>max_native_bytes:
                            raise ValueError('native output exceeds caller resource quota')
                        dest.write(chunk);size+=n;count+=1
                    elif tag==b'\0':
                        status=exact(proc.stdout,1)
                        if status!=b'\0':raise ValueError('Brainfuck code emitter rejected source')
                        if proc.stdout.read(1):raise ValueError('trailing code emitter output')
                        break
                    else:raise ValueError('invalid BF code output tag')
                if proc.wait()!=0:raise RuntimeError('BF code emitter failed')
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
        with wire.open('rb') as framed,events.open('wb') as dest:
            proc=subprocess.Popen([str(ledger_stage)],stdin=framed,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                assert proc.stdout is not None
                num_events=0;total_words=None
                while True:
                    tag=exact(proc.stdout,1)
                    if tag in (b'\1',b'\2'):
                        dest.write(tag+exact(proc.stdout,8));num_events+=1
                    elif tag==b'\3':
                        if total_words is not None:raise ValueError('repeated native length')
                        total_words=int.from_bytes(exact(proc.stdout,8),'little')
                        if exact(proc.stdout,2)!=b'\0\0':raise ValueError('BF ledger overflow or rejection')
                        if proc.stdout.read(1):raise ValueError('trailing native ledger output')
                        break
                    else:raise ValueError('invalid BF native offset tag')
                if proc.wait()!=0:raise RuntimeError('BF native offset ledger failed')
                if total_words is None or total_words*4!=size:
                    raise ValueError('native ledger and code emitter disagree about code length')
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
        pairing=pair_events(events,pairs,stage=pair_stage,max_pairs=max_pairs)
        if pairing['matched_pairs']*2!=num_events:raise ValueError('pair and ledger count mismatch')
        def sha(path):
            with path.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
        manifest={
            'format':'BF_ANDROID_COMPACT_UNRELOCATED_V1',
            'artifact_kind':'RAW_AARCH64_CODE_AND_BF_OWNED_WORD_OFFSETS_NOT_ELF',
            'raw_source_bytes':raw_bytes,'raw_source_sha256':raw_sha.hexdigest(),
            'native_instruction_records':count,'native_code_bytes':size,
            'native_word_count':total_words,'bracket_events':num_events,
            'matched_pairs':pairing['matched_pairs'],
            'maximum_observed_depth':pairing['maximum_observed_depth'],
            'native_code_sha256':sha(code),'pairs_sha256':sha(pairs),
            'source_classification':'STANDARD_BRAINFUCK',
            'native_position_arithmetic':'STANDARD_BRAINFUCK_64BIT_WORDS',
            'bracket_pairing':'STANDARD_BRAINFUCK_FILE_BACKED_STACK',
            'relocation_word_encoding_integrated':False,
            'android_loadable_elf':False,'android_device_executed':False,
            'program_behavior_executed':False,
            'resource_limits':{'max_native_bytes':max_native_bytes,'max_pairs':max_pairs}}
        manifest_file=tmp/'manifest.json';manifest_file.write_text(json.dumps(manifest,indent=2)+'\n')
        artifact=tmp/'bundle.zip'
        with zipfile.ZipFile(artifact,'w',compression=zipfile.ZIP_STORED) as z:
            for p in (code,pairs,manifest_file):z.write(p,p.name)
        artifact.replace(bundle)
        return manifest


def main():
    p=argparse.ArgumentParser(description='BF-owned compact AArch64 code plus BF-owned 64-bit bracket relocations (not ELF)')
    p.add_argument('source',type=Path);p.add_argument('-o','--output',type=Path,required=True)
    p.add_argument('--max-native-bytes',type=int);p.add_argument('--max-pairs',type=int)
    a=p.parse_args()
    print(json.dumps(make_bundle(a.source,a.output,max_native_bytes=a.max_native_bytes,max_pairs=a.max_pairs),indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Iteration 36: independent oracle for BF-owned relocation through 2000 slots.

The Linux-native patcher is unchanged BF; this verifies its two-byte walk and
its integration with the BF-only ELF relayout/rebase stages. No device test.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'bootstrap'), str(ROOT/'tests'), str(ROOT/'tools')]
from run_android_extended import (compile_source, check_provenance,
     WIDE_512_SOURCE, WIDE_512_NATIVE, EXTENDED_LOOP_EVIDENCE)
from verify_android_tape_rebase import check_image
from verify_android_aarch64_subset import emulate
from reference import execute
from transport import encode_source, extract_artifact
from source_check import check_source


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def make_case(n: int, tail: bytes) -> bytes:
    assert n >= len(tail)
    return b'+' * (n - len(tail)) + tail


def pairs(source: bytes):
    stack=[]
    matches=[]
    for i, command in enumerate(source, 1):
        if command == ord('['):stack.append(i)
        if command == ord(']'):
            assert stack
            matches.append((stack.pop(),i))
    assert not stack
    return matches


def verify_branches(source: bytes, image: bytes) -> int:
    matches=pairs(source)
    for opening, closing in matches:
        delta=closing-opening
        for slot, word in ((opening,0x14000000 | ((12*delta+10)&0x03ffffff)),
                           (closing,0x14000000 | ((10-12*delta)&0x03ffffff))):
            at=0x210+48*(slot-1)+8
            assert image[at:at+4]==struct.pack('<I',word),(len(source),slot,opening,closing)
    return len(matches)


def main():
    start=time.monotonic()
    proof=json.loads(EXTENDED_LOOP_EVIDENCE.read_text())
    bf=WIDE_512_SOURCE.read_bytes(); instructions=check_source(bf)
    native=WIDE_512_NATIVE.read_bytes()
    assert sha(bf)==proof['source_sha256']
    assert sha(native)==proof['native_linux_elf_sha256']
    assert sha(instructions)==proof['filtered_sha256']
    # Same Brainfuck stream and ELF whether comments are present or removed.
    independently_compiled=0
    for source in (bf,instructions):
        result=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
              input=encode_source(source),capture_output=True,check=True,timeout=60)
        assert extract_artifact(result.stdout)==native
        independently_compiled+=1
    check_provenance(allow_loops=True,multiclass=True,tape_relocated=True)
    boundary=[512,513,671,672,1023,1024,1025,1353,1354,1355,1356,
              1695,1696,1697,1999,2000]
    cases=[(b'+'*(n-4)+b'[-].') for n in boundary]
    # Loop begins at slot one and its closing branch reaches the last slot.
    for n in (513,1025,1355,2000):
        cases.append(b'[' + b'+'*(n-2) + b']')
    # Nested and sequential loops with positions on both sides of tape moves.
    tails=[b'+[>+<-]>.',b'++[>++[>+<-]<-]>>.',b'[-][].',b'[[-]]',
           b'[->+<]>.',b'[+]']
    for i,n in enumerate((1025,1300,1355,1696,1999,2000)):
        cases.append(make_case(n,tails[i]))
    # Dense loop records test repeated BF table writes and walking past 512.
    cases.extend([b'<' + b'+'*1995 + b'[-].',
                  b',' + b'+'*1995 + b'[-].',
                  b'[]'*40+b'+'*1920,b'['*32+b']'*32+b'+'*1936,
                  b'+'*1897+b'[-]'+b'[]'*50])
    rng=random.Random(2026101336)
    for _ in range(8):
        n=rng.choice((513,720,1025,1355,1499,1696,1876,2000))
        tail=rng.choice([b'[-].',b'[-][].',b'[>+<-]>.',b'[->+<]>.'])
        cases.append(make_case(n,tail))
    input_bytes=bytes(range(256))*16
    tested=matched=executions=expected_traps=tape_changes=large=0
    for source in cases:
        assert len(source)<=2000
        image=compile_source(source,allow_loops=True,multiclass=True,tape_relocated=True)
        aligned=check_image(image,len(source))
        matched+=verify_branches(source,image)
        assert image[0x210:0x210+48*len(source)]
        if len(source)>1024:large+=1
        if aligned>=0x14000:tape_changes+=1
        try:
            expected,_=execute(source,input_bytes,max_steps=250000)
            trap=False
        except IndexError:
            expected=b'';trap=True;expected_traps+=1
        except TimeoutError:
            raise AssertionError(f'nonterminating fixture length {len(source)}')
        for bias in (0,0x40000000):
            out,status,_=emulate(image,bias,tape_base_rva=aligned+0x60,
                code_limit=0x220+48*len(source),input_bytes=input_bytes,
                max_steps=250000)
            if trap:
                assert status==2,(len(source),status)
            else:
                assert (out,status)==(expected,0),(len(source),status,out[:32],expected[:32])
            executions+=1
        tested+=1
    negative=[b'+'*2718+b'[-].',b'['+b'+'*2719+b']',
              b'['+b'+'*1998,b']'+b'+'*1200,b'['*256+b']'*256]
    rejected=0
    for source in negative:
        try:compile_source(source,allow_loops=True,multiclass=True,tape_relocated=True)
        except ValueError: rejected+=1
        else:raise AssertionError(f'invalid case accepted: {len(source)}')
    # Under the old flag, no silent expansion of the non-relocated writer.
    for source in (b'+'*1022+b'[-]',b'+'*1500):
        try:compile_source(source,allow_loops=True,multiclass=True)
        except ValueError: rejected+=1
        else:raise AssertionError('legacy flag accepted expanded source')
    atomic=False
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);src=root/'input.bf';dest=root/'output.elf'
        command=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),
                 str(src),str(dest),'--multiclass','--tape-relocated','--loops']
        dest.write_bytes(b'original');src.write_bytes(b'+'*2720)
        p=subprocess.run(command,capture_output=True,timeout=50)
        assert p.returncode!=0 and dest.read_bytes()==b'original'
        atomic=True
        src.write_bytes(make_case(2000,b'[-].'))
        p=subprocess.run(command,capture_output=True,timeout=50)
        assert p.returncode==0,p.stderr
        assert dest.read_bytes()==compile_source(src.read_bytes(),allow_loops=True,multiclass=True,tape_relocated=True)
        if shutil.which('readelf'):
            p=subprocess.run(['readelf','-Wl',str(dest)],capture_output=True,text=True,check=True)
            assert 'Requesting program interpreter: /system/bin/linker64' in p.stdout
            assert 'LOAD' in p.stdout and 'R E' in p.stdout and 'RW ' in p.stdout
    proof['verified']={'BF_source_variants_native_byte_identical':independently_compiled,
       'programs_checked':tested,'simulator_executions':executions,
       'bracket_pairs_verified':matched,'programs_above_1024':large,
       'rebased_tape_cases':tape_changes,'expected_tape_traps':expected_traps,
       'expected_rejections':rejected,'output_preservation_on_rejection':atomic,
       'readelf_checked':bool(shutil.which('readelf')),
       'android_loader_executed':False,'android_native_selfhosting':False,
       'elapsed_seconds':round(time.monotonic()-start,3)}
    EXTENDED_LOOP_EVIDENCE.write_text(json.dumps(proof,indent=2)+'\n')
    print('ITERATION 36 WIDE LOOPS 2000 PASS',proof['verified'],flush=True)

if __name__=='__main__':main()

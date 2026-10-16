#!/usr/bin/env python3
"""Iteration 35: BF-only ELF tape rebase, length carry, and extended linear path.

This is Linux-native BF execution plus AArch64 simulation, not an Android test.
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
from run_android_extended import (compile_source, TAPE_REBASE_NATIVE,
    TAPE_REBASE_SOURCE, TAPE_REBASE_EVIDENCE, check_provenance, bf_native)
from source_check import check_source
from transport import encode_source, extract_artifact
from reference import execute
from verify_android_aarch64_subset import emulate


def check_image(image: bytes, n: int) -> int:
    assert image.startswith(b'\x7fELF\2\1\1')
    assert struct.unpack_from('<H',image,18)[0] == 183
    rx_size = 0x220+48*n
    aligned = (rx_size+0x3fff) & ~0x3fff
    assert len(image) == aligned+96
    ph = [struct.unpack_from('<IIQQQQQQ',image,64+56*i) for i in range(5)]
    assert [v[0] for v in ph]==[6,3,1,1,2]
    rx,rw,dynamic=ph[2:]
    assert rx[1]==5 and rx[2:7]==(0,0,0,rx_size,rx_size)
    assert rw[1]==6 and rw[2:7]==(aligned,aligned,aligned,96,65632)
    assert dynamic[2:5] == (aligned,aligned,aligned)
    assert dynamic[5:7]==(96,96)
    assert rx[7]==rw[7]==0x4000
    assert rw[3]>=rx[5]
    # BF patcher must preserve all original instructions after the startup.
    assert struct.unpack_from('<I',image,0x200)[0]==0x90000014+(aligned//0x4000)*0x20
    assert image[0x201:0x204]==b'\0\0\x90'
    assert image[rx_size:aligned]==bytes(aligned-rx_size)
    return aligned


def main():
    started=time.monotonic()
    proof=json.loads(TAPE_REBASE_EVIDENCE.read_text())
    raw=TAPE_REBASE_SOURCE.read_bytes()
    stream=check_source(raw)
    assert len(stream)==proof['bf_instructions']
    assert hashlib.sha256(raw).hexdigest()==proof['source_sha256']
    assert hashlib.sha256(stream).hexdigest()==proof['filtered_sha256']
    native=TAPE_REBASE_NATIVE.read_bytes()
    assert hashlib.sha256(native).hexdigest()==proof['native_linux_elf_sha256']
    assert len(native)==215+32*len(stream)
    # All compiler implementation logic in this stage is runnable BF.
    matching=0
    for source in (raw,stream):
        result=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
            input=encode_source(source),capture_output=True,timeout=75,check=True)
        assert extract_artifact(result.stdout)==native
        matching+=1
    check_provenance(multiclass=True,tape_relocated=True)
    counts=[0,1,2,74,255,256,330,331,671,672,1012,1013,1023,1024,
            1353,1354,1355,1356,1695,1696,1697,1999,2000]
    for n in counts:
        check_image(compile_source(b'+'*n,multiclass=True,tape_relocated=True),n)
    rng=random.Random(2026101335)
    programs=[b'',b'+'*2000,b'+'*1999+b'.',b'+'*1353+b'.',
              b'+'*1354+b'.',b'+'*1695+b'.',b'+'*1696+b'.',
              b'<'*2000,b'+'*1020+b'[-].',b'+'*1016+b'[->+<]>.',
              b'['*255+b']'*255,b'>'*1999+b'<',b','*1999+b'.',
              b'+'*1998+b'>.']
    for _ in range(20):
        n=rng.choice([800,1012,1024,1200,1354,1355,1450,1695,1696,2000])
        if n<=1024 and rng.randrange(2):
            p=b'+'*(n-4)+b'[-].'
        else:
            chars=b'+-.,><'
            p=bytes(rng.choice(chars) for _ in range(n))
        programs.append(p)
    io=bytes(range(256))*12
    sims=0
    traps=0
    for p in programs:
        is_loop=b'[' in p
        image=compile_source(p,allow_loops=is_loop,multiclass=True,tape_relocated=True)
        base=check_image(image,len(p))
        try:
            expected,_=execute(p,io,max_steps=200000)
            trapped=False
        except IndexError:
            trapped=True;expected=b'';traps+=1
        for bias in (0,0x40000000):
            actual,code,_=emulate(image,bias,tape_base_rva=base+0x60,
                code_limit=0x220+48*len(p),input_bytes=io,max_steps=200000)
            if trapped:assert code==2,(len(p),code)
            else:assert (actual,code)==(expected,0),(len(p),code,actual[:16],expected[:16])
            sims+=1
    rejects=0
    for source,options in ((b'+'*2720,{}),(b'+'*2718+b'[-]',{'allow_loops':True}),
                           (b'+'*2718+b'[+]',{'allow_loops':True}),
                           (b'['+b'+'*999,{'allow_loops':True}),
                           (b'['*256+b']'*256,{'allow_loops':True})):
        try:
            compile_source(source,multiclass=True,tape_relocated=True,**options)
        except (ValueError,TypeError):rejects+=1
        else:raise AssertionError(f'unsupported source accepted: {len(source)}')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);src=td/'program.bf';dest=td/'result.elf'
        cli=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),
             str(src),str(dest),'--multiclass','--tape-relocated','--loops']
        src.write_bytes(b'+'*2720);dest.write_bytes(b'keep original')
        result=subprocess.run(cli,capture_output=True,timeout=45)
        assert result.returncode and dest.read_bytes()==b'keep original'
        src.write_bytes(b'+'*1999+b'.')
        result=subprocess.run(cli,capture_output=True,timeout=45)
        assert result.returncode==0,result.stderr
        assert dest.read_bytes()==compile_source(src.read_bytes(),multiclass=True,tape_relocated=True)
        if shutil.which('readelf'):
            result=subprocess.run(['readelf','-Wl',str(dest)],capture_output=True,text=True,check=True)
            assert 'Requesting program interpreter: /system/bin/linker64' in result.stdout
    proof['verified']={'stage_source_variants_byte_identical':matching,
        'size_boundaries_checked':len(counts),'programs_compared':len(programs),
        'aarch64_simulator_runs':sims,'reference_expected_tape_traps':traps,
        'expected_rejections':rejects,'cli_atomic_failure_preservation':True,
        'readelf_checked':bool(shutil.which('readelf')),
        'android_loader_execution':False,'independent_cold_linux_bootstrap':'NOT_RERUN',
        'elapsed_seconds':round(time.monotonic()-started,3)}
    TAPE_REBASE_EVIDENCE.write_text(json.dumps(proof,indent=2)+'\n')
    print('ITERATION 35 TAPE REBASE PASS',proof['verified'])

if __name__=='__main__':main()

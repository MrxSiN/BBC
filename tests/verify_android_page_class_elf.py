#!/usr/bin/env python3
"""Independent checks of the BF-authored two size-class Android ELF stage."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from transport import encode_source,extract_artifact
from source_check import check_source
from run_android_extended import (compile_source,bf_native,PAGE_CLASS_SOURCE,
    PAGE_CLASS_NATIVE,PAGE_CLASS_EVIDENCE)
from verify_android_aarch64_subset import emulate,PACK,TEMPLATES,NOP
from reference import execute
sha=lambda b:hashlib.sha256(b).hexdigest()
EXIT=PACK([0xd2800000,0xd2800ba8,0xd4000001,NOP])
REFERENCE_DYN=(ROOT/'build/android_dynamic_linear_255_aarch64.elf').read_bytes()[0x4000:0x4060]


def structure(image,source):
    n=len(source);rx_size=0x220+48*n
    off=0x4000 if n<=330 else 0x8000
    assert len(image)==off+96 and image[:8]==b'\x7fELF\2\1\1\0'
    assert struct.unpack_from('<H',image,18)[0]==183
    ph=[struct.unpack_from('<IIQQQQQQ',image,64+56*i) for i in range(5)]
    assert [x[0] for x in ph]==[6,3,1,1,2]
    rx,rw,dyn=ph[2:]
    assert (rx[1],rx[2],rx[3],rx[5],rx[6],rx[7])==(5,0,0,rx_size,rx_size,0x4000)
    assert (rw[1],rw[2],rw[3],rw[5],rw[6],rw[7])==(6,off,0x10000,96,65632,0x4000)
    assert (dyn[2],dyn[3],dyn[5],dyn[6])==(off,0x10000,96,96)
    assert image[0x200:0x210]==PACK([0x90000094,0x91018294,0xaa1403f3,NOP])
    assert image[0x210+48*n:0x220+48*n]==EXIT
    assert image[rx_size:off]==bytes(off-rx_size)
    assert image[off:off+96]==REFERENCE_DYN
    for i,command in enumerate(source):
        if command in TEMPLATES:
            assert image[0x210+48*i:0x210+48*(i+1)]==TEMPLATES[command]
    for p in (rx,rw):assert p[2]%p[7]==p[3]%p[7]
    assert rx_size <= 0x10000 and rw[3]>=rx_size
    return rx_size


def main():
    start=time.monotonic()
    source=PAGE_CLASS_SOURCE.read_bytes()
    filtered=check_source(source)
    assert len(filtered)<=16128
    original=PAGE_CLASS_NATIVE.read_bytes()
    for s in (source,filtered):
        r=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
              input=encode_source(s),capture_output=True,check=True,timeout=90)
        assert extract_artifact(r.stdout)==original
    # Direct stage: all boundary and carry values are checked, even when source
    # emission is not exercised in order to keep test execution bounded.
    direct_checks=0
    for n in (0,1,74,254,255,256,329,330,331,332,510,511,512):
        raw=bf_native(PAGE_CLASS_NATIVE,n.to_bytes(2,'little')+bytes(48*n),'page class')
        size=0x4000 if n<=330 else 0x8000
        assert len(raw)==size+96+2 and raw[-2:]==b'\0\0'
        assert struct.unpack_from('<Q',raw,0xd0)[0]==0x220+48*n
        assert struct.unpack_from('<Q',raw,0xf0)[0]==size
        direct_checks+=1
    rng=random.Random(2026101331)
    cases=[b'',b'+',b'-',b'+.',b'+-'*255,b'+'*329+b'.',b'+'*330+b'.',
           b'+'*511+b'.',b'<'*512,b'>'*512,b','*511+b'.',b'+'*512,
           b'+'*255+b'comment'+b'+'*77+b'.']
    for _ in range(65):
        n=rng.choice((rng.randint(0,255),rng.randint(256,512)))
        cases.append(bytes(rng.choice(b'+-.<>,') for _ in range(n)))
    cases_run=0;sim_runs=0;traps=0
    input_bytes=bytes((i*107+7)&255 for i in range(600))
    for source in cases:
        filtered_source=bytes(b for b in source if b in b'><+-.,[]')
        img=compile_source(source,page_class=True)
        rx=structure(img,filtered_source)
        try: expected,_=execute(filtered_source,input_bytes,max_steps=30000);trap=False
        except IndexError:expected=None;trap=True;traps+=1
        for bias in (0,0x40000000):
            output,status,_=emulate(img,bias,tape_base_rva=0x10060,
                  code_limit=rx,input_bytes=input_bytes,max_steps=12000)
            assert (status==2) if trap else ((output,status)==(expected,0)),(source[:20],bias,status,output,expected)
            sim_runs+=1
        cases_run+=1
    loops=[b'[]',b'+[->+<]>.',b'+++[>++[>+<-]<-]>>.',b'[]'*37]
    for s in loops:
        img=compile_source(s,page_class=True,allow_loops=True)
        rx=structure(img,s)
        expected,_=execute(s,b'',max_steps=20000)
        for bias in (0,0x40000000):
            out,status,_=emulate(img,bias,tape_base_rva=0x10060,code_limit=rx,max_steps=14000)
            assert (out,status)==(expected,0)
            sim_runs+=1
    rejected=0
    for source,allow_loops in ((b'+'*513,False),(b'['+b'+'*511+b']',True),
                               (b'[+',True),(b']',True),(b'+'*511+b'[]',True)):
        try:compile_source(source,page_class=True,allow_loops=allow_loops)
        except ValueError:rejected+=1
        else:raise AssertionError('unsupported source accepted')
    # CLI must not replace a preexisting result on rejection.
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);s=p/'src.bf';output=p/'out.elf'
        s.write_bytes(b'+'*513);output.write_bytes(b'do not overwrite')
        args=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(s),str(output),'--page-class']
        result=subprocess.run(args,capture_output=True,text=True,timeout=40)
        assert result.returncode!=0 and output.read_bytes()==b'do not overwrite'
        s.write_bytes(b'+'*330+b'.')
        result=subprocess.run(args,capture_output=True,text=True,timeout=40)
        assert result.returncode==0 and output.read_bytes()==compile_source(s.read_bytes(),page_class=True)
        for n in (0,330,331,512):
            output.write_bytes(compile_source(b'+'*n,page_class=True))
            q=subprocess.run(['readelf','-Wl',str(output)],capture_output=True,text=True,check=True)
            assert 'Requesting program interpreter: /system/bin/linker64' in q.stdout
            assert q.stdout.count('LOAD')>=2
    e=json.loads(PAGE_CLASS_EVIDENCE.read_text())
    e.update({'classification':'EXECUTED_LINUX_NATIVE_BF_STAGE_SIMULATED_AARCH64',
      'source_variants_compiled_to_identical_linux_elf':2,'direct_size_boundary_cases':direct_checks,
      'linear_source_cases':cases_run,'bounded_loop_cases':len(loops),
      'aarch64_simulator_runs':sim_runs,'pointer_traps':traps,'rejected_inputs':rejected,
      'readelf_validated_counts':[0,330,331,512],
      'aligned_elf_file_bytes':[16480,32864],
      'first_new_size_class_command_count':331,
      'maximum_linear_commands':512,'maximum_loop_commands':74,
      'android_device_executed':False,'android_native_selfhosting':False,
      'selfhosting_linux_fresh_replay': bool(json.loads((ROOT/'evidence/iteration31_linux_selfhost_replay.json').read_text())['stage2_identical']),
      'elapsed_seconds':round(time.monotonic()-start,3)})
    PAGE_CLASS_EVIDENCE.write_text(json.dumps(e,indent=2)+'\n')
    print(f'page-class writer: {cases_run} linear cases; {len(loops)} loop cases; '
          f'{sim_runs} AArch64 simulator runs; {direct_checks} boundary cases; {rejected} rejections')
if __name__=='__main__':main()

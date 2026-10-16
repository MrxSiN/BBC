#!/usr/bin/env python3
"""Independent checks for BF-owned variable-RX-length AArch64 PIE wrapper.

Python is an isolated oracle/transport. ELF generation, slot instruction
encoding and bounded loop relocation occur in native BF-authored stages.
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

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tools'),str(ROOT/'tests')]
from transport import encode_source,extract_artifact
from source_check import check_source
from run_android_extended import (compile_source,bf_native,DYNAMIC_SOURCE,DYNAMIC_NATIVE,
                                  DYNAMIC_EVIDENCE)
from verify_android_aarch64_subset import emulate,NOP,TEMPLATES,PACK
from reference import execute

sha=lambda x:hashlib.sha256(x).hexdigest()
COMPILER=ROOT/'build/compiler_x86_64_linux.elf'
EXIT=PACK([0xd2800000,0xd2800ba8,0xd4000001,NOP])
DYN=ROOT/'build/android_aarch64_loop_demo.elf'


def structural(image,commands):
    n=len(commands)
    assert len(image)==16480 and image[:8]==b'\x7fELF\2\1\1\0'
    assert struct.unpack_from('<H',image,18)[0]==183
    assert struct.unpack_from('<Q',image,24)[0]==0x200
    phdrs=[struct.unpack_from('<IIQQQQQQ',image,64+i*56) for i in range(5)]
    assert [p[0] for p in phdrs]==[6,3,1,1,2]
    rx,rw,dyn=phdrs[2:]
    assert (rx[1],rx[2],rx[3],rx[5],rx[6],rx[7])==(5,0,0,0x220+48*n,0x220+48*n,0x4000)
    assert (rw[1],rw[2],rw[3],rw[5],rw[6],rw[7])==(6,0x4000,0x8000,96,65632,0x4000)
    assert (dyn[2],dyn[3],dyn[5],dyn[6])==(0x4000,0x8000,96,96)
    assert image[0x160:0x175]==b'/system/bin/linker64\0'
    assert image[0x200:0x210]==PACK([0x90000054,0x91018294,0xaa1403f3,NOP])
    assert image[0x210+48*n:0x220+48*n]==EXIT
    assert image[0x220+48*n:0x4000]==bytes(0x4000-(0x220+48*n))
    assert image[0x4000:0x4060]==DYN.read_bytes()[0x1000:0x1060]
    for i,b in enumerate(commands):
        if b in TEMPLATES:
            assert image[0x210+48*i:0x210+48*(i+1)]==TEMPLATES[b]
    for p in (rx,rw):assert p[2]%p[7]==p[3]%p[7]
    return rx[5]


def main():
    start=time.monotonic()
    bf=DYNAMIC_SOURCE.read_bytes()
    filtered=check_source(bf)
    assert len(filtered)<=16128
    expected=DYNAMIC_NATIVE.read_bytes()
    for source in (bf,filtered):
        result=subprocess.run([str(COMPILER)],input=encode_source(source),check=True,
                              capture_output=True,timeout=90)
        assert extract_artifact(result.stdout)==expected
    manifest={
      'iteration':30,'classification':'EXECUTED_LINUX_NATIVE_BF_DYNAMIC_RX_PIE_SIMULATED',
      'stage':{'source':str(DYNAMIC_SOURCE.relative_to(ROOT)),
               'source_sha256':sha(bf),'filtered_sha256':sha(filtered),
               'bf_instructions':len(filtered),
               'native_linux_elf':str(DYNAMIC_NATIVE.relative_to(ROOT)),
               'native_linux_elf_sha256':sha(expected),'native_linux_elf_bytes':len(expected)}
    }
    # The pipeline checks hashes before allowing execution.
    DYNAMIC_EVIDENCE.write_text(json.dumps(manifest,indent=2)+'\n')
    # Test at carries and previously unsupported command counts.
    rng=random.Random(2026101330)
    testcases=[b'',b'+',b'+.',b'+'*74,b'+'*75,b'+'*100+b'.',
               b'+'*254+b'.',b','*254+b'.',b'>'*255,b'<'*255,
               b'+-.<>,',b'\x00+ hello world +.']
    for _ in range(67):
        src=bytes(rng.choice(b'+-.<>,') for _ in range(rng.randint(0,255)))
        testcases.append(src)
    image_cases=0;traps=0;runtime_checks=0
    test_input=bytes((i*101+7)&255 for i in range(300))
    for source in testcases:
        commands=bytes(b for b in source if b in b'<>+-,.[]')
        image=compile_source(source,dynamic=True)
        limit=structural(image,commands)
        try:out,_=execute(commands,test_input,max_steps=30000);trap=False
        except IndexError:out=None;trap=True;traps+=1
        for bias in (0,0x40000000):
            obs,status,_=emulate(image,bias,tape_base_rva=0x8060,code_limit=limit,
                                  input_bytes=test_input,max_steps=8000)
            assert (status==2) if trap else ((obs,status)==(out,0)),(source[:30],bias,status,obs,out)
            runtime_checks+=1
        image_cases+=1
    # Exhaustively check carry handling at every admitted one-byte count.
    for n in range(256):
        payload=bytes([n])+bytes(48*n)
        data=bf_native(DYNAMIC_NATIVE,payload,'dynamic-count')
        assert len(data)==16482 and data[-2:]==b'\0\0'
        assert struct.unpack_from('<Q',data,0xd0)[0]==0x220+48*n
        assert struct.unpack_from('<Q',data,0xd8)[0]==0x220+48*n
        assert data[0x220+48*n:0x4000]==bytes(0x4000-0x220-48*n)
    # Preserve bounded loop capabilities, but don't disguise 75+ loops as done.
    loopcases=[b'[]',b'+[->+<]>.',b'++++[->+++<]>.',
               b'+++[>++[>+<-]<-]>>.',b'+'*60+b'[->+<]>.',b'[]'*37]
    loop_checks=0
    for source in loopcases:
        assert len(source)<=74
        image=compile_source(source,dynamic=True,allow_loops=True)
        rx=structural(image,source)
        out,_=execute(source,b'',max_steps=15000)
        for bias in (0,0x40000000):
            observed,status,_=emulate(image,bias,tape_base_rva=0x8060,code_limit=rx,max_steps=14000)
            assert (observed,status)==(out,0)
        loop_checks+=1
    # Native-source fragments (BF stage) must behave the same under an independent interpreter.
    seed_checks=0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as tmp:
            for seed in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=Path(tmp)/seed
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/seed),'-o',str(exe)],
                               check=True,capture_output=True)
                data=b'\0' # 16KiB ELF output even for an empty program
                interp=subprocess.run([str(exe),str(DYNAMIC_SOURCE),'100000000'],
                                      input=data,capture_output=True,timeout=75,check=True).stdout
                native=bf_native(DYNAMIC_NATIVE,data,'dynamic')
                assert interp==native
                seed_checks+=1
    # Verify rejected requests cannot overwrite a previous valid output file.
    rejections=0
    for source,allowloops in ((b'+'*256,False),(b'['*38+b']'*38,False),
                              (b'+'*255+b'[]',True),(b'['+b'+'*254+b']',True),
                              (b'[+',True),(b']',True)):
        try:compile_source(source,dynamic=True,allow_loops=allowloops)
        except ValueError:rejections+=1
        else:raise AssertionError('invalid or unsupported source was accepted')
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp);src=path/'input.bf';exe=path/'program.elf'
        src.write_bytes(b'+'*256);exe.write_bytes(b'keep original')
        args=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(src),str(exe),'--dynamic']
        p=subprocess.run(args,capture_output=True,text=True,timeout=30)
        assert p.returncode!=0 and exe.read_bytes()==b'keep original'
        src.write_bytes(b'+'*100+b'.')
        p=subprocess.run(args,capture_output=True,text=True,timeout=30)
        assert p.returncode==0,p.stderr
        assert exe.read_bytes()==compile_source(src.read_bytes(),dynamic=True)
    # Validate p_filesz changes with n; full file length changes only at alignment crossings.
    assert structural(compile_source(b'',dynamic=True),b'')==0x220
    assert structural(compile_source(b'+'*255,dynamic=True),b'+'*255)==0x31f0
    for n in (0,74,75,255):
        with tempfile.NamedTemporaryFile(suffix='.elf') as f:
            f.write(compile_source(b'+'*n,dynamic=True));f.flush()
            p=subprocess.run(['readelf','-Wl',f.name],capture_output=True,text=True,check=True)
            assert '/system/bin/linker64' in p.stdout and 'LOAD' in p.stdout
    example_source=ROOT/'examples/android_long_linear_255.bf'
    example_elf=ROOT/'build/android_dynamic_linear_255_aarch64.elf'
    if example_source.is_file() and example_elf.is_file():
        expected_example=compile_source(example_source.read_bytes(),dynamic=True,allow_loops=True)
        assert len(expected_example)==16480 and example_elf.read_bytes()==expected_example
        manifest['example']={
            'source':str(example_source.relative_to(ROOT)),
            'source_sha256':sha(example_source.read_bytes()),
            'elf':str(example_elf.relative_to(ROOT)),
            'elf_sha256':sha(expected_example),'elf_bytes':len(expected_example),
            'source_commands':255,'readelf_inspected':True}
    manifest.update({
      'maximum_generated_commands':255,'all_256_count_values_passed':True,
      'machine_slot_bytes':48,
      'variable_executable_segment_bytes':[0x220,0x31f0],
      'aligned_elf_file_bytes':16480,'load_align':16384,
      'emulated_linear_cases':image_cases,'simulator_runs':runtime_checks,
      'pointer_traps':traps,'bounded_loop_cases':loop_checks,
      'expected_rejections':rejections,'independent_interpreter_matches':seed_checks,
      'clean_cli_atomic_preservation':True,
      'android_device_executed':False,'android_compiler_selfhosting':False,
      'genuinely_general_size_class_switching':False,
      'general_bracket_relocation_beyond_74':False,
      'elapsed_seconds':round(time.monotonic()-start,3)})
    DYNAMIC_EVIDENCE.write_text(json.dumps(manifest,indent=2)+'\n')
    print('dynamic AArch64 BF stage:',image_cases,'linear images;',loop_checks,'bounded loop images;',
          runtime_checks+loop_checks*2,'simulator executions;',seed_checks,'seed comparisons')

if __name__=='__main__':main()

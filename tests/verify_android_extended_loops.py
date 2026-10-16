#!/usr/bin/env python3
"""Cross-check BF-owned 74-slot relocation and executable images.

The Python interpreter, slot oracle, and AArch64 simulator are development
validation only. Native machine instruction emission and patching are BF-owned.
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
from transport import encode_source, extract_artifact
from source_check import check_source
from run_android_extended import (compile_source, bf_native, PATCH_SOURCE, PATCH_NATIVE,
                                  PATCH_EVIDENCE, SLOT_NATIVE, check_provenance)
from run_android_loops import run_stage
from verify_android_aarch64_subset import emulate, NOP
from reference import execute


def sha(x):return hashlib.sha256(x).hexdigest()


def oracle_pairs(src):
    stack=[];pairs=[]
    for pos,b in enumerate(src,1):
        if b==ord('['):stack.append(pos)
        elif b==ord(']'):
            assert stack
            pairs.append((stack.pop(),pos))
    assert not stack
    return pairs


def verify_patched(image,code):
    assert len(image)==4192 and image[:4]==b'\x7fELF'
    expected={}
    for a,b in oracle_pairs(code):
        d=b-a
        expected[a]=struct.pack('<I',0x14000000|((12*d+10)&0x3ffffff))
        expected[b]=struct.pack('<I',0x14000000|((10-12*d)&0x3ffffff))
    for position,word in expected.items():
        offset=0x210+(position-1)*48
        assert image[offset:offset+4]==b'\x69\x02\x40\x39'
        assert image[offset+8:offset+12]==word,(code,position,image[offset+8:offset+12].hex(),word.hex())
    return len(expected)//2


def main():
    start=time.monotonic()
    src=PATCH_SOURCE.read_bytes(); filtered=check_source(src)
    assert len(filtered)<=16128
    compiler=ROOT/'build/compiler_x86_64_linux.elf'
    generated=extract_artifact(subprocess.run([str(compiler)],input=encode_source(src),
                                              check=True,capture_output=True,timeout=35).stdout)
    assert generated==PATCH_NATIVE.read_bytes()
    stripped=extract_artifact(subprocess.run([str(compiler)],input=encode_source(filtered),
                                             check=True,capture_output=True,timeout=35).stdout)
    assert stripped==generated
    manifest={
        'iteration':29,'classification':'EXECUTED_LINUX_NATIVE_BF_PATCHED_AARCH64_ELF_SIMULATED',
        'source':str(PATCH_SOURCE.relative_to(ROOT)),
        'source_sha256':sha(src),'filtered_sha256':sha(filtered),
        'bf_instructions':len(filtered),
        'native_linux_elf':str(PATCH_NATIVE.relative_to(ROOT)),
        'native_linux_elf_sha256':sha(generated),
        'native_linux_elf_bytes':len(generated),
    }
    PATCH_EVIDENCE.write_text(json.dumps(manifest,indent=2)+'\n')
    check_provenance(allow_loops=True)
    # Exact stage protocol: count, encoded BF records and status, then slots.
    for n in (0,1,2,11,74):
        src_linear=b'+'*n
        slots=bf_native(SLOT_NATIVE,src_linear,'slot')[:-5]
        patched=bf_native(PATCH_NATIVE,bytes([n])+b'\0\0'+slots,'patch')
        assert patched==slots+b'\0\0'
    # Bracketed programs include zero trips, transfers, nested loops and
    # loop branch targets across the old ten-instruction boundary.
    programs=[b'[]',b'[[]]',b'[+]',b'+[->+<]>.',
              b'++++++++++[>++++++++<-]>.',b'+'*40+b'[->+<]>.',
              b'+'*66+b'[-]>.',b'['+b'+'*70+b']',
              b'+++[>++[>+<-]<-]>>.',b'+'*60+b'[>+<-]>.',
              b'[-][-][-][-][-][-][-][-][-][-][-]',
              b'+'*71+b'[-]',b'['*37+b']'*37,b'[]'*37,
              b'+[-]+[-]+[-]+[-]+[-]+[-]+[-]+[-]+[-]',
              b',.[-],.[-],.', b'>'*12+b'++[<+>-]<.',
              b'<',b'+'*74,b','*74]
    rng=random.Random(2026101329)
    for _ in range(65):
        base=bytearray()
        for _ in range(rng.randint(1,8)):
            kind=rng.randrange(5)
            if kind==0:base.extend(b'[-]')
            elif kind==1:base.extend(b'[+[->+<]]') # outer loop zero, skipped
            elif kind==2:base.extend(b'+[-]')
            elif kind==3:base.extend(b'+[>+<-]')
            else:base.extend(b'+-.')
        if len(base)<=74:programs.append(bytes(base))
    passed=0;loops=0;invalid=0;traps=0;linear_parity=0
    for code in programs:
        assert len(code)<=74
        image=compile_source(code,allow_loops=True)
        loops+=verify_patched(image,code)
        if b'[' not in code:
            assert image==compile_source(code,allow_loops=False)
            linear_parity+=1
        inp=b'\x00\xff\x7f\x13\x09\x00'
        try:
            expected,_=execute(code,inp,max_steps=20000)
            trapped=False
        except IndexError:
            trapped=True;expected=None;traps+=1
        for bias in (0,0x40000000):
            observed,status,_=emulate(image,bias,input_bytes=inp,max_steps=15000)
            if trapped:assert status==2,(code,status)
            else:assert (observed,status)==(expected,0),(code,observed,status,expected)
        passed+=1
    for malformed in (b'[',b']',b'[][][',b'[]]',b'+'*60+b'[',b']'+b'+'*60):
        try:compile_source(malformed,allow_loops=True)
        except ValueError:invalid+=1
        else:raise AssertionError(f'accepted unmatched source {malformed!r}')
    for oversized in (b'+'*75,b'['+b'+'*73+b']'):
        try:compile_source(oversized,allow_loops=True)
        except ValueError:invalid+=1
        else:raise AssertionError('accepted over-capacity program')
    seeds=0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory(prefix='bf-wide-patch-seeds-') as folder:
            for name in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=Path(folder)/name
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/name),'-o',str(exe)],
                               check=True,capture_output=True)
                for source in (b'[]',b'++++[->+<]>.'):
                    rawslots=bf_native(SLOT_NATIVE,source,'slots')[:-5]
                    m=run_stage('wide_metadata',source)
                    p=run_stage('wide_pairs',m)
                    enc=run_stage('wide_encode',p)
                    payload=bytes([len(source)])+enc+rawslots
                    native=bf_native(PATCH_NATIVE,payload,'patch')
                    interpreted=subprocess.run([str(exe),str(PATCH_SOURCE),'50000000'],input=payload,
                                               capture_output=True,timeout=30,check=True)
                    assert interpreted.stdout==native
                    seeds+=1
    # Atomic install never destroys a previous image on error.
    with tempfile.TemporaryDirectory() as folder:
        srcpath=Path(folder)/'program.bf';target=Path(folder)/'out.elf'
        srcpath.write_bytes(b'[+');target.write_bytes(b'previous')
        result=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),
                              str(srcpath),str(target),'--loops'],capture_output=True)
        assert result.returncode!=0 and target.read_bytes()==b'previous'
        srcpath.write_bytes(b'+'*25+b'[-].')
        result=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),
                              str(srcpath),str(target),'--loops'],capture_output=True)
        assert result.returncode==0,result.stderr
        assert target.read_bytes()==compile_source(srcpath.read_bytes(),allow_loops=True)
    manifest.update({
        'bounded_android_elf_bytes':4192,'maximum_source_commands':74,
        'executed_linux_native_BF_patch_stage':True,
        'programs_simulated':passed,'simulated_bases_per_program':2,
        'relocated_bracket_pairs_total':loops,'traps':traps,
        'linear_path_byte_identical_cases':linear_parity,
        'malformed_and_oversize_rejections':invalid,
        'independent_BF_seed_matches':seeds,
        'atomic_cli_error_preservation':True,
        'compiler_stages_remain_separate_native_Linux_processes':True,
        'general_dynamic_ELF':False,
        'actual_Android_device_execution':False,
        'Android_native_compiler_execution':False,'Android_native_self_hosting':False,
        'Windows_PE32_backend':False,
        'elapsed_seconds':round(time.monotonic()-start,3)
    })
    PATCH_EVIDENCE.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Wide-loop BF ELF pass:',passed,'programs,',loops,'pairs,',invalid,'rejections,',seeds,'seeds')

if __name__=='__main__':main()

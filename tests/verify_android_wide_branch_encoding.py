#!/usr/bin/env python3
"""Independent AArch64 B/conditional-veneer oracle for native BF stage.

This script validates compiled BF output; it does not patch Android images or
perform production machine-code emission. The wide stage is not yet wired into
an Android native executable emitter.
"""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact
from run_android_loops import compile_source
sys.path.insert(0,str(ROOT/'tools'))
from source_check import check_source

BF_SOURCE = ROOT/'experiments/android_wide_branch_encoding.bf'
NATIVE = ROOT/'build/android_wide_branch_encoding_x86_64_linux.elf'
METADATA = ROOT/'build/android_wide_bracket_metadata_x86_64_linux.elf'
PAIRS = ROOT/'build/android_wide_bracket_pairs_x86_64_linux.elf'
EVIDENCE = ROOT/'evidence/iteration28_wide_branch_encoding.json'
B_MAX = (1<<25)-1
MAX_DELTA = (B_MAX-10)//12
NOP = 0xd503201f

def sha(x):return hashlib.sha256(x).hexdigest()

def execute(path,inp,timeout=45):
    r=subprocess.run([str(path)],input=inp,capture_output=True,timeout=timeout)
    assert r.returncode==0 and not r.stderr, (path,r.returncode,r.stderr[:200])
    return r.stdout

def records(pairs):
    return b''.join(b']'+o.to_bytes(3,'little')+c.to_bytes(3,'little') for o,c in pairs)+b'\x00\x00'

def oracle(pairs):
    out=bytearray()
    for o,c in pairs:
        if not (1<=o<c<=0xffffff):return b'\x00\x01'
        span=c-o
        f=12*span+10
        if f>B_MAX:return b'\x00\x04'
        r=10-12*span
        out+=b']'+o.to_bytes(3,'little')+c.to_bytes(3,'little')
        out+=struct.pack('<II', 0x14000000|(f & 0x3ffffff),
                          0x14000000|(r & 0x3ffffff))
    return bytes(out)+b'\x00\x00'

def signed_branch(word):
    assert word>>26 == 0b000101, hex(word)
    n=word & 0x3ffffff
    return n-(1<<26) if n&(1<<25) else n

def verify_veneer(pair,encoded):
    o,c=pair
    tag=encoded[0]
    assert tag==0x5d and encoded[1:4]==o.to_bytes(3,'little')
    assert encoded[4:7]==c.to_bytes(3,'little')
    f,r=struct.unpack_from('<II',encoded,7)
    # Slot starts are 12 instructions apart, and the B is instruction 2.
    assert ((o-1)*12+2)+signed_branch(f)==c*12
    assert ((c-1)*12+2)+signed_branch(r)==o*12
    # Inverted conditional veneer skips two AArch64 instructions: +8 bytes.
    assert (0x35000049 >> 5) & 0x7ffff == 2
    assert (0x34000049 >> 5) & 0x7ffff == 2

def main():
    started=time.monotonic()
    code=BF_SOURCE.read_bytes()
    filtered=check_source(code)
    elf=extract_artifact(execute(ROOT/'build/compiler_x86_64_linux.elf',encode_source(code),timeout=50))
    assert elf==extract_artifact(execute(ROOT/'build/compiler_x86_64_linux.elf',encode_source(filtered),timeout=50))
    assert elf==NATIVE.read_bytes()
    assert len(elf)==215+32*len(filtered)
    rng=random.Random(2026101329)
    pairs=[(1,2),(1,3),(255,257),(65535,65536),(65536,300001),
           (1,300001),(1,1+MAX_DELTA),(1,1+MAX_DELTA-1),
           (0xffffff-500,0xffffff), (255,256), (0xffffff-1,0xffffff)]
    for _ in range(160):
        o=rng.randint(1,0xffffff-1)
        d=rng.randint(1,min(MAX_DELTA,0xffffff-o))
        pairs.append((o,o+d))
    cases=[]
    for pair in pairs:
        raw=execute(NATIVE,records([pair]))
        assert raw==oracle([pair]),(pair,raw.hex(),oracle([pair]).hex())
        verify_veneer(pair,raw[:15])
    for _ in range(34):
        n=rng.randint(1,25)
        sampled=rng.sample(pairs,n)
        raw=execute(NATIVE,records(sampled))
        assert raw==oracle(sampled),sampled
        for i,p in enumerate(sampled):verify_veneer(p,raw[15*i:15*i+15])
    rejected=[]
    for label,inp,result in (
        ('bad_tag',b'[\x01\x00\x00\x02\x00\x00\x00\x00',1),
        ('zero_open',records([(0,2)]),1),
        ('equal',records([(20,20)]),1),
        ('reversed',records([(65537,2)]),1),
        ('beyond_imm26',records([(1,MAX_DELTA+2)]),4),
        ('upstream_error',b'\x00\x03',3),
    ):
        out=execute(NATIVE,inp)
        assert out[-2:]==b'\x00'+bytes([result]),(label,out.hex())
        rejected.append({'case':label,'status':result})
    # Feed true wide BF metadata and pair stages into the native BF encoder.
    program_cases=[b'',b'[]',b'[[]]',b'++[>+<-]>.',
                   b'['+b'+'*299998+b']',b'['*255+b']'*255,
                   b'[]'*4000,b'+'*65536+b'[++]']
    stage_cases=[]
    for program in program_cases:
        metadata=execute(METADATA,program)
        assert metadata[-2:]==b'\x00\x00'
        paired=execute(PAIRS,metadata)
        assert paired[-2:]==b'\x00\x00'
        actual=execute(NATIVE,paired)
        stack=[]; expected_pairs=[]
        for pos,ch in enumerate(program,1):
            if ch==91:stack.append(pos)
            elif ch==93:expected_pairs.append((stack.pop(),pos))
        assert not stack
        assert actual==oracle(expected_pairs),(len(program),actual[:20].hex())
        for i,p in enumerate(expected_pairs):verify_veneer(p,actual[15*i:15*i+15])
        stage_cases.append({'commands':len(program),'pairs':len(expected_pairs),'record_sha256':sha(actual)})
    seeds=0
    with tempfile.TemporaryDirectory(prefix='wide-branch-seeds-') as tmp:
        for src in ('seed_interpreter.c','seed_interpreter_alt.c'):
            exe=Path(tmp)/src
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/src),'-o',str(exe)],check=True,capture_output=True)
            for pair in ((1,2),(255,257)):
                encoded=records([pair])
                p=subprocess.run([str(exe),str(BF_SOURCE),'100000000'],input=encoded,capture_output=True,timeout=35,check=True)
                assert p.stdout==execute(NATIVE,encoded),(src,pair,p.stdout.hex())
                seeds+=1
    evidence={
        'iteration':28,'classification':'EXECUTED_LINUX_NATIVE_BF_LONG_BRANCH_RECORDS_ONLY',
        'source':str(BF_SOURCE.relative_to(ROOT)),
        'native_linux_elf':str(NATIVE.relative_to(ROOT)),
        'source_sha256':sha(code),'filtered_sha256':sha(filtered),
        'brainfuck_instructions':len(filtered),'linux_native_elf_sha256':sha(elf),
        'linux_native_elf_bytes':len(elf),'output_bytes_per_pair':15,
        'aarch64_veneer_instructions':{
            'load':hex(0x39400269), 'open_skip':hex(0x35000049),
            'close_skip':hex(0x34000049), 'unconditional_base':hex(0x14000000)},
        'maximum_supported_bracket_separation':MAX_DELTA,
        'random_and_boundary_valid_pairs':len(pairs),
        'multi_record_cases':34,
        'rejected_cases':rejected,
        'wide_metadata_pair_encoder_cases':stage_cases,
        'independent_bf_seed_checks':seeds,
        'comment_invariance':True,
        'linux_native_selfhost_not_rerun_by_this_test':True,
        'android_native_generated_executables_tested':False,
        'android_native_compiler_selfhosting':False,
        'dynamic_android_elf_emitter_available':False,
        'elapsed_seconds':round(time.monotonic()-started,3)
    }
    EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    # Check optional adapter uses this BF pass without changing old images.
    parity=[]
    for program in (b'',b'[]',b'[[]]',b'++[>+<-]>.',b'+,.,',b'[-][-]'):
        original=compile_source(program,check_hashes=True,source_filter='scan',wide_brackets=True)
        branch=compile_source(program,check_hashes=True,source_filter='scan',wide_branches=True)
        assert original==branch
        parity.append(sha(branch))
    evidence['bounded_android_elf_byte_identical_cases']=len(parity)
    evidence['bounded_android_elf_sha256']=parity
    EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    print('BF wide branch encoding validated',len(pairs),'pairs,',len(stage_cases),
          'source stage cases,',len(parity),'bounded ELFs,',seeds,'independent BF seeds')

if __name__=='__main__':main()

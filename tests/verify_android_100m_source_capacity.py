#!/usr/bin/env python3
"""Correctness of BF-owned 32-bit parsing, NOT 100M native compilation."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from source_check import check_source
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact
from android_100m_transport import compress_bytes, scan_file

BF=ROOT/'experiments/android_100m_rle_scan.bf'
NATIVE=ROOT/'build/android_100m_rle_scan_x86_64_linux.elf'
COMPILER=ROOT/'build/compiler_x86_64_linux.elf'
ALPHABET=b'><+-.,[]'


def enc_runs(runs, mode=0):
    return bytes([mode])+b''.join(struct.pack('<IB',size,byte) for size,byte in runs)+b'\x00'*4


def oracle(raw, mode=0):
    n=depth=0; bad=False; ev=bytearray()
    for byte in raw:
        if byte not in ALPHABET:continue
        if byte==91:
            if mode: ev.extend(b'['+struct.pack('<I',n))
            depth+=1
        elif byte==93:
            if mode: ev.extend(b']'+struct.pack('<I',n))
            depth-=1
            if depth<0:bad=True
        n+=1
    return bytes(ev)+struct.pack('<IIB',n,depth&0xffffffff,int(bad or depth!=0))


def execute(wire):
    p=subprocess.run([str(NATIVE)],input=wire,capture_output=True,timeout=30)
    assert p.returncode==0 and not p.stderr, (p.returncode,p.stderr[:100])
    assert len(p.stdout)>=9
    return p.stdout


def main():
    t=time.monotonic()
    source=BF.read_bytes()
    filtered=check_source(source)
    assert len(filtered)<16128,len(filtered)
    exe=extract_artifact(subprocess.run([str(COMPILER)],input=encode_source(source),
                                         capture_output=True,check=True,timeout=60).stdout)
    assert exe==NATIVE.read_bytes(), 'canonical BF compilation disagrees with installed native'
    stripped=extract_artifact(subprocess.run([str(COMPILER)],input=encode_source(filtered),
                                              capture_output=True,check=True,timeout=60).stdout)
    assert exe==stripped
    fixed=[b'',b'++[-]',b'[[]]',b']',b'[[',b']][',b'foobar plus not BF',
           bytes(range(256)),b'\0\xff ignored<--> test [>+<-]>.',
           b'['*255+b']'*255,b'+'*1000+b'[>+<-]']
    rng=random.Random(100000047)
    fixed.extend(rng.randbytes(rng.randrange(0,1500)) for _ in range(65))
    tests=0; transports=0
    for raw in fixed:
        for mode in (0,1):
            wire=io.BytesIO();compress_bytes(io.BytesIO(raw),wire,mode=mode)
            # Verify the generic transport reconstructs identical original bytes.
            encoded=wire.getvalue(); offset=1;decoded=bytearray()
            while True:
                n=int.from_bytes(encoded[offset:offset+4],'little');offset+=4
                if n==0:break
                b=encoded[offset];offset+=1
                decoded.extend(bytes([b])*n)
            assert bytes(decoded)==raw and offset==len(encoded)
            assert execute(encoded)==oracle(raw,mode),(raw[:100],mode)
            tests+=1;transports+=1
    # True 32-bit offsets and carry, without any per-command host decoding.
    n=100_000_000
    cases={
       'hundred_million_plus': ([(n,ord('+'))],0,struct.pack('<IIB',n,0,0)),
       'far_brackets': ([(1,91),(n,43),(1,93)],1,
                         b'['+struct.pack('<I',0)+b']'+struct.pack('<I',n+1)+struct.pack('<IIB',n+2,0,0)),
       'fifty_million_nested': ([(n//2,91),(n//2,93)],0,struct.pack('<IIB',n,0,0)),
       'ignored_raw_100m': ([(n,ord('A')),(17,ord('+'))],0,struct.pack('<IIB',17,0,0)),
       'count_overflow': ([(0xffffffff,ord('+')),(1,ord('+'))],0,struct.pack('<IIB',0,0,2)),
       'depth_underflow': ([(n,93)],0,struct.pack('<IIB',n,(-n)&0xffffffff,1)),
    }
    summaries=[]
    for name,(runs,mode,expected) in cases.items():
        start=time.monotonic();result=execute(enc_runs(runs,mode));assert result==expected,(name,result.hex(),expected.hex())
        summaries.append(dict(name=name,encoded_input_bytes=len(enc_runs(runs,mode)),
                              represented_raw_bytes=sum(n for n,_ in runs),
                              output_sha256=hashlib.sha256(result).hexdigest(),
                              native_seconds=round(time.monotonic()-start,4)))
    # Generate an actual 100MB raw-source file and run the transport in bounded memory.
    with tempfile.TemporaryDirectory(prefix='android100m-') as td:
        big=Path(td)/'hundred_million_real_source.bf'
        chunk=b'+'*(1<<20)
        with big.open('wb') as f:
            for _ in range(n//len(chunk)):f.write(chunk)
            f.write(b'+'*(n%len(chunk)))
        assert big.stat().st_size==n
        start=time.monotonic();actual=scan_file(big,emit_positions=False)
        assert actual['filtered_commands']==n and actual['raw_bytes']==n and actual['verified_balanced']
        real_case=dict(real_raw_file_bytes=n,real_raw_file_transport_seconds=round(time.monotonic()-start,3),
                       source_spooled_to_disk=True,backend_native_generation=False)
    # Independent standard BF seeds on a small case; source is BF, not a foreign compiler.
    independent=0
    with tempfile.TemporaryDirectory(prefix='android100m-seed-') as td:
        for seed in ('seed_interpreter.c','seed_interpreter_alt.c'):
            exe_seed=Path(td)/seed
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/seed),'-o',str(exe_seed)],check=True,capture_output=True)
            sample=enc_runs([(1,91),(23,ord('+')),(1,93)],mode=1)
            p=subprocess.run([str(exe_seed),str(BF),'150000000'],input=sample,capture_output=True,check=True,timeout=50)
            assert p.stdout==execute(sample),(seed,p.stdout.hex())
            independent+=1
    evidence=dict(iteration=47,classification='EXECUTED_LINUX_BF_100M_RLE_SOURCE_ANALYSIS_ONLY',
      source='experiments/android_100m_rle_scan.bf',filtered_instructions=len(filtered),
      source_sha256=hashlib.sha256(source).hexdigest(),
      filtered_sha256=hashlib.sha256(filtered).hexdigest(),
      native='build/android_100m_rle_scan_x86_64_linux.elf',
      native_sha256=hashlib.sha256(exe).hexdigest(), native_bytes=len(exe),
      ordinary_differential_cases=tests,transport_roundtrip_cases=transports,
      independent_seed_checks=independent, virtual_run_cases=summaries,
      real_raw_input_stress=real_case, complete_native_100m_compilation=False,
      android_target_native_execution=False, android_shared_library=False,
      app_policy_native_compilation=False, elapsed_seconds=round(time.monotonic()-t,3))
    (ROOT/'evidence/iteration47_android_100m_source.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('PASS',tests,'differential cases,',len(cases),'32-bit/RLE boundary cases,',independent,'seed comparisons; real 100MB transport',real_case)

if __name__=='__main__': main()

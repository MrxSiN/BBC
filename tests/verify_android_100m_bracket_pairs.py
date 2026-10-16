#!/usr/bin/env python3
"""Verify BF pairing at 32-bit offsets and 100M span. No machine-code output."""
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from source_check import check_source
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact
from android_100m_transport import compress_bytes
from android_100m_pair_transport import pair_file

SCANNER=ROOT/'build/android_100m_rle_scan_framed_x86_64_linux.elf'
PAIRER=ROOT/'build/android_100m_bracket_pairs_x86_64_linux.elf'
ORIGINAL=ROOT/'build/android_100m_rle_scan_x86_64_linux.elf'
ALPHABET=b'><+-.,[]'


def run(bin:Path,data:bytes,timeout=30):
    p=subprocess.run([str(bin)],input=data,capture_output=True,timeout=timeout)
    assert p.returncode==0 and not p.stderr,(bin.name,p.returncode,p.stderr[:200])
    return p.stdout


def oracle(src:bytes):
    stack=[];pairs=[];offset=0;bad=False
    for b in src:
        if b not in ALPHABET: continue
        if b==91:
            if len(stack)==255:bad=True
            else:stack.append(offset)
        elif b==93:
            if not stack: bad=True
            else:pairs.append((stack.pop(),offset))
        offset+=1
    if bad or stack:return None
    return b''.join(b']'+struct.pack('<II',*p) for p in pairs)+b'\0\0'


def wire(src:bytes):
    out=io.BytesIO();compress_bytes(io.BytesIO(src),out,mode=1)
    return out.getvalue()


def sha(s):return hashlib.sha256(s).hexdigest()


def main():
    begun=time.monotonic();stages={}
    for kind,src,elf in (
      ('framed_scanner','experiments/android_100m_rle_scan_framed.bf',SCANNER),
      ('wide_pairing','experiments/android_100m_bracket_pairs.bf',PAIRER)):
        data=(ROOT/src).read_bytes();filtered=check_source(data)
        assert len(filtered)<=16128
        native=extract_artifact(run(ROOT/'build/compiler_x86_64_linux.elf',encode_source(data)))
        assert native==elf.read_bytes()
        assert native==extract_artifact(run(ROOT/'build/compiler_x86_64_linux.elf',encode_source(filtered)))
        stages[kind]={'bf_source':src,'brainfuck_instructions':len(filtered),
            'source_sha256':sha(data),'filtered_sha256':sha(filtered),
            'native_linux_elf_sha256':sha(native),'native_linux_elf_bytes':len(native)}
    rng=random.Random(481000000)
    valid=[b'',b'[]',b'[[]]',b'[-]',b'+'*99+b'[->+<]',b'[]'*100,
           b'['*255+b']'*255,b'+'*100+b'[[]]' +b'.',
           b'A\x00[]\xff[]ignored',b'['+b'+'*8000+b']',b'+'*999+b'[+][-]']
    invalid=[b'[',b']',b'][',b'[[[]]',b'['*256+b']'*256,b']'*4,b'[+]][']
    for _ in range(135):
        text=bytearray();depth=0
        for j in range(rng.randrange(0,280)):
            choices=b'><+-.,'+(b'[' if depth<32 else b'')+(b']' if depth else b'')
            c=rng.choice(choices);text.append(c)
            depth+=int(c==91)-int(c==93)
        text.extend(b']'*depth)
        valid.append(bytes(text))
    for _ in range(20):
        text=bytes(rng.choice(b'][+') for j in range(rng.randrange(1,120)))
        if oracle(text) is None: invalid.append(text)
    counts={'valid':0,'invalid':0,'original_scanner_parity':0}
    for src in valid+invalid:
        data=wire(src)
        original=run(ORIGINAL,data)
        framed=run(SCANNER,data)
        assert framed==original[:-9]+b'\x00'+original[-9:]
        counts['original_scanner_parity']+=1
        output=run(PAIRER,framed)
        expected=oracle(src)
        if src in invalid:
            assert expected is None and output[-1]!=0,(src[:100],output[-12:])
            counts['invalid']+=1
        else:
            assert output==expected,(src[:100],output[:100],expected[:100])
            counts['valid']+=1
    # 100,000,002 command source with positions above 32 bit signed range
    n=100_000_000
    enc=b'\x01'+struct.pack('<IB',1,91)+struct.pack('<IB',n,43)+struct.pack('<IB',1,93)+b'\0'*4
    events=run(SCANNER,enc)
    far=run(PAIRER,events)
    assert far==b']'+struct.pack('<II',0,n+1)+b'\0\0',far.hex()
    # 255-deep stack accepted; 256 rejected
    accepted=b'['*255+b']'*255
    rejected=b'['*256+b']'*256
    assert run(PAIRER,run(SCANNER,wire(accepted)))[-1]==0
    assert run(PAIRER,run(SCANNER,wire(rejected)))[-1]==3
    # The byte transport works on a real 100MB source file
    with tempfile.TemporaryDirectory(prefix='bf100m-pair-') as folder:
        p=Path(folder)/'real100m.bf'; output=Path(folder)/'pairs.bin'
        with p.open('wb') as f:
            f.write(b'[')
            for _ in range(95):f.write(b'+'*(1<<20))
            f.write(b'+'*(n-95*(1<<20)))
            f.write(b']')
        result=pair_file(p,pairs_path=output)
        assert result['raw_bytes']==n+2 and result['pair_records']==1
        assert output.read_bytes()==far
        output.write_bytes(b'kept')
        bad=Path(folder)/'bad.bf';bad.write_bytes(b'['*256+b']'*256)
        try:pair_file(bad,pairs_path=output)
        except ValueError:pass
        else:raise AssertionError('overflow was accepted')
        assert output.read_bytes()==b'kept'
    # Two independent conforming BF interpreters: small representative cases
    seed_matches=0
    with tempfile.TemporaryDirectory(prefix='bf100m-pair-seeds-') as folder:
        for interpreter in ('seed_interpreter.c','seed_interpreter_alt.c'):
            exe=Path(folder)/interpreter
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/interpreter),'-o',str(exe)],
                           check=True,capture_output=True)
            for src in (b'[]',b'[[]]',b'++[-]'):
                data=wire(src)
                framed=run(SCANNER,data)
                native=run(PAIRER,framed)
                p=subprocess.run([str(exe),str(ROOT/'experiments/android_100m_bracket_pairs.bf'),
                                  '30000000'],input=framed,capture_output=True,check=True,timeout=25)
                assert p.stdout==native
                seed_matches+=1
    result={'iteration':48,'date':'2026-10-13','classification':'EXECUTED_LINUX_BF_32BIT_PAIRING_NOT_NATIVE_ANDROID_CODEGEN',
            'stages':stages,'tests':counts,'hundred_million_far_pair':True,
            'real_raw_source_bytes':n+2,'real_raw_source_bracket_pairs':1,
            'max_nesting_supported':255,'nesting_depth_256_rejected':True,
            'independent_seed_comparisons':seed_matches,'input_output_preservation':True,
            'android_native_codegen_max_commands':2719,'android_100m_native_compilation':'UNIMPLEMENTED',
            'elapsed_seconds':round(time.monotonic()-begun,3)}
    dst=ROOT/'evidence/iteration48_android_100m_pairing.json'
    dst.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

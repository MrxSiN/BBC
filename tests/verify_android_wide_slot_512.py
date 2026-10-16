#!/usr/bin/env python3
"""Independent test oracle for the BF-authored 512-position relocation stage."""
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
from transport import encode_source, extract_artifact
from source_check import check_source
from run_android_extended import (compile_source, bf_native, WIDE_512_SOURCE,
    WIDE_512_NATIVE, WIDE_512_EVIDENCE, SLOT_NATIVE, check_provenance)
from run_android_loops import run_stage
from verify_android_aarch64_subset import emulate
from reference import execute


def sha(data): return hashlib.sha256(data).hexdigest()


def bracket_pairs(program):
    stack=[]; pairs=[]
    for p,command in enumerate(program,1):
        if command==ord('['): stack.append(p)
        elif command==ord(']'):
            assert stack
            pairs.append((stack.pop(),p))
    assert not stack
    return pairs


def verify_words(program,image):
    for opening,closing in bracket_pairs(program):
        span=closing-opening
        for pos,value in ((opening,0x14000000|((12*span+10)&0x3ffffff)),
                          (closing,0x14000000|((10-12*span)&0x3ffffff))):
            off=0x210+48*(pos-1)+8
            assert image[off:off+4] == struct.pack('<I',value),(opening,closing,pos)
    return len(bracket_pairs(program))


def main():
    start=time.monotonic()
    filtered=check_source(WIDE_512_SOURCE.read_bytes())
    assert len(filtered)<16128
    installed=WIDE_512_NATIVE.read_bytes()
    compiler=ROOT/'build/compiler_x86_64_linux.elf'
    for candidate in (WIDE_512_SOURCE.read_bytes(),filtered):
        r=subprocess.run([str(compiler)],input=encode_source(candidate),
              capture_output=True,timeout=55,check=True)
        assert extract_artifact(r.stdout)==installed
    check_provenance(allow_loops=True,page_class=True)
    cases=[b'',b'[]',b'+[-].',b'+[>+<-]>.',b'<' + b'+'*330+b'[-]',
           b'['+b']'*1+b'.', b'+'*255+b'[-].', b'+'*254+b'[->+<]>.',
           b'+'*327+b'[-].', b'+'*328+b'[-].', b'+'*329+b'[-].',
           b'+'*509+b'[-]', b'[]'*256,b'['*255+b']'*255,
           b'+'*300+b'[>+<-]'+b'.'*6,b','*331+b'[-].',b'+'*512,
           b'+'*330+b'[-].',b'+'*331+b'[->+<]>.']
    rng=random.Random(2026101333)
    chunks=[b'+[-]',b'[-]',b'[[-]]',b'+[>+<-]',b'++[->+<]',b'+-.',b'>+<',b'[-].',b'.,']
    for _ in range(47):
        target=rng.randint(260,512); buf=bytearray()
        while len(buf)<target:
            item=rng.choice(chunks)
            if len(buf)+len(item)>target:
                break
            buf.extend(item)
        cases.append(bytes(buf))
    verified=0; pairs=0; simulated=0; trapped=0;class_2=0;linear_parity=0
    for program in cases:
        if len(program)>512: continue
        loops=b'[' in program or b']' in program
        image=compile_source(program,allow_loops=loops,page_class=True)
        assert image[:4]==b'\x7fELF'
        if len(program)>330:
            class_2+=1;assert len(image)==32864
        else: assert len(image)==16480
        pairs+=verify_words(program,image)
        if not loops:
            assert image==compile_source(program,page_class=True)
            linear_parity+=1
        input_data=bytes((v*31+7)%256 for v in range(640))
        try:
            expected,_=execute(program,input_data,max_steps=100000)
            trap=False
        except IndexError:
            expected=None;trap=True;trapped+=1
        except TimeoutError:
            raise AssertionError(f'nonterminating or over-budget fixture of {len(program)} commands')
        for bias in (0,0x40000000):
            result,status,_=emulate(image,bias,tape_base_rva=0x10060,
               code_limit=0x220+48*len(program), input_bytes=input_data,
               max_steps=100000)
            if trap: assert status==2,(len(program),status)
            else: assert (result,status)==(expected,0),(len(program),result,status,expected)
            simulated+=1
        verified+=1
    assert class_2>0 and pairs>0 and verified>=50
    rejects=0
    for program in (b'+'*511+b'[]', b'['+b'+'*511+b']',b'['*256+b']'*256,
                    b']'+b'+'*330, b'['+b'+'*330):
        try:compile_source(program,allow_loops=True,page_class=True)
        except ValueError:rejects+=1
        else:raise AssertionError('invalid or over-capacity source accepted')
    # Preserve the destination on rejected sources.
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);src=root/'source.bf';dst=root/'program.elf'
        src.write_bytes(b'+'*511+b'[]');dst.write_bytes(b'unchanged')
        args=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),
              str(src),str(dst),'--page-class','--loops']
        r=subprocess.run(args,capture_output=True,timeout=45)
        assert r.returncode and dst.read_bytes()==b'unchanged'
        src.write_bytes(b'+'*328+b'[-].')
        r=subprocess.run(args,capture_output=True,timeout=45)
        assert r.returncode==0,r.stderr
        assert dst.read_bytes()==compile_source(src.read_bytes(),allow_loops=True,page_class=True)
        if shutil.which('readelf'):
            ph=subprocess.run(['readelf','-Wl',str(dst)],capture_output=True,text=True,check=True).stdout
            assert 'Requesting program interpreter: /system/bin/linker64' in ph
            assert 'LOAD' in ph
    independent=0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as folder:
            for file in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=Path(folder)/file
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/file),'-o',str(exe)],
                       capture_output=True,check=True)
                for program in (b'[]', b'+[-].'):
                    slots=bf_native(SLOT_NATIVE,program,'slots')[:-5]
                    records=run_stage('wide_encode',run_stage('wide_pairs',
                           run_stage('wide_metadata',program)))
                    payload=len(program).to_bytes(2,'little')+records+slots
                    interpreted=subprocess.run([str(exe),str(WIDE_512_SOURCE),'75000000'],
                           input=payload,capture_output=True,timeout=60,check=True).stdout
                    native=bf_native(WIDE_512_NATIVE,payload,'patch')
                    assert interpreted==native
                    independent+=1
    evidence=json.loads(WIDE_512_EVIDENCE.read_text())
    evidence['verified']={'source_variants_compiled_identically':2,
       'programs_checked':verified,'bracket_pairs_checked':pairs,
       'simulated_executions':simulated,'size_class_two_programs':class_2,
       'linear_parity':linear_parity,'pointer_traps':trapped,
       'expected_rejections':rejects,'independent_seed_matches':independent,
       'atomic_output_on_rejection':True,'readelf_checked':bool(shutil.which('readelf')),
       'elapsed_seconds':round(time.monotonic()-start,3)}
    WIDE_512_EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    print('512-slot BF patch PASS',evidence['verified'])

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Iteration 45 Android BF-owned eighth size class and ADRP carry checks.

This runs Linux-native BF compiler stages and AArch64 simulation only.
It does not establish execution by an Android loader or self-hosting at this size.
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
from run_android_extended import (compile_source, bf_native, check_provenance,
    CLASS8_NATIVE, CLASS8_SOURCE, CLASS8_EVIDENCE)
from reference import execute
from verify_android_aarch64_subset import emulate
from source_check import check_source
from transport import encode_source, extract_artifact


def digest(x): return hashlib.sha256(x).hexdigest()


def make_case(n, tail):
    assert len(tail) <= n
    return b'+' * (n-len(tail)) + tail


def check_image(image, n):
    rx_end = 0x220 + 48*n
    aligned = (rx_end+0x3fff) & ~0x3fff
    assert image[:4] == b'\x7fELF'
    assert len(image) == aligned+96, (n,len(image),aligned)
    ph = [struct.unpack_from('<IIQQQQQQ', image, 64+56*i) for i in range(5)]
    assert [x[0] for x in ph] == [6,3,1,1,2]
    rx, rw, dyn = ph[2:]
    assert rx[1] == 5 and rx[2:7] == (0,0,0,rx_end,rx_end)
    assert rw[1] == 6 and rw[2:7] == (aligned,aligned,aligned,96,65632)
    assert dyn[2:7] == (aligned,aligned,aligned,96,96)
    assert rx[7] == rw[7] == 0x4000
    assert rx_end <= aligned
    assert struct.unpack_from('<I',image,0x200)[0] == 0x90000014+(aligned//0x4000)*0x20
    assert image[rx_end:aligned] == bytes(aligned-rx_end)
    return aligned


def count_pairs(source, img):
    stack=[]; paired=0
    for pos, c in enumerate(source,1):
        if c == 91: stack.append(pos)
        elif c == 93:
            opening=stack.pop()
            delta=pos-opening
            for slot, word in ((opening,0x14000000|((12*delta+10)&0x3ffffff)),
                               (pos,0x14000000|((10-12*delta)&0x3ffffff))):
                offset = 0x210 + 48*(slot-1)+8
                assert struct.unpack_from('<I',img,offset)[0] == word,(len(source),slot)
            paired+=1
    assert not stack
    return paired


def main():
    t=time.monotonic()
    proof=json.loads(CLASS8_EVIDENCE.read_text())
    source=CLASS8_SOURCE.read_bytes()
    stream=check_source(source)
    native=CLASS8_NATIVE.read_bytes()
    assert len(stream)==proof['bf_instruction_count']
    assert (digest(source),digest(stream),digest(native))==(proof['source_sha256'],proof['filtered_sha256'],proof['native_linux_elf_sha256'])
    assert len(native)==215+32*len(stream)
    check_provenance(allow_loops=True,multiclass=True,tape_relocated=True)
    compiled=0
    for src in (source,stream):
        process=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
            input=encode_source(src), capture_output=True, check=True, timeout=45)
        assert extract_artifact(process.stdout)==native
        compiled+=1

    cases=[(n,make_case(n,b'[-].')) for n in
           (2000,2036,2037,2038,2377,2378,2379,2380,2399,2400,2559,2560,2699,2718,2719)]
    cases.extend([
       (2379,b'['+b'+'*2377+b']'),
       (2719,b'['+b'+'*2717+b']'),
       (2719,make_case(2719,b'[->+<]>.')),
       (2719,make_case(2719,b'++[>++[>+<-]<-]>>.')),
       (2719,make_case(2719,b'[-][].')),
       (2719,make_case(2719,b',.[-].')),
       (2400,b'<' + b'+'*2399),
       (2719,b'<' + b'+'*2718),
       (2719,b'>'*2718+b'<'),
       (2719,b'+'*2718+b'.'),
    ])
    rng=random.Random(4502719)
    tails=(b'[->+<]>.',b'[-].',b'++[>+<-]>.',b'[-][]',b',.',b'.')
    for _ in range(10):
        n=rng.randrange(2380,2720)
        cases.append((n,make_case(n,rng.choice(tails))))

    counts=0;loops=0;simulations=0;traps=0;class8=0
    inputs=bytes(range(256))*12
    for n,program in cases:
        assert len(program)==n
        image=compile_source(program,allow_loops=b'[' in program,
            multiclass=True,tape_relocated=True)
        aligned=check_image(image,n)
        assert aligned==0x20000 if n>=2379 else aligned<=0x1c000
        if n>=2379:class8+=1
        loops+=count_pairs(program,image)
        try:
            expected,_=execute(program, inputs,max_steps=500000)
            trap=False
        except IndexError:
            expected=b'';trap=True;traps+=1
        for bias in (0,0x40000000):
            actual,status,_=emulate(image,bias,input_bytes=inputs,
                tape_base_rva=aligned+0x60, code_limit=0x220+48*n,
                max_steps=500000)
            if trap:
                assert status==2,(n,status)
            else:
                assert (actual,status)==(expected,0),(n,actual[:30],expected[:30],status)
            simulations+=1
        counts+=1

    # Compare standard-BF interpreter and native BF stage on the same full ELF.
    test=compile_source(make_case(2400,b'[-].'),allow_loops=True,multiclass=True,tape_relocated=True)
    before=bytearray(test)
    assert before[0x201]==1
    before[0x201]=0
    after=bf_native(CLASS8_NATIVE,bytes(before),'class8')
    assert after==test+b'\0\0'
    independent,steps=execute(source,bytes(before),max_steps=2_000_000)
    assert independent==after
    assert after[:0x201]==before[:0x201]
    assert after[0x202:-2]==before[0x202:]

    rejects=0
    for program,kwargs in (
        (b'+'*2720,{}),
        (b'+'*2717+b'[-].',{}),
        (b'['+b'+'*2718,{}),
        (b'['*256+b']'*256,{}),
        (b'+'*2380,{'tape_relocated':False}),
    ):
        settings={'multiclass':True,'tape_relocated':True,'allow_loops':True}
        settings.update(kwargs)
        try: compile_source(program,**settings)
        except ValueError: rejects+=1
        else: raise AssertionError('unsupported source accepted')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        src=td/'input.bf';out=td/'output.elf'
        cli=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(src),str(out),
             '--multiclass','--tape-relocated','--loops']
        src.write_bytes(b'+'*2720);out.write_bytes(b'keep-original')
        res=subprocess.run(cli,capture_output=True,timeout=45)
        assert res.returncode != 0 and out.read_bytes()==b'keep-original'
        src.write_bytes(make_case(2719,b'[-].'))
        res=subprocess.run(cli,capture_output=True,timeout=45)
        assert res.returncode == 0,res.stderr
        assert check_image(out.read_bytes(),2719)==0x20000
        if shutil.which('readelf'):
            p=subprocess.run(['readelf','-l',str(out)],capture_output=True,check=True)
            assert b'LOAD' in p.stdout and b'DYNAMIC' in p.stdout
    # Preserve the historically verified 2000-slot example byte-for-byte.
    original=ROOT/'build/android_wide_2000_loop_aarch64.elf'
    if original.exists():
        p=ROOT/'examples/android_2000_loop_demo.bf'
        assert compile_source(p.read_bytes(),allow_loops=True,multiclass=True,tape_relocated=True)==original.read_bytes()
    output={'classification':'EXECUTED_LINUX_NATIVE_BF_AND_SIMULATED_AARCH64_NOT_ANDROID_DEVICE',
            'programs_checked':counts,'class8_programs':class8,'simulated_runs':simulations,
            'bracket_pairs_checked':loops,'expected_trap_programs':traps,
            'rejected_invalid_or_overlimit':rejects,'native_selfcompile_bf_variants':compiled,
            'independent_BF_interpreter_stage_steps':steps,
            'atomic_output_preservation':True,'readelf':bool(shutil.which('readelf')),
            'android_device_run':False,'universal_300000_command_goal':False,
            'elapsed_seconds':round(time.monotonic()-t,3)}
    print(json.dumps(output,indent=2))
    return output


if __name__=='__main__':main()

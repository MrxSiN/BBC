#!/usr/bin/env python3
"""Executed BF-native source-to-74-slot ELF regression with emulator oracle."""
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'), str(ROOT/'tools'),str(ROOT/'tests')]
from run_android_extended import compile_source, bf_native, SLOT_NATIVE, WRAP_NATIVE, SLOT_SOURCE, WRAP_SOURCE
from run_android_loops import compile_source as bounded_legacy
from verify_android_aarch64_subset import emulate, TEMPLATES, NOP, PACK
from reference import execute
from source_check import check_source
from transport import encode_source, extract_artifact

EVIDENCE=ROOT/'evidence/iteration29_extended_slots.json'
COMPILER=ROOT/'build/compiler_x86_64_linux.elf'

def sha(data):return hashlib.sha256(data).hexdigest()


def validate_image(image, source):
    assert len(image)==4192 and image[:4]==b'\x7fELF'
    old=bounded_legacy(b'',check_hashes=False)
    assert image[:0x210]==old[:0x210]
    assert image[0x1000:]==old[0x1000:]
    assert image[0xff0:0xffc]==PACK([0xd2800000,0xd2800ba8,0xd4000001])
    assert image[0xffc:0x1000]==PACK([NOP])
    for i,b in enumerate(source):
        assert image[0x210+i*48:0x210+(i+1)*48]==TEMPLATES[b]
    assert image[0x210+48*len(source):0xff0]==PACK([NOP]*(12*(74-len(source))))
    # PT_LOAD align and flags inherited from known verified ELF header
    phdrs=[struct.unpack_from('<IIQQQQQQ',image,64+56*i) for i in range(5)]
    assert [p[0] for p in phdrs]==[6,3,1,1,2]
    assert (phdrs[2][1],phdrs[2][5],phdrs[2][7])==(5,4096,16384)
    assert (phdrs[3][1],phdrs[3][5],phdrs[3][7])==(6,96,16384)


def main():
    start=time.monotonic()
    stages={}
    for name,src,binary in [('slots',SLOT_SOURCE,SLOT_NATIVE),('elf',WRAP_SOURCE,WRAP_NATIVE)]:
        source=src.read_bytes(); filtered=check_source(source)
        assert len(filtered)<=16128
        proc=subprocess.run([str(COMPILER)],input=encode_source(source),capture_output=True,timeout=65,check=True)
        assert extract_artifact(proc.stdout)==binary.read_bytes()
        proc=subprocess.run([str(COMPILER)],input=encode_source(filtered),capture_output=True,timeout=65,check=True)
        assert extract_artifact(proc.stdout)==binary.read_bytes()
        assert len(binary.read_bytes())==215+32*len(filtered)
        stages[name]={'source':str(src.relative_to(ROOT)), 'source_sha256':sha(source),
                      'filtered_sha256':sha(filtered),'bf_commands':len(filtered),
                      'native_linux_elf':str(binary.relative_to(ROOT)),
                      'native_linux_elf_sha256':sha(binary.read_bytes()),
                      'native_linux_elf_bytes':len(binary.read_bytes())}
    # Create the manifest prior to using the CLI's strict provenance checks.
    EVIDENCE.write_text(json.dumps({'stages':stages},indent=2)+'\n')
    rng=random.Random(2026101329)
    cases=[b'',b'+'*11+b'.',b'+'*20+b'.',b'+'*73+b'.',b'+'*74,
           b'>'+b'+'*25+b'.',b','*40+b'.',b'>'*73+b'.',b'-'*73+b'.',b'>+<.']
    alphabet=b'+-.<>, '
    for _ in range(75):
        n=rng.randint(0,74)
        p=bytes(rng.choice(alphabet) for i in range(n))
        cases.append(p)
    tested=0;expected_traps=0;legacy_slots=0
    for src in cases:
        filtered=bytes(b for b in src if b in b'+-.<>,')
        if len(filtered)>74: continue
        image=compile_source(src,check_hashes=True)
        validate_image(image,filtered)
        program_input=bytes((i*107+13)&255 for i in range(120))
        reference_out=None;reference_trap=False
        try:
            reference_out,_=execute(filtered,program_input,max_steps=15000)
        except IndexError:
            reference_trap=True
        for bias in (0,0x40000000):
            out,status,steps=emulate(image,bias,input_bytes=program_input,max_steps=1200)
            if reference_trap:
                assert status==2,(src,status)
            else:
                assert (out,status)==(reference_out,0),(src,out,status,reference_out)
        if reference_trap:expected_traps+=1
        if len(filtered)<=10:
            legacy_slots+=1
            old=bounded_legacy(filtered,check_hashes=False)
            assert image[:0x210+48*len(filtered)]==old[:0x210+48*len(filtered)]
        tested+=1
    for n in (0,1,10,74,75,100,255):
        output=bf_native(WRAP_NATIVE,bytes([n])+(b'\0'*48*n if n<=74 else b''),'elf')
        assert (len(output)==4194 and output[-2:]==b'\0\0') if n<=74 else output==b'\0\x01'
    for raw in (b'[]',b'[+]',b'+[->+<]>.',b'[',b']',b'+[]'*7):
        try:compile_source(raw,check_hashes=True)
        except ValueError as e: assert 'bracket' in str(e).lower(),str(e)
        else:raise AssertionError(f'accepted unrelocated bracket source: {raw!r}')
    for raw in (b'+'*75,b'+'*100,b'+'*256):
        try:compile_source(raw,check_hashes=True)
        except ValueError as e: assert '74 commands' in str(e)
        else:raise AssertionError('over-limit accepted')
    for n in (0,1,10,74,255,256,257,1024):
        payload=bf_native(SLOT_NATIVE,b'+'*n,'slots')
        assert len(payload)==48*n+5 and payload[-5:]==n.to_bytes(3,'little')+b'\0\0'
        assert payload[:48]==TEMPLATES[ord('+')] if n else payload==b'\0'*5
    assert bf_native(SLOT_NATIVE,b'[]','slots')[-1]==3
    assert bf_native(SLOT_NATIVE,b'?','slots')[-1]==1
    independent_seed_checks=0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as temp:
            for seed in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=Path(temp)/seed
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/seed),'-o',str(exe)],
                               capture_output=True,check=True)
                for src, payload, native in ((SLOT_SOURCE,b'+',SLOT_NATIVE),
                                             (SLOT_SOURCE,b'[]',SLOT_NATIVE),
                                             (WRAP_SOURCE,b'\x00',WRAP_NATIVE)):
                    reference=subprocess.run([str(exe),str(src),'100000000'],input=payload,
                                             capture_output=True,check=True,timeout=35)
                    assert reference.stdout==bf_native(native,payload,'seeds')
                    independent_seed_checks+=1
    # The artifact already exists only after both native BF stages succeeded.
    with tempfile.TemporaryDirectory() as temp:
        target=Path(temp)/'out.elf';source=Path(temp)/'input.bf'
        target.write_bytes(b'original');source.write_bytes(b'[]')
        r=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(source),str(target)],capture_output=True,text=True)
        assert r.returncode!=0 and target.read_bytes()==b'original'
        source.write_bytes(b'+'*20+b'.')
        r=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(source),str(target)],capture_output=True,text=True)
        assert r.returncode==0,r.stderr
        assert target.read_bytes()==compile_source(source.read_bytes(),check_hashes=True)
    evidence={
        'iteration':29,
        'classification':'EXECUTED_LINUX_NATIVE_BF_74_SLOT_ANDROID_ELF_SIMULATED_NOT_ANDROID_DEVICE',
        'stages':stages,'max_compiled_commands_without_brackets':74,
        'machine_slot_bytes':48,'extended_elf_bytes':4192,
        'linear_source_emulator_cases':tested,'two_load_biases_per_case':True,
        'expected_pointer_traps':expected_traps,
        'legacy_prefix_parity_cases':legacy_slots,
        'slot_counter_boundaries':[0,1,10,74,255,256,257,1024],
        'bracket_rejection_cases':6,'overlimit_rejection_cases':3,
        'wrapper_length_rejection_cases':[75,100,255],
        'comment_invariance':True,'cli_atomic_preserve_and_success':True,
        'independent_bf_interpreter_checks':independent_seed_checks,
        'native_android_device_executed':False,
        'android_native_compiler_selfhosting':False,
        'windows_native_target':False,
        'dynamic_executable_size':False,
        'general_loop_relocation_in_elf':False,
        'elapsed_seconds':round(time.monotonic()-start,3)
    }
    EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    print('Iteration 29 pass',tested,'emulated ELF cases',expected_traps,'pointer traps',legacy_slots,'legacy comparisons')

if __name__=='__main__':main()

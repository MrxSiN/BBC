#!/usr/bin/env python3
"""BF-authored dynamic ELF DSO structure, ABI and codegen verification.

No Android execution, Bionic linking or JNI loading is implied by these tests.
"""
import hashlib
import json
import random
import struct
import subprocess
import tempfile
from pathlib import Path

from bootstrap.android_dynamic_callable58 import ROOT,STAGES,compile_callable
from bootstrap.android_dynamic_callable59 import compile_shared
from bootstrap.transport import extract_artifact,encode_source
from tests.verify_android_dynamic_callable58 import reference,emulate_callable
from tests.reference import execute as independent_interpreter
from tools.source_check import check_source

STAGE='android_callable_dso_header59'

def verify_elf(image:bytes, code_bytes:int):
    assert image[:4]==b'\x7fELF' and image[4:6]==b'\x02\x01'
    assert image[0x180:0x188]==b'BFP1\x01\x00\x00\x00'
    assert len(image)==1024+code_bytes
    kind,machine,version,entry,phoff,shoff=struct.unpack_from('<HHIQQQ',image,16)
    assert (kind,machine,version,entry,phoff,shoff)==(3,183,1,0,64,512)
    assert struct.unpack_from('<HHHHHH',image,52)==(64,56,2,64,7,6)
    load=struct.unpack_from('<IIQQQQQQ',image,64)
    dynamic=struct.unpack_from('<IIQQQQQQ',image,120)
    assert load==(1,5,0,0,0,len(image),len(image),16384)
    assert dynamic==(2,4,288,288,288,96,96,8)
    assert struct.unpack_from('<IIIII',image,0xc0)==(1,2,1,0,0)
    sym=struct.unpack_from('<IBBHQQ',image,0xf8)
    assert sym==(1,0x12,0,5,1024,code_bytes)
    assert image[0x110:0x11d]==b'\0bfc_call_v1\0'
    tags=[struct.unpack_from('<QQ',image,0x120+16*i) for i in range(6)]
    assert tags==[(4,0xc0),(5,0x110),(6,0xe0),(10,13),(11,24),(0,0)]
    text=struct.unpack_from('<IIQQQQIIQQ',image,0x340)
    assert text[1:6]==(1,6,1024,1024,code_bytes)
    assert text[8:]==(4,0)


def main():
    evidence={'iteration':59,'classification':'STRUCTURAL_ELF_DSO_PLUS_SIMULATED_AARCH64',
      'native_stage_BF_source_rebuild_identical':False,'BF_header_interpreter_equality':0,
      'header_length_vectors':0,'symbol_exports':'bfc_call_v1','dso_cases':0,
      'aarch64_simulator_runs':0,'legacy_code_byte_parity':0,
      'transactional_rejections':0,'readelf_checks':0,
      'android_device_executed':False,'android_dlopen_executed':False,
      'jni_adapter_device_executed':False,'android_native_selfhosting':False}
    source=(ROOT/'experiments'/f'{STAGE}.bf').read_bytes()
    commands=check_source(source)
    assert 0<len(commands)<=16128
    compiler=ROOT/'build/compiler_x86_64_linux.elf'
    rebuilt=extract_artifact(subprocess.run([str(compiler)],input=encode_source(source),
             capture_output=True,check=True,timeout=120).stdout)
    assert rebuilt==(STAGES/f'{STAGE}.elf').read_bytes()
    evidence['native_stage_BF_source_rebuild_identical']=True
    evidence['bf_commands']=len(commands)
    evidence['native_stage_sha256']=hashlib.sha256(rebuilt).hexdigest()
    vectors=[0,1,255,256,511,512,65535,65536,0x100ff,0x10000ff,
             0x100000000,0x1000000000000,0xfffffffffffffbff,
             0xfffffffffffffc00,0xffffffffffffffff]
    for length in vectors:
        out=subprocess.run([str(STAGES/f'{STAGE}.elf')],input=length.to_bytes(8,'little'),
                           capture_output=True,check=True,timeout=15).stdout
        assert len(out)==1025
        overflow=length>=(1<<64)-1024
        assert out[-1]==int(overflow)
        assert out[96:104]==((length+1024)&((1<<64)-1)).to_bytes(8,'little')
        assert out[0x108:0x110]==length.to_bytes(8,'little')
        assert out[0x360:0x368]==length.to_bytes(8,'little')
        evidence['header_length_vectors']+=1
    for length in (0,260):
        independent,_=independent_interpreter(source,length.to_bytes(8,'little'),max_steps=4000000)
        native=subprocess.run([str(STAGES/f'{STAGE}.elf')],input=length.to_bytes(8,'little'),
                              capture_output=True,check=True,timeout=15).stdout
        assert independent==native
        evidence['BF_header_interpreter_equality']+=1
    cases=[b'',b'+.',b'+++[-].',b'+[->+<]>.',b'[[]]',
           b',.',b',[-].',b'<',b'+[.]',b'+[+]',
           b'+++[>++[>+<-]<-]>>.',b'+++++[>+++++[>+<-]<-]>>.',
           b'\x00 ignored\xff+[-].']
    with tempfile.TemporaryDirectory(prefix='dso59-check-') as td:
        d=Path(td);inp=d/'program.bf';shared=d/'policy.so';old=d/'legacy.elf'
        for case in cases:
            inp.write_bytes(case)
            result=compile_shared(inp,shared)
            image=shared.read_bytes();verify_elf(image,result['native_code_bytes'])
            if result['bracket_pairs']<100:
                legacy=compile_callable(inp,old)
                assert image[1024:]==old.read_bytes()[128:]
                evidence['legacy_code_byte_parity']+=1
            for data,budget,cap,tape_size in ((b'',1000,32,64),
                                             (b'\x00\xff',10,6,32),
                                             (b'hello',0,0,1),
                                             (b'\xff',1,1,2)):
                try:r=reference(case,data,tape_size,cap,budget)
                except TimeoutError:continue
                o,status,wrote,used,tape,_=emulate_callable(image,data,tape_size,cap,budget)
                assert (o,status,wrote,used,tape)==(r[0],r[1],len(r[0]),r[2],r[3]),case
                evidence['aarch64_simulator_runs']+=1
            evidence['dso_cases']+=1
            readelf=subprocess.run(['readelf','-Wl','-WS','-Ws','-d',str(shared)],
                         capture_output=True,text=True,check=True,timeout=10)
            assert 'bfc_call_v1' in readelf.stdout and 'DYNAMIC' in readelf.stdout
            assert '.dynsym' in readelf.stdout and '0x400' in readelf.stdout
            evidence['readelf_checks']+=1
        inp.write_bytes(b'[')
        prior=shared.read_bytes()
        for quota in ({}, {'max_pairs':0}):
            try:compile_shared(inp,shared,**quota)
            except ValueError:pass
            else:raise AssertionError('invalid brackets accepted')
            assert shared.read_bytes()==prior
            evidence['transactional_rejections']+=1
        inp.write_bytes(b'+')
        try:compile_shared(inp,shared,max_code_bytes=68)
        except ValueError:pass
        else:raise AssertionError('quota failed to reject')
        assert shared.read_bytes()==prior
        evidence['transactional_rejections']+=1
    p=ROOT/'evidence/iteration59_dynamic_callable_dso.json'
    p.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent checks for BF-owned fixed Windows PE32+ exit-image primitive."""
import hashlib
from pathlib import Path
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'tools'),str(ROOT/'bootstrap')]
from reference import execute
from source_check import check_source
from transport import encode_source,extract_artifact

BF=ROOT/'experiments/windows_pe_exit_seed.bf'
SEED=ROOT/'build/windows_pe_exit_seed_x86_64_linux.elf'
OUTPUT=ROOT/'build/windows_pe_exit_seed_x86_64.exe'

def inspect(image):
    assert len(image)==0x600 and image[:2]==b'MZ'
    nt=struct.unpack_from('<I',image,0x3c)[0]
    assert nt==0x80 and image[nt:nt+4]==b'PE\0\0'
    assert struct.unpack_from('<HHIIIHH',image,nt+4)==(0x8664,2,0,0,0,0xF0,0x22)
    p=nt+24
    assert struct.unpack_from('<H',image,p)[0]==0x20b
    assert struct.unpack_from('<I',image,p+16)[0]==0x1000
    assert struct.unpack_from('<Q',image,p+24)[0]==0x140000000
    assert struct.unpack_from('<II',image,p+32)==(0x1000,0x200)
    assert struct.unpack_from('<II',image,p+56)==(0x3000,0x200)
    assert struct.unpack_from('<H',image,p+68)[0]==3
    assert struct.unpack_from('<I',image,p+108)[0]==16
    assert struct.unpack_from('<II',image,p+112+8)==(0x2010,40)
    assert struct.unpack_from('<II',image,p+112+12*8)==(0x2000,16)
    sec=p+0xF0
    sections=[]
    for i in range(2):
        name,vs,rva,raw,off,_,_,_,_,flags=struct.unpack_from('<8sIIIIIIHHI',image,sec+40*i)
        assert off+raw<=len(image)
        sections.append((name.rstrip(b'\0'),vs,rva,raw,off,flags))
    assert sections==[(b'.text',16,0x1000,512,512,0x60000020),
                      (b'.idata',0x70,0x2000,512,1024,0xC0000040)]
    assert image[0x200:0x206]==b'\x48\x83\xec\x28\x31\xc9'
    assert image[0x206:0x208]==b'\xff\x15'
    disp=struct.unpack_from('<i',image,0x208)[0]
    assert 0x1000+12+disp==0x2000
    assert image[0x20c:0x20e]==b'\x0f\x0b'
    assert struct.unpack_from('<Q',image,0x400)[0]==0x2050
    assert struct.unpack_from('<IIIII',image,0x410)==(0,0,0,0x2038,0x2000)
    assert image[0x438:0x445]==b'KERNEL32.dll\0'
    assert image[0x450:0x45e]==b'\0\0ExitProcess\0'
    assert image[0x424:0x438]==bytes(20)

def main():
    bf=BF.read_bytes(); code=check_source(bf)
    assert len(code)<16128
    reference,steps=execute(bf,max_steps=100000)
    # The existing native Linux BF compiler compiles this BF emitter; no C/LLVM
    # compiler generates PE bytes in the tested emission path.
    result=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],input=encode_source(bf),
                          capture_output=True,timeout=90,check=True)
    compiled=extract_artifact(result.stdout)
    assert compiled==SEED.read_bytes()
    a=subprocess.run([str(SEED)],capture_output=True,timeout=20,check=True)
    b=subprocess.run([str(SEED)],capture_output=True,timeout=20,check=True)
    assert a.stdout==b.stdout==reference==OUTPUT.read_bytes()
    assert not a.stderr and not b.stderr
    inspect(a.stdout)
    probe=bytearray(a.stdout)
    for offset in (0x80,0x206,0x400,0x438):
        corrupted=bytearray(probe); corrupted[offset]^=0x7f
        try: inspect(corrupted)
        except AssertionError: pass
        else: raise AssertionError(f'corrupted PE not rejected at {offset}')
    objdump=subprocess.run(['objdump','-p',str(OUTPUT)],capture_output=True,text=True,timeout=10,check=True)
    assert 'KERNEL32.dll' in objdump.stdout and 'ExitProcess' in objdump.stdout
    return {'bf_instructions':len(code),'native_linux_stage_bytes':len(compiled),
            'pe_bytes':len(a.stdout),'independent_interpreter_steps':steps,
            'output_sha256':hashlib.sha256(a.stdout).hexdigest(),
            'classification':'STRUCTURAL_LINUX_EXECUTED_BF_BYTE_EMITTER_NOT_WINDOWS_EXECUTED'}

if __name__=='__main__':
    import json
    print(json.dumps(main(),indent=2))

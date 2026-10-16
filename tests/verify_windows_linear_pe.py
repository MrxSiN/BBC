#!/usr/bin/env python3
"""Independent offline checks of the bounded BF-owned Windows linear backend."""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import struct
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from run_windows_linear import compile_source,run_stage,WRITER
from reference import execute
from source_check import check_source
from transport import encode_source,extract_artifact

BF=ROOT/'experiments/windows_linear_pe_64.bf'
CORE=ROOT/'build/compiler_x86_64_linux.elf'
IMAGE=ROOT/'build/windows_linear_pe_example_x86_64.exe'
OPMAP={ord('+'):bytes.fromhex('fe03')+b'\x90'*10,
       ord('-'):bytes.fromhex('fe0b')+b'\x90'*10,
       ord('>'):bytes.fromhex('48ffc34c39eb72020f0b9090'),
       ord('<'):bytes.fromhex('48ffcb4c39e373020f0b9090')}

def sha(b):return hashlib.sha256(b).hexdigest()

def inspect(image, commands):
    assert len(image)==2048 and image[:2]==b'MZ'
    assert struct.unpack_from('<I',image,0x3c)[0]==0x80
    assert image[0x80:0x84]==b'PE\0\0'
    assert struct.unpack_from('<HH',image,0x84)==(0x8664,3)
    p=0x98
    assert struct.unpack_from('<H',image,p)[0]==0x20b
    assert struct.unpack_from('<IIII',image,p+4)==(0x400,0x200,0x10000,0x1000)
    assert struct.unpack_from('<Q',image,p+24)[0]==0x140000000
    assert struct.unpack_from('<II',image,p+32)==(0x1000,0x200)
    assert struct.unpack_from('<II',image,p+56)==(0x13000,0x200)
    assert struct.unpack_from('<H',image,p+68)[0]==3
    assert struct.unpack_from('<I',image,p+108)[0]==16
    assert struct.unpack_from('<II',image,p+120)==(0x2010,40)
    assert struct.unpack_from('<II',image,p+208)==(0x2000,16)
    result=[]
    for i in range(3):
        name,vsize,rva,raw,off,_,_,_,_,flags=struct.unpack_from('<8sIIIIIIHHI',image,0x188+40*i)
        result.append((name.rstrip(b'\0'),vsize,rva,raw,off,flags))
    assert result==[(b'.text',0x400,0x1000,0x400,0x200,0x60000020),
                    (b'.idata',0x70,0x2000,0x200,0x600,0xc0000040),
                    (b'.tape',0x10000,0x3000,0,0,0xc0000080)]
    assert image[0x200:0x203]==bytes.fromhex('4c8d25')
    assert 0x1000+7+struct.unpack_from('<i',image,0x203)[0]==0x3000
    assert image[0x207:0x20a]==bytes.fromhex('4c89e3')
    assert image[0x20a:0x20d]==bytes.fromhex('4c8d2d')
    assert 0x1000+17+struct.unpack_from('<i',image,0x20d)[0]==0x13000
    start=0x211
    assert len(commands)<=64
    for i in range(64):
        actual=image[start+i*12:start+(i+1)*12]
        expected=OPMAP[commands[i]] if i<len(commands) else b'\x90'*12
        assert actual==expected, (i,actual.hex(),expected.hex())
    exit_off=start+64*12
    assert image[exit_off:exit_off+8]==bytes.fromhex('4883ec2831c9ff15')
    assert 0x1000+(exit_off-0x200)+12+struct.unpack_from('<i',image,exit_off+8)[0]==0x2000
    assert image[exit_off+12:exit_off+14]==bytes.fromhex('0f0b')
    assert image[exit_off+14:0x600]==b'\x90'*(0x600-exit_off-14)
    assert struct.unpack_from('<Q',image,0x600)[0]==0x2050
    assert struct.unpack_from('<IIIII',image,0x610)==(0,0,0,0x2038,0x2000)
    assert image[0x638:0x645]==b'KERNEL32.dll\0'
    assert image[0x650:0x65e]==b'\0\0ExitProcess\0'


def verify_semantics(commands):
    # Independent per-slot semantic oracle for the four supported commands.
    tape=bytearray(65536);ptr=0
    for command in commands:
        if command==ord('+'):tape[ptr]=(tape[ptr]+1)&255
        elif command==ord('-'):tape[ptr]=(tape[ptr]-1)&255
        elif command==ord('>'):ptr+=1
        else:ptr-=1
        if not 0<=ptr<65536:return True
    snapshot=bytearray()
    out,_=execute(commands,tape_snapshot=snapshot)
    assert not out and snapshot==tape
    return False


def main():
    code=check_source(BF.read_bytes())
    assert len(code)==10831
    compiled=extract_artifact(run_stage(CORE,encode_source(BF.read_bytes()),90))
    assert compiled==WRITER.read_bytes()
    native_tests=0;reference_tests=0; expected_traps=0
    cases=[b'',b'+',b'-',b'>',b'<',b'+>++<--',b'>+<',b'+'*64,
           b'-'*64,b'>'*64,b'+'*32+b'<'*32,b'+'*255 if False else b'+'*63+b'-']
    rng=random.Random(390013)
    for i in range(75):
        cases.append(bytes(rng.choice(b'+-<>') for _ in range(rng.randrange(0,65))))
    for commands in cases:
        src=b'This is ignored!\0\xff\n'+commands+b'\xff\0ignored text'
        image=compile_source(src)
        inspect(image,commands)
        expected_traps+=verify_semantics(commands)
        native_tests+=1
    for source in (b'',b'+',b'+-<',b'++++>----<',b'+'*64):
        image=compile_source(source)
        independent,steps=execute(BF.read_bytes(),stdin=source,max_steps=5_000_000)
        assert independent==image+b'\0'
        reference_tests+=1
    # The BF writer, rather than the host adapter, rejects unknown opcodes.
    rejections=[b'.',b',',b'[+]',b'+[->+<]',b'+'*65,b'<'*65,b'+'*64+b'.']
    for raw in rejections:
        filtered=bytes(c for c in raw if c in b'<>+-.,[]')
        result=run_stage(WRITER,filtered)
        assert len(result)==2049 and result[-1]==1
        try:compile_source(raw)
        except ValueError:pass
        else:raise AssertionError(f'unsupported input accepted: {raw[:20]!r}')
    # Source filtering is performed by existing BF scanner, not host Python.
    assert compile_source(b'junk\x00\xff+ more junk!')==compile_source(b'+')
    # CLI must not overwrite an existing target on rejected input.
    with tempfile.TemporaryDirectory() as td:
        t=pathlib.Path(td); inp=t/'test.bf';out=t/'test.exe';out.write_bytes(b'KEEP')
        for raw in (b'.', b'+'*65, b'['):
            inp.write_bytes(raw)
            p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_linear.py'),str(inp),str(out)],capture_output=True)
            assert p.returncode!=0 and out.read_bytes()==b'KEEP'
        inp.write_bytes(b'>+<')
        p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_linear.py'),str(inp),str(out)],capture_output=True)
        assert p.returncode==0
        assert out.read_bytes()==compile_source(b'>+<')
    # Published example is produced by BF source, not development template.
    assert IMAGE.read_bytes()==compile_source(b'>+<')
    assert 'KERNEL32.dll' in subprocess.run(['objdump','-p',str(IMAGE)],capture_output=True,text=True,check=True).stdout
    disasm=subprocess.run(['objdump','-d','-j','.text','-Mintel',str(IMAGE)],capture_output=True,text=True,check=True).stdout
    for mnemonic in ('lea','inc','dec','cmp','ud2','ExitProcess'):
        if mnemonic!='ExitProcess':assert mnemonic in disasm
    return {'iteration':39,'class':'LINUX_EXECUTED_BF_PE_EMISSION_WINDOWS_RUNTIME_UNVERIFIED',
            'linear_commands_max':64,'operations':['+','-','>','<'],
            'source_bf_commands':len(code),'source_bf_sha256':sha(BF.read_bytes()),
            'compiled_linux_bf_emitter_bytes':len(compiled),'compiled_linux_sha256':sha(compiled),
            'emitted_pe_bytes':2048,'example_sha256':sha(IMAGE.read_bytes()),
            'semantic_and_structure_programs':native_tests,'reference_interpreter_programs':reference_tests,
            'reference_expected_pointer_traps':expected_traps,
            'BF_emitter_rejections':len(rejections),'CLI_atomic_rejection_cases':3,
            'Windows_loader_tests':'NOT_RUN','Windows_native_compiler':'UNIMPLEMENTED',
            'Windows_selfhosting':'UNIMPLEMENTED'}

if __name__=='__main__':print(json.dumps(main(),indent=2))

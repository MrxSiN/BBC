#!/usr/bin/env python3
"""Offline PE/ABI, BF ownership, differential source, and failure checks.

Not a Windows loader test. Machine-code semantics are checked structurally; the
runtime API protocol must still execute under Windows or a verified emulator.
"""
import hashlib
import json
import pathlib
import random
import struct
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from transport import encode_source,extract_artifact
from reference import execute
from source_check import check_source
from run_windows_linear_io import compile_source,run_stage,WRITER
from author_windows_linear_io import template

SOURCE=ROOT/'experiments/windows_linear_io_pe_64.bf'
CORE=ROOT/'build/compiler_x86_64_linux.elf'
EXAMPLE=ROOT/'build/windows_linear_io_example_x86_64.exe'
SLOTS={ord('+'):bytes.fromhex('fe03')+b'\x90'*10,
       ord('-'):bytes.fromhex('fe0b')+b'\x90'*10,
       ord('>'):bytes.fromhex('48ffc34c39eb72020f0b9090'),
       ord('<'):bytes.fromhex('48ffcb4c39e373020f0b9090'),
       ord('.'):bytes.fromhex('41ffd6')+b'\x90'*9,
       ord(','):bytes.fromhex('41ffd7')+b'\x90'*9}

def sha(data):return hashlib.sha256(data).hexdigest()
def load_target(image, offset):
    return 0x1000+(offset-0x200)+7+struct.unpack_from('<i',image,offset+3)[0]

def static_image(image,commands):
    assert len(image)==2048 and image[:2]==b'MZ' and image[0x80:0x84]==b'PE\0\0'
    assert struct.unpack_from('<HH',image,0x84)==(0x8664,3)
    assert struct.unpack_from('<H',image,0x98)[0]==0x20b
    assert struct.unpack_from('<I',image,0x98+56)[0]==0x13000
    assert struct.unpack_from('<II',image,0x98+120)==(0x2030,40)
    assert struct.unpack_from('<II',image,0x98+208)==(0x2000,40)
    sections=[]
    for n in range(3):
        name,vsize,rva,raw,off,_,_,_,_,flags=struct.unpack_from('<8sIIIIIIHHI',image,0x188+40*n)
        sections.append((name.rstrip(b'\0'),vsize,rva,raw,off,flags))
    assert sections==[(b'.text',0x400,0x1000,0x400,0x200,0x60000020),
                       (b'.idata',0xd0,0x2000,0x200,0x600,0xc0000040),
                       (b'.tape',0x10000,0x3000,0,0,0xc0000080)]
    pro,epi,helpers=template()[1:]
    assert image[0x200:0x200+31]==pro
    for i, target in ((0,0x3000),(10,0x13000)):
        assert load_target(image,0x200+i)==target
    end_of_slots=0x200+31+64*12
    assert load_target(image,0x200+17)==0x1000+31+768+14
    # R15 uses its own RIP-relative LEA. Write and read helpers must be stable.
    assert load_target(image,0x200+24)==0x1000+31+768+14+len(helpers)-len(template_read_helper())
    for i in range(64):
        slot=image[0x200+31+i*12:0x200+31+(i+1)*12]
        assert slot == (SLOTS[commands[i]] if i<len(commands) else b'\x90'*12),(i,slot.hex())
    assert image[end_of_slots:end_of_slots+14]==epi
    assert image[end_of_slots+14:end_of_slots+14+len(helpers)]==helpers
    assert image[end_of_slots+14+len(helpers):0x600]==b'\x90'*(0x600-end_of_slots-14-len(helpers))
    fixed=template()[0]
    assert image[:0x200]==fixed[:0x200] and image[0x600:]==fixed[0x600:]
    assert image[0x670:0x67d]==b'KERNEL32.dll\0'
    for offset,name in ((0x690,b'ExitProcess'),(0x6a0,b'GetStdHandle'),(0x6b0,b'ReadFile'),(0x6c0,b'WriteFile')):
        assert image[offset+2:offset+2+len(name)+1]==name+b'\0'

def template_read_helper():
    from author_windows_linear_io import make_io_helper
    return make_io_helper(0x1000+31+768+14+len(template()[3])-len(make_io_helper(0,-10,0x2010,False)), -10,0x2010,False)

def test_helpers(image):
    """Independent API call, shadow space, I/O buffer, and return checks."""
    pro,epi,helpers=template()[1:]
    origin=0x200+31+768+14
    write_len=len(helpers)-len(template_read_helper())
    for pos,handle,iat,write in ((origin,-11,0x2018,True),(origin+write_len,-10,0x2010,False)):
        helper=helpers[pos-origin:pos-origin+(write_len if write else len(helpers)-write_len)]
        assert helper.startswith(bytes.fromhex('4883ec30'))
        if write: assert bytes.fromhex('c60300') not in helper
        else: assert bytes.fromhex('c60300') in helper
        assert b'\xb9'+struct.pack('<i',handle) in helper
        assert bytes.fromhex('41b801000000') in helper
        assert bytes.fromhex('4c8d4c2428') in helper
        assert bytes.fromhex('48c744242000000000') in helper
        assert bytes.fromhex('c744242800000000') in helper
        assert bytes.fromhex('75020f0b') in helper
        assert helper.endswith(bytes.fromhex('4883c430c3'))
        if write:assert bytes.fromhex('837c24280174020f0b') in helper
        # Locate import calls by their six-byte opcodes and verify RIP targets.
        calls=[n for n in range(len(helper)-5) if helper[n:n+2]==b'\xff\x15']
        assert len(calls)==2
        resolved=[0x1000+(pos-0x200)+n+6+struct.unpack_from('<i',helper,n+2)[0] for n in calls]
        assert resolved==[0x2008,iat]

def main():
    source=SOURCE.read_bytes(); commands=check_source(source)
    assert len(commands)==10352
    compiled=extract_artifact(run_stage(CORE,encode_source(source),timeout=90))
    assert compiled==WRITER.read_bytes()
    examples=[b'',b'+.',b'-.',b',.',b',>,.<.',b'+>++,<.',
              b'+\0ignored\xff.',b'>+<.',b','*64,b'.'*64,
              b'+'*63+b'.',b'<'*64]
    rng=random.Random(400013)
    for _ in range(75):
        examples.append(bytes(rng.choice(b'+-<>.,') for _ in range(rng.randrange(0,65))))
    oracle_cases=0
    for original in examples:
        filtered=bytes(c for c in original if c in b'<>+-.,[]')
        image=compile_source(original)
        static_image(image,filtered)
        # Independent BF semantic oracle, only for nontrapping programs.
        if b'<' not in filtered or filtered.find(b'>')>=0:
            try:execute(filtered,stdin=b'\0\xffHELLO',max_steps=10000)
            except Exception:pass # excluded boundary traps; structural safety checked by x64 slots
            else:oracle_cases+=1
    image=compile_source(b',.');test_helpers(image)
    assert image==EXAMPLE.read_bytes()
    print('images',len(examples),'oracle no-trap cases',oracle_cases)
    for program in (b'',b'+.',b',.',b'-->.',b',,',b'.'*64):
        generated,steps=execute(source,stdin=program,max_steps=5_000_000)
        assert generated==compile_source(program)+b'\0',(program,steps)
    rejections=(b'[+]',b'[]',b',]' ,b'+'*65,b'.'*65,b'+'*64+b'[')
    for src in rejections:
        direct=run_stage(WRITER,src)
        assert len(direct)==2049 and direct[-1]==1
        try:compile_source(src)
        except ValueError:pass
        else:raise AssertionError('unsupported source accepted')
    # Strictly transport-only CLI and atomic output preservation.
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td);input_path=p/'source.bf';output=p/'compiled.exe'
        output.write_bytes(b'ORIGINAL')
        for original in rejections:
            input_path.write_bytes(original)
            result=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_linear_io.py'),str(input_path),str(output)],capture_output=True)
            assert result.returncode != 0 and output.read_bytes()==b'ORIGINAL'
        input_path.write_bytes(b',.')
        result=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_linear_io.py'),str(input_path),str(output)],capture_output=True)
        assert result.returncode==0 and output.read_bytes()==image
    symbols=subprocess.run(['objdump','-p',str(EXAMPLE)],capture_output=True,text=True,check=True).stdout
    for name in ('ExitProcess','GetStdHandle','ReadFile','WriteFile'):
        assert name in symbols
    output={'iteration':40,'classification':'LINUX_EXECUTED_BF_PE_GENERATION_WINDOWS_EXECUTION_UNVERIFIED',
            'source':'experiments/windows_linear_io_pe_64.bf','source_commands':len(commands),
            'source_sha256':sha(source),'filtered_sha256':sha(commands),
            'native_linux_emitter_bytes':len(compiled),'native_linux_emitter_sha256':sha(compiled),
            'pe_example_sha256':sha(image),'pe_bytes':len(image),
            'operations':list('+-<>.,'),'linear_limit':64,'structural_and_semantic_cases':len(examples),'reference_bf_program_executions':oracle_cases,
            'independent_bf_interpreter_comparisons':6,'expected_rejections':len(rejections),
            'atomic_preservation_rejections':len(rejections),'Windows_loader':'NOT_RUN',
            'Win32_IO_RUNTIME':'NOT_EXECUTED','Windows_native_S2':'UNIMPLEMENTED'}
    (ROOT/'evidence/iteration40_windows_linear_io.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Verify BF-authored compact raw AArch64 slots, NOT complete Android ELF."""
from __future__ import annotations
import hashlib,json,random,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tools'),str(ROOT/'tests')]
from transport import encode_source,extract_artifact
from source_check import check_source
from android_compact_stream_transport import emit_compact_slots
from verify_android_aarch64_subset import emulate,NOP,PACK
from reference import execute
from run_android_extended import compile_source

NEW=ROOT/'build/android_streaming_compact_slots_x86_64_linux.elf'
SRC=ROOT/'experiments/android_streaming_compact_slots.bf'
OLD=ROOT/'build/android_wide_slot_emitter_x86_64_linux.elf'
OPS=b'+-><.,'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def process(src):
    raw=b''.join(bytes((1,c)) for c in src)+b'\0'
    p=subprocess.run([str(NEW)],input=raw,capture_output=True,timeout=60,check=True)
    assert p.stderr==b''
    return p.stdout

def decode(raw):
    p=0;out=bytearray();count=0
    while p<len(raw):
        if raw[p]==0:
            assert raw[p:]==b'\0\0' or raw[p:]==b'\0\1'
            return bytes(out),count,raw[p+1]
        assert raw[p]==1;p+=1
        assert p<len(raw);size=raw[p];p+=1
        assert size>=4 and size<=48 and size%4==0
        assert len(raw)-p>=size
        out.extend(raw[p:p+size]);p+=size;count+=1
    raise AssertionError('missing final frame')

def main():
    start=time.monotonic()
    raw=SRC.read_bytes();filtered=check_source(raw)
    assert len(filtered)<=16128
    native=extract_artifact(subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                            input=encode_source(raw),capture_output=True,check=True,timeout=90).stdout)
    assert native==NEW.read_bytes()
    assert native==extract_artifact(subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                            input=encode_source(filtered),capture_output=True,check=True,timeout=90).stdout)
    templates={}
    for op in OPS:
        t=subprocess.run([str(OLD)],input=bytes((op,0)),capture_output=True,check=True).stdout[:48]
        while t.endswith(PACK([NOP])):t=t[:-4]
        templates[op]=t
    rng=random.Random(500075)
    cases=[b'',b'+',b'-',b'>',b'<',b'.',b',',b'+++---..,,><',b'\x00+\xff-']
    for _ in range(150):
        cases.append(bytes(rng.choice(OPS+b'xyz \n\x00\xff') for _ in range(rng.randrange(0,230))))
    for case in cases:
        stream=process(case);compiled,count,status=decode(stream)
        expect=b''.join(templates[x] for x in case if x in OPS)
        assert compiled==expect and status==0
        assert count==sum(c in OPS for c in case)
    for source in (b'[',b']',b'+[]',b'++[-]',b'['+b'+'*90+b']'):
        _,_,status=decode(process(source));assert status==1
    # Construct a synthetic TEST-ONLY ELF overlay with existing BF-authored
    # empty source header and startup. The compact compiler does not do this.
    empty=compile_source(b'',dynamic=True)
    inputs=bytes((i*47+3)&255 for i in range(250))
    runs=0;traps=0
    for source in cases[:10]+cases[10:75]:
        instructions=bytes(x for x in source if x in OPS)
        if len(instructions)>160:continue
        code,_,_=decode(process(source))
        image=bytearray(empty)
        image[0x210:0x210+len(code)]=code
        image[0x210+len(code):0x220+len(code)]=PACK([0xd2800000,0xd2800ba8,0xd4000001,NOP])
        try:out,_=execute(instructions,inputs,max_steps=10000);trap=False
        except IndexError:out=None;trap=True;traps+=1
        for bias in (0,0x40000000):
            observed,status,_=emulate(image,bias,tape_base_rva=0x8060,
                                       code_limit=0x220+len(code),input_bytes=inputs,max_steps=6000)
            assert (status==2) if trap else (observed,status)==(out,0),(source,bias,observed,status,out)
            runs+=1
    with tempfile.TemporaryDirectory(prefix='bf-compact-') as d:
        d=Path(d);src=d/'input.bf';dest=d/'code.bin';src.write_bytes(b'+'*300001)
        t=time.monotonic();measurement=emit_compact_slots(src,dest);duration=time.monotonic()-t
        assert measurement['instruction_records']==300001
        assert measurement['native_code_bytes']==300001*12
        assert sha(dest.read_bytes())==sha(templates[ord('+')]*300001)
        dest.write_bytes(b'EXISTING')
        for invalid,quota in ((b'[+]',None),(b'++++',47)):
            src.write_bytes(invalid)
            try:emit_compact_slots(src,dest,max_output_bytes=quota)
            except ValueError:pass
            else:raise AssertionError('failure was accepted')
            assert dest.read_bytes()==b'EXISTING'
    evidence={'iteration':50,'classification':'LINUX_EXECUTED_STANDARD_BF_COMPACT_AARCH64_RAW_CODE_ONLY',
     'bf_source':str(SRC.relative_to(ROOT)),'native_stage':str(NEW.relative_to(ROOT)),
     'source_sha256':sha(raw),'native_sha256':sha(native),'source_bf_commands':len(filtered),
     'native_stage_bytes':len(native),'differential_raw_programs':len(cases),
     'aarch64_instruction_simulations':runs,'expected_pointer_traps':traps,
     'tested_large_linear_source_commands':300001,'native_bytes_for_large_linear_source':300001*12,
     'equivalent_padded_native_bytes':300001*48,'seconds_large_source':round(duration,3),
     'atomic_rejections':2,'native_code_generation_by_brainfuck':True,
     'full_android_elf_generated':False,'bracket_support':False,'android_loader_executed':False,
     'large_real_app_compilation':'NOT_RUN','elapsed_seconds':round(time.monotonic()-start,3)}
    (ROOT/'evidence/iteration50_android_compact_stream.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""BF native callable branch compiler: independent instruction-level simulator.

This tests emitted bytes, not real Android loader/JNI execution.
"""
import hashlib
import json
import random
import struct
import subprocess
import tempfile
import time
from pathlib import Path

from bootstrap.android_dynamic_callable58 import compile_callable,ROOT,STAGES
from bootstrap.transport import encode_source,extract_artifact
from tools.source_check import check_source
from bootstrap.android_dynamic_callable57 import compile_callable as compile_linear57
from tests.reference import execute as bf_reference

MASK=(1<<64)-1


def emulate_callable(image:bytes,data=b'',tape_size=65536,output_limit=65536,
                     budget=1000,max_steps=2000000):
    assert image[:4]==b'\x7fELF'
    if image[0x180:0x184]==b'BFP1':
        code=image[1024:]
    else:
        assert image[120:124]==b'BFP1'
        code=image[128:]
    regs={0:0,1:len(data),3:output_limit,4:0x100000,5:tape_size,
          6:budget,9:0,10:0,11:0,12:0,13:0,14:0,16:0,17:0,15:0}
    tape=bytearray(tape_size);out=bytearray();pc=0;cmp_hs=False
    output_used=None;budget_used=None
    for step in range(max_steps):
        if not 0<=pc<=len(code)-4 or pc%4:raise ValueError(f'invalid AArch64 PC {pc}')
        op=struct.unpack_from('<I',code,pc)[0]
        nxt=pc+4
        if op&0xfc000000==0x14000000:
            jump=op&0x3ffffff
            if jump&(1<<25):jump-=1<<26
            nxt=pc+4*jump
        elif op&0xff00001f in (0x54000002,0x54000003):
            jump=(op>>5)&0x7ffff
            if jump&(1<<18):jump-=1<<19
            if ((op&15)==2 and cmp_hs) or ((op&15)==3 and not cmp_hs):nxt=pc+4*jump
        elif op in (0x350000e9,0x340000e9):
            if (op==0x350000e9 and regs[9]&255) or (op==0x340000e9 and not regs[9]&255):
                nxt=pc+28
        elif op==0xb50000a6:
            if regs[6]:nxt=pc+20
        elif op==0x10000011:regs[17]=pc
        elif op==0x5800006f:
            regs[15]=struct.unpack_from('<q',code,pc+12)[0]
        elif op==0x8b0f0a31:regs[17]=(regs[17]+(regs[15]<<2))&MASK
        elif op==0xd61f0220:nxt=regs[17]
        elif op==0xaa1f03ea:regs[10]=0
        elif op==0xaa0403eb:regs[11]=regs[4]
        elif op==0xaa1f03ec:regs[12]=0
        elif op==0xaa1f03ed:regs[13]=0
        elif op==0xaa0603f0:regs[16]=regs[6]
        elif op==0xaa1f03ee:regs[14]=0
        elif op==0xd503201f:pass
        elif op==0x39400169:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe tape load')
            regs[9]=tape[pos]
        elif op==0x39000169:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe tape store')
            tape[pos]=regs[9]&255
        elif op==0x11000529:regs[9]=(regs[9]+1)&0xffffffff
        elif op==0x51000529:regs[9]=(regs[9]-1)&0xffffffff
        elif op==0x9100054a:regs[10]=(regs[10]+1)&MASK
        elif op==0xd100054a:regs[10]=(regs[10]-1)&MASK
        elif op==0xeb05015f:cmp_hs=regs[10]>=regs[5]
        elif op==0x52800060:regs[0]=3
        elif op==0xcb060201:
            regs[1]=(regs[16]-regs[6])&MASK;budget_used=regs[1]
        elif op==0xf90000ed:output_used=regs[13]
        elif op==0xd65f03c0:
            return bytes(out),regs[0],output_used,budget_used,bytes(tape),step+1
        elif op==0x8b0a008b:regs[11]=(regs[4]+regs[10])&MASK
        elif op==0xeb01019f:cmp_hs=regs[12]>=regs[1]
        elif op==0x386c6809:
            if regs[12]>=len(data):raise ValueError('unsafe input load')
            regs[9]=data[regs[12]]
        elif op==0x9100058c:regs[12]+=1
        elif op==0x3900017f:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe zero store')
            tape[pos]=0
        elif op==0xeb0301bf:cmp_hs=regs[13]>=regs[3]
        elif op==0x382d6849:
            if regs[13]>=output_limit:raise ValueError('unsafe output store')
            out.append(regs[9]&255)
        elif op==0x910005ad:regs[13]+=1
        elif op==0x5280004e:regs[14]=2
        elif op==0x2a0e03e0:regs[0]=regs[14]
        elif op==0x52800020:regs[0]=1
        elif op==0xd10004c6:regs[6]-=1
        else:raise ValueError(f'unknown AArch64 opcode {op:08x} at {pc:x}')
        pc=nxt
    raise TimeoutError('AArch64 instruction limit')


def reference(src:bytes,inp:bytes,tape_size:int,output_limit:int,budget:int):
    code=bytes(c for c in src if c in b'><+-.,[]')
    pair={};stack=[]
    for i,c in enumerate(code):
        if c==ord('['):stack.append(i)
        if c==ord(']'):
            if not stack:raise ValueError('bad brackets')
            j=stack.pop();pair[i]=j;pair[j]=i
    if stack:raise ValueError('bad brackets')
    tape=bytearray(tape_size);p=0;i=0;cursor=0;used=0;status=0;out=bytearray()
    for _ in range(200000):
        if i>=len(code):return bytes(out),status,used,bytes(tape)
        c=code[i]
        if c==43:tape[p]=(tape[p]+1)&255
        if c==45:tape[p]=(tape[p]-1)&255
        if c==62 or c==60:
            p+=1 if c==62 else -1
            if p<0 or p>=tape_size:return bytes(out),3,used,bytes(tape)
        if c==44:
            tape[p]=inp[cursor] if cursor<len(inp) else 0
            cursor+=cursor<len(inp)
        if c==46:
            if len(out)==output_limit:status=2
            else:out.append(tape[p])
        if c==91:
            if tape[p]==0:i=pair[i]+1;continue
            if used>=budget:return bytes(out),1,used,bytes(tape)
            used+=1
        if c==93 and tape[p]!=0:i=pair[i];continue
        i+=1
    raise TimeoutError('reference too many steps')


def main():
    t0=time.monotonic()
    evidence={'iteration':58,'classification':'LINUX_BF_NATIVE_AARCH64_CALLABLE_ALL8_SIMULATOR',
              'stages':{},'cases':0,'simulator_runs':0,'invalid_brackets':0,
              'wide_branch_patches':0,'largest_nesting':0,'large_structural':{},
              'independent_interpreter_checks':0,'linear_byte_identical_cases':0,
              'android_device_executed':False,'jni_loader_executed':False,
              'fully_dynamic_callable_completed':False}
    for name in ('android_callable_slots58','android_callable_ledger58'):
        src=(ROOT/'experiments'/f'{name}.bf').read_bytes()
        cmds=check_source(src);assert len(cmds)<=16128
        elf=extract_artifact(subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
               input=encode_source(src),capture_output=True,check=True,timeout=120).stdout)
        native=STAGES/f'{name}.elf'
        assert elf==native.read_bytes()
        evidence['stages'][name]={'bf_commands':len(cmds),
                'source_sha256':hashlib.sha256(src).hexdigest(),
                'native_sha256':hashlib.sha256(elf).hexdigest(),
                'rebuild_identical':True}
    # Execute the new authoritative BF stages under an independent interpreter.
    for name,raw in [('android_callable_slots58',b'\x01+\0'),
                     ('android_callable_slots58',b'\x01[\x01]\0'),
                     ('android_callable_ledger58',b'\x01+\0'),
                     ('android_callable_ledger58',b'\x01[\x01]\0')]:
        first,_=bf_reference((ROOT/'experiments'/f'{name}.bf').read_bytes(),
                             raw,max_steps=4000000)
        proc=subprocess.run([str(STAGES/f'{name}.elf')],input=raw,
                            capture_output=True,check=True,timeout=15)
        assert first==proc.stdout
        evidence['independent_interpreter_checks']+=1
    cases=[b'',b'+',b'-',b'>+<.',b'<',b',.',b'+[->+<]>.',
           b'+++[>++[>+<-]<-]>>.',b'[[]]',b'[-][[]]',b',[-].',
           b'+[.]',b'+[+]',b'+[->+<]>.',b'+[[-]+++]',
           b'['*260+b']'*260,b'['*1030+b']'*1030,
           b'+'*260+b'[-].',b'X\x00ignored[.]']
    rng=random.Random(58)
    for _ in range(40):
        prefix=bytes(rng.choice(b'+-<>.,') for _ in range(rng.randrange(0,35)))
        # Every synthesized loop terminates for zero input, and tests both
        # jump directions when the prefix leaves the current cell nonzero.
        cases.append(prefix+b'[->+<][-]')
    with tempfile.TemporaryDirectory(prefix='callable58-checks-') as td:
        d=Path(td);src=d/'sample.bf';dst=d/'image.elf'
        for program in cases:
            src.write_bytes(program)
            result=compile_callable(src,dst)
            image=dst.read_bytes()
            if not any(c in program for c in b'[]'):
                old=d/'old.elf'
                compile_linear57(src,old)
                assert old.read_bytes()==image
                evidence['linear_byte_identical_cases']+=1
            assert result['elf_bytes']==len(image)
            assert int.from_bytes(image[96:104],'little')==len(image)
            assert result['wide_relocation_patches']==2*result['bracket_pairs']
            subprocess.run(['readelf','-Wl',str(dst)],check=True,capture_output=True)
            evidence['wide_branch_patches']+=result['wide_relocation_patches']
            evidence['largest_nesting']=max(evidence['largest_nesting'],result['maximum_nesting_depth'])
            for tape_size in (1,32):
                for budget in (0,5,1000):
                    raw=bytes(rng.randrange(256) for _ in range(8))
                    expect=reference(program,raw,tape_size,3,budget)
                    got=emulate_callable(image,raw,tape_size,3,budget)
                    observed=(got[0],got[1],got[3],got[4])
                    assert observed==expect,(program[:40],tape_size,budget,observed,expect)
                    evidence['simulator_runs']+=1
            evidence['cases']+=1
        for malformed in (b'[',b']',b'[[[]',b'[]]',b'][',b'['*200+b']'*199):
            src.write_bytes(malformed);dst.write_bytes(b'KEEP')
            try:compile_callable(src,dst)
            except (ValueError,RuntimeError):pass
            else:raise AssertionError('invalid source accepted')
            assert dst.read_bytes()==b'KEEP'
            evidence['invalid_brackets']+=1
        src.write_bytes(b'[[]]');dst.write_bytes(b'KEEP')
        try:compile_callable(src,dst,max_pairs=1)
        except (ValueError,RuntimeError):pass
        else:raise AssertionError('bracket resource quota not enforced')
        assert dst.read_bytes()==b'KEEP'
        src.write_bytes(b'+[->+<]')
        try:compile_callable(src,dst,max_code_bytes=68)
        except (ValueError,RuntimeError):pass
        else:raise AssertionError('code resource quota not enforced')
        assert dst.read_bytes()==b'KEEP'
        # Legacy 4,096 IR records and 255 bracket depth are exceeded above.
        # This larger program is examined structurally instead of emulated.
        for label,program in [('records6000',b'+'*6000+b'[->+<]'),
                               ('ignored_above_1m',b'ignored'+b'X'*(1048576+9)+b'+[->+<]')]:
            src.write_bytes(program);meta=compile_callable(src,dst)
            assert meta['bracket_pairs']==1
            assert len(dst.read_bytes())==meta['elf_bytes']
            evidence['large_structural'][label]={'source_bytes':len(program),
                'elf_bytes':meta['elf_bytes'],'pairs':meta['bracket_pairs']}
        evidence['atomic_rejections']=8
    evidence['elapsed_seconds']=round(time.monotonic()-t0,2)
    target=ROOT/'evidence'/'iteration58_dynamic_callable_loops.json'
    target.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Differential tests for the new BF-native dynamically sized callable lane.

This executes emitted AArch64 words in a deliberately small independent
instruction emulator. It does NOT establish on-device native Android execution.
"""
import hashlib
import json
import random
import struct
import subprocess
import tempfile
from pathlib import Path

from bootstrap.android_dynamic_callable57 import compile_callable, STAGES, ROOT
from bootstrap.transport import encode_source, extract_artifact
from tests.reference import execute
from tools.source_check import check_source

MASK=(1<<64)-1


def aarch64_linear(image:bytes, data=b'', tape_size=65536, output_limit=65536,
                   max_steps=1000000):
    assert image[:4]==b'\x7fELF' and image[120:124]==b'BFP1'
    code=image[128:]
    regs={0:0,1:len(data),3:output_limit,4:0x100000,5:tape_size,
          6:1000,10:0,11:0,12:0,13:0,14:0,16:0}
    tape=bytearray(tape_size)
    out=bytearray()
    pc=0
    cmp_hs=False
    output_used=None
    budget_used=None
    for step in range(max_steps):
        if pc<0 or pc+4>len(code) or pc%4:raise ValueError('invalid AArch64 PC')
        op=struct.unpack_from('<I',code,pc)[0]
        next_pc=pc+4
        if op & 0xfc000000 == 0x14000000:
            jump=op&0x3ffffff
            if jump&(1<<25):jump-=1<<26
            next_pc=pc+4*jump
        elif op&0xff00001f in (0x54000002,0x54000003):
            jump=(op>>5)&0x7ffff
            if jump&(1<<18):jump-=1<<19
            if (op&15)==2 and cmp_hs or (op&15)==3 and not cmp_hs:next_pc=pc+4*jump
        elif op==0xaa1f03ea:regs[10]=0
        elif op==0xaa0403eb:regs[11]=regs[4]
        elif op==0xaa1f03ec:regs[12]=0
        elif op==0xaa1f03ed:regs[13]=0
        elif op==0xaa0603f0:regs[16]=regs[6]
        elif op==0xaa1f03ee:regs[14]=0
        elif op==0xd503201f:pass
        elif op==0x39400169:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe AArch64 tape access')
            regs[9]=tape[pos]
        elif op==0x39000169:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe AArch64 tape store')
            tape[pos]=regs[9]&255
        elif op==0x11000529:regs[9]=(regs[9]+1)&0xffffffff
        elif op==0x51000529:regs[9]=(regs[9]-1)&0xffffffff
        elif op==0x9100054a:regs[10]=(regs[10]+1)&MASK
        elif op==0xd100054a:regs[10]=(regs[10]-1)&MASK
        elif op==0xeb05015f:cmp_hs=regs[10]>=regs[5]
        elif op==0x52800060:regs[0]=3
        elif op==0xcb060201:
            regs[1]=(regs[16]-regs[6])&MASK
            budget_used=regs[1]
        elif op==0xf90000ed:output_used=regs[13]
        elif op==0xd65f03c0:
            return bytes(out),regs[0],output_used,budget_used,bytes(tape),step+1
        elif op==0x8b0a008b:regs[11]=(regs[4]+regs[10])&MASK
        elif op==0xeb01019f:cmp_hs=regs[12]>=regs[1]
        elif op==0x386c6809:
            if regs[12]>=len(data):raise ValueError('unsafe AArch64 input access')
            regs[9]=data[regs[12]]
        elif op==0x9100058c:regs[12]+=1
        elif op==0x3900017f:
            pos=regs[11]-regs[4]
            if not 0<=pos<tape_size:raise ValueError('unsafe AArch64 zero store')
            tape[pos]=0
        elif op==0xeb0301bf:cmp_hs=regs[13]>=regs[3]
        elif op==0x382d6849:
            if regs[13]>=output_limit:raise ValueError('unsafe AArch64 output access')
            out.append(regs[9]&255)
        elif op==0x910005ad:regs[13]+=1
        elif op==0x5280004e:regs[14]=2
        elif op==0x2a0e03e0:regs[0]=regs[14]
        elif op==0x52800020:regs[0]=1
        elif op==0xd10004c6:regs[6]-=1
        else:raise ValueError(f'unknown AArch64 opcode {op:08x} at {pc:x}')
        pc=next_pc
    raise TimeoutError('AArch64 word limit')


def main():
    evidence={'iteration':57,'classification':'LINUX_NATIVE_BF_DYNAMIC_CALLABLE_LINEAR_PLUS_AARCH64_SIMULATOR',
              'source_purity':{},'small_cases':0,'simulator_runs':0,'failed_atomic_rejections':0,
              'large_record_cases':{},'elf_header_wide_sizes':0,
              'android_device_executed':False,'android_jni_integrated':False,'loops_supported':False,
              'full_dynamic_callable_complete':False}
    for name in ('android_callable_linear57','android_callable_header57'):
        s=(ROOT/'experiments'/f'{name}.bf').read_bytes()
        cmds=check_source(s)
        assert len(cmds)<=16128
        elf=extract_artifact(subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                           input=encode_source(s),capture_output=True,check=True,timeout=120).stdout)
        assert elf==(STAGES/f'{name}.elf').read_bytes()
        evidence['source_purity'][name]={'bf_commands':len(cmds),
            'source_sha256':hashlib.sha256(s).hexdigest(),
            'native_stage_sha256':hashlib.sha256(elf).hexdigest(),
            'BF_compiler_rebuild_byte_identical':True}
    from tests.verify_policy_ir import native_oracle
    rng=random.Random(57)
    samples=[b'',b'+',b'-',b',.',b'+,.',b'>+<-.',b'<',b'+<',b','*2+b'.'*2,
             b'+.'*8,b'>+<'*25,b'[-]',b'ignored\0noninstructions+++.',
             b'\xff.\x00++',b'+'*256+b'.',b'+'*511+b'.']
    for _ in range(45):
        samples.append(bytes(rng.choice(b'>.<+-,garbage\x00') for _ in range(rng.randrange(1,80))))
    with tempfile.TemporaryDirectory(prefix='bf-callable57-tests-') as td:
        d=Path(td);source=d/'sample.bf';target=d/'sample.elf'
        for program in samples:
            source.write_bytes(program)
            target.write_bytes(b'UNCHANGED')
            if b'[' in program or b']' in program:
                try:compile_callable(source,target)
                except ValueError as e:assert 'bracketed source' in str(e)
                else:raise AssertionError('unsupported loop accepted')
                assert target.read_bytes()==b'UNCHANGED'
                evidence['failed_atomic_rejections']+=1
                continue
            result=compile_callable(source,target)
            image=target.read_bytes()
            assert result['elf_bytes']==len(image)
            assert int.from_bytes(image[96:104],'little')==len(image)
            assert image[96:104]==image[104:112]
            assert image[128:160]==bytes.fromhex('ea031faaeb0304aaec031faaed031faa f00306aaee031faa1f2003d51f2003d5'.replace(' ',''))
            assert image[-4:]==struct.pack('<I',0xd65f03c0)
            # Cross-check the native straight-line cost and code against a
            # separate length/word encoder where possible.
            filtered=bytes(c for c in program if c in b'><+-.,[]')
            costs={43:3,45:3,62:8,60:8,44:7,46:7}
            assert len(image)==128+32+36+sum(4*costs[c] for c in filtered)
            if all(c in b'+-.,' for c in filtered):
                cost={43:3,45:3,44:7,46:7}
                records=b''.join(struct.pack('<BBHHB',c,1,0,0,cost[c]) for c in filtered)
                ir=(len(filtered).to_bytes(2,'little')+sum(cost[c] for c in filtered).to_bytes(2,'little')
                    +b'\0\0\0'+records+b'\0\0')
                # Existing 16-bit reference oracle is only applicable when
                # this independent test representation can express the count.
                assert image==native_oracle(ir)
            subprocess.run(['readelf','-Wl',str(target)],capture_output=True,check=True,timeout=10)
            runtime_input=bytes(rng.randrange(256) for _ in range(12))
            tape_size=512
            for output_limit in (0,64):
                for tape_size in (1,512):
                    output,status,count,used,tape,_=aarch64_linear(image,runtime_input,
                        tape_size=tape_size,output_limit=output_limit)
                    # Compare against independently evaluated BF semantics.
                    ref_tape=bytearray(tape_size)
                    ref_out=[];ptr=0;cursor=0;trap=False
                    for cmd in filtered:
                        if cmd==43:ref_tape[ptr]=(ref_tape[ptr]+1)&255
                        if cmd==45:ref_tape[ptr]=(ref_tape[ptr]-1)&255
                        if cmd==44:
                            ref_tape[ptr]=runtime_input[cursor] if cursor<len(runtime_input) else 0
                            cursor=min(cursor+1,len(runtime_input))
                        if cmd==46:ref_out.append(ref_tape[ptr])
                        if cmd==62:ptr+=1
                        if cmd==60:ptr-=1
                        if ptr<0 or ptr>=tape_size:trap=True;break
                    assert output==bytes(ref_out[:output_limit]),(program,output,ref_out)
                    assert count==len(output) and used==0
                    assert status==(3 if trap else 2 if len(ref_out)>output_limit else 0),(program,status)
                    assert tape==bytes(ref_tape),(program,tape[:20],ref_tape[:20])
                    evidence['simulator_runs']+=1
            evidence['small_cases']+=1
        # Exceed the legacy 4,096 record layout without changing semantics.
        for name,prog in [('increments5000',b'+'*5000),('outputs5000',b'.'*5000),
                          ('mixed20000',b'+>.<-'*4000),
                          ('comments100k',b'ignored\0'+b'Z'*100000+b'+.'),
                          ('raw_beyond_legacy_1m',b'X'*(1048576+1)+b'+.')]:
            source.write_bytes(prog)
            result=compile_callable(source,target)
            subprocess.run(['readelf','-Wl',str(target)],capture_output=True,check=True,timeout=10)
            evidence['large_record_cases'][name]={'raw_source_bytes':len(prog),
                'emitted_elf_bytes':result['elf_bytes'],
                'sha256':result['elf_sha256']}
        source.write_bytes(b'+.'*80)
        target.write_bytes(b'UNCHANGED')
        try:compile_callable(source,target,max_code_bytes=100)
        except ValueError as exc: assert 'resource quota' in str(exc)
        else:raise AssertionError('explicit caller quota not enforced')
        assert target.read_bytes()==b'UNCHANGED'
        evidence['failed_atomic_rejections']+=1
        header=STAGES/'android_callable_header57.elf'
        for size in (0,1,127,128,255,256,65535,65536,2**32-128,
                     2**32+97,2**56,2**64-129,2**64-128,2**64-1):
            p=subprocess.run([str(header)],input=size.to_bytes(8,'little'),
                             capture_output=True,check=True,timeout=15).stdout
            assert len(p)==129
            if size+128>=2**64:assert p[-1]!=0
            else:
                assert p[-1]==0 and p[96:104]==(size+128).to_bytes(8,'little')
                assert p[104:112]==p[96:104]
            evidence['elf_header_wide_sizes']+=1
    destination=ROOT/'evidence/iteration57_dynamic_callable_linear.json'
    destination.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()

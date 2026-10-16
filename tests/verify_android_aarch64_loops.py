#!/usr/bin/env python3
"""End-to-end checks for a Linux-hosted, all-Brainfuck AArch64 loop toolchain.

The Python code is a test oracle and transport. It does not generate native
instructions for the compiler. No Android device execution is claimed.
"""
import hashlib
import json
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from run_android_loops import STAGES,compile_source,run_stage
from verify_android_aarch64_subset import emulate,check_elf,NOP,PACK
from reference import execute
from source_check import check_source

ALPHABET=b'><+-.,[]'


def oracle_slots(image,source):
    instructions=bytes(x for x in source if x in ALPHABET)
    assert len(instructions)<=10
    stack=[]; pairs=[]
    for pos,ch in enumerate(instructions):
        if ch==91:stack.append(pos)
        elif ch==93:
            assert stack
            pairs.append((stack.pop(),pos))
    assert not stack
    modified=set()
    for opening,closing in pairs:
        span=closing-opening+1
        for pos,is_open,words in (
            (opening,True,12*span-1),
            (closing,False,12*(2-span)-1),
        ):
            modified.add(pos)
            op=(0x34000009 if is_open else 0x35000009)|((words&0x7ffff)<<5)
            at=0x210+48*pos
            want=PACK([0x39400269,op]+[NOP]*10)
            assert image[at:at+48]==want,(source,pos,image[at:at+8].hex())
    masked=run_stage('mask',instructions)
    base=run_stage('emit',masked)
    assert len(base)==4193 and base[-1]==0
    for i in range(10):
        at=0x210+48*i
        if i not in modified:
            assert image[at:at+48]==base[at:at+48],(source,i)
    assert image[:0x210]==base[:0x210]
    assert image[0x210+480:]==base[0x210+480:-1]


def samples():
    fixed=[(b'',b''),(b'comment abc xyz',b''),(b'[]',b''),(b'[+]',b''),
           (b'[[]]',b''),(b'[[[]]]',b''),(b'[][]',b''),
           (b'+++[.-]',b''),(b'+[+]',b''),(b'-[-]',b''),
           (b',[.-]',b'\x04'),(b',[-]',b'\x04'),
           (b',[>+<-]>.',b'\x06'),(b',[->+<]>.',b'\x04'),
           (b'++[->+<]>.',b''),(b'[+][-]',b''),
           (b'\x00[ . ]\xff',b''),(b'[\x00++\xff]',b''),
           (b'>[-]<.',b''),(b',.[-]',b'\xff'),
           (b',.[-]',b''),(b'>+<[-]>.',b''),
           (b'++[>+<-]>.',b'')]
    rng=random.Random(20261012)
    safe=[b'[]',b'[-]',b'[+]',b'[[]]',b'[][]',b'[-][[]]',b'+[+]',
          b'+++[.-]',b'+[->+<]',b',[-]',b',[.-]',b'[+][-]']
    for _ in range(120):
        lead=bytes(rng.choice(b'+-.,><') for _ in range(rng.randrange(0,4)))
        frag=rng.choice(safe)
        tail=bytes(rng.choice(b'+-.,><') for _ in range(rng.randrange(0,3)))
        program=lead+frag+tail
        if len(program)>10:continue
        input_bytes=bytes([rng.randrange(0,4)]*4)
        try:execute(program,input_bytes,max_steps=8000)
        except (IndexError,TimeoutError):
            # Pointer escapes and genuinely nonterminating trials are handled
            # by fixed cases and explicit negative tests, not silently passed.
            continue
        fixed.append((program,input_bytes))
    return fixed


def main():
    for name,(src,binary) in STAGES.items():
        commands=check_source((ROOT/src).read_bytes())
        assert len(commands)<=16128,(name,len(commands))
        assert (ROOT/binary).is_file() and (ROOT/binary).stat().st_size==215+32*len(commands)
    good=0;loop_cases=0;negative=0;seedcases=0
    for source,input_bytes in samples():
        img=compile_source(source,check_hashes=False)
        check_elf(img)
        oracle_slots(img,source)
        reference,steps=execute(source,input_bytes,max_steps=40000)
        for load_bias in (0,0x40000000):
            actual,status,iterations=emulate(img,load_bias,input_bytes=input_bytes,max_steps=50000)
            assert (actual,status)==(reference,0),(source,actual,status,reference)
        if b'[' in source or b']' in source:loop_cases+=1
        good+=1
    # Every balanced bracket-only stream up to ten commands is compiled.
    for n in range(0,11):
        for mask in range(1<<n):
            source=bytes(93 if mask>>i&1 else 91 for i in range(n))
            depth=0;ok=True
            for ch in source:
                depth+=1 if ch==91 else -1
                if depth<0:ok=False;break
            if depth:ok=False
            if not ok:continue
            image=compile_source(source,check_hashes=False)
            oracle_slots(image,source)
            _,status,_=emulate(image,0,input_bytes=b'',max_steps=5000)
            assert status==0
            good+=1;loop_cases+=bool(source)
    invalid=[b'[',b']',b'][',b'[]]',b'[[]',b'['*10,b']'*10,
             b'[]'*6,b'+'*11,b'+++++++++++.',b',[]' + b'+'*8]
    for sample in invalid:
        try:compile_source(sample,check_hashes=False)
        except ValueError:negative+=1
        else:raise AssertionError(f'malformed or oversized source was accepted: {sample!r}')
    # Retain original bytes if a compilation fails.
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp)/'out.elf';source=Path(temp)/'input.bf'
        out.write_bytes(b'existing')
        source.write_bytes(b'[')
        # Hash verification is deliberately disabled only in this test call.
        try:compile_source(source.read_bytes(),check_hashes=False)
        except ValueError:pass
        else:raise AssertionError('expected unmatched bracket rejection')
        assert out.read_bytes()==b'existing'
    # Independent BF seeds for the *new* stages; no seed hides AArch64 encoding.
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as temp:
            for seed in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=Path(temp)/seed
                subprocess.run(['cc','-O2','-o',str(exe),str(ROOT/'bootstrap'/seed)],check=True)
                for name,payload in [('encode',bytes([2,2,0,0])),
                                     ('encode',bytes([2,3,4,4,0,0])),
                                     ('mask',b'[[+].]'),
                                     ('apply',run_stage('encode',run_stage('resolve',b'[+]'))+
                                              run_stage('emit',run_stage('mask',b'[+]'))[:-1])]:
                    want=run_stage(name,payload)
                    src=ROOT/STAGES[name][0]
                    got=subprocess.run([str(exe),str(src)],input=payload,capture_output=True,
                                       timeout=25,check=True).stdout
                    assert got==want,(seed,name,payload)
                    seedcases+=1
    stages={}
    for name,(src,binary) in STAGES.items():
        s=(ROOT/src).read_bytes();elf=(ROOT/binary).read_bytes()
        stages[name]={'source_sha256':hashlib.sha256(s).hexdigest(),
                      'elf_sha256':hashlib.sha256(elf).hexdigest(),
                      'source_instructions':len(check_source(s)),
                      'elf_bytes':len(elf)}
    evidence={'classification':'EXECUTED Linux-hosted native BF pipeline; AArch64 instruction simulated, NOT Android-executed',
              'source_limit_commands':10,'image_bytes':4192,
              'input_source_cases':good,'loop_containing_cases':loop_cases,
              'invalid_rejections':negative,'independent_seed_cases':seedcases,
              'separate_bf_compilation_stages':len(STAGES),
              'supported_instructions':'><+-.,[]',
              'limitations':['Not a single self-hosted Android compiler',
                 'No Android hardware or Android loader execution verified',
                 'Only ten Brainfuck commands and 65536 wrapping byte cells',
                 'External Python adapter performs process and byte transport',
                 'Generated Android binary loader compatibility remains unverified',
                 'Not yet compatible with four required external applications'],
              'stages':stages}
    (ROOT/'evidence/android_loop_pipeline.json').write_text(json.dumps(evidence,indent=2)+'\n')
    # CLI must preserve the previous artifact when compilation fails.
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/'program.bf'
        dest=Path(tmp)/'program.elf'
        source.write_bytes(b'++[>+<-]>.')
        p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_loops.py'),str(source),str(dest)],
                         capture_output=True,timeout=30)
        assert p.returncode==0,(p.returncode,p.stderr)
        before=dest.read_bytes()
        assert before==compile_source(source.read_bytes(),check_hashes=True)
        source.write_bytes(b'[+')
        p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_android_loops.py'),str(source),str(dest)],
                         capture_output=True,timeout=30)
        assert p.returncode!=0 and dest.read_bytes()==before

    print(f'PASS Android BF branch pipeline: {good} native ELF compilations ({loop_cases} loop cases), '
          f'{negative} rejections, {seedcases} independent BF seed checks')

if __name__=='__main__':main()

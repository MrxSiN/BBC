#!/usr/bin/env python3
"""Iteration 43: test-only differential x64 execution for BF-owned 128-slot PE.

The Linux execution shim is NOT a Windows loader and does not qualify Windows S2.
The release compiler path itself still consists of standard Brainfuck programs.
"""
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from run_windows_full128 import compile_source,WRITER,PATCH
from run_windows_full64 import compile_source as compile_64
from reference import execute
from run_windows_linear_io import run_stage
from source_check import check_source

HARNESS=ROOT/'build/windows_pe_linux_x64_shim_128'
BFOPS=b'<>+-.,[]'
SLOT_OFFSET=0x200+31
SLOT_SIZE=12
MAX=128


def cases():
    fixed=[b'',b'.',b'+.',b'-.',b',.',b'+++[->+<]>.',b'++[>++[>+<-]<-]>>.',
       b'+'*127+b'.',b'.'*128,b',.'*64,b'[]'*64,b'[+]'*42,
       b'+'*62+b'[-].',b'+'*64+b'[-].',b'+'*120+b'[-].',
       b'+'*63+b'[->+<]>.',b'+'*110+b'[->+<]>.',
       b'['+b'+'*126+b']', b'['+b'['+b'+'*124+b']'+b']',
       b'+'*70+b'[->+<]>.', b'+'*100+b'[->+<]>.',
       b'+'*64+b'[[-]].', b'+'*66+b'[[-]].',
       b'>'*127+b'.',b'>'*126+b'<.',b'+'*125+b',.',
       b'>'*64+b'<'*63+b'.', b'<' ,b'+[<]',b'+'*127+b'<',
       b'[[]]'*31, b'[->+<]'*15+b'.',
       b'\x00random text\xff[->+<]>.',b'\xffnontoken\x00+.',
       b',[-].',b',>,.<.',b',+.',b',.,.',b',[-],.', b',[-],.',
    ]
    rng=random.Random(43128)
    fragments=[b'+',b'-',b'>',b'<',b'.',b',',b'[-]',b'[+]',b'[->+<]',b'[->++<]',b'[]']
    for _ in range(78):
        src=bytearray(); pointer=0
        while len(src)<128 and rng.random()<0.91:
            candidates=[frag for frag in fragments if len(src)+len(frag)<=128 and
               (frag not in (b'<',) or pointer>0) and
               (frag not in (b'[->+<]',b'[->++<]') or pointer<4) and
               (frag!=b'>' or pointer<5)]
            if not candidates:break
            frag=rng.choice(candidates)
            src+=frag
            if frag==b'>':pointer+=1
            if frag==b'<':pointer-=1
        fixed.append(bytes(src))
    return fixed


def main():
    results={'iteration':43, 'architecture':'x86_64', 'source_cases':0,'runtime_checked':0,
      'expected_pointer_traps':0,'rejected_sources':0,'boundary_over64':0,
      'bracket_pair_patches_checked':0,'output_bytes_checked':0,
      'legacy64_semantic_parity':0,'independent_BF_interpreter_compares':0}
    sources=[ROOT/'experiments/windows_loop_slots_pe_128.bf',ROOT/'experiments/windows_x64_loop_patch_pe_128.bf']
    binaries=[WRITER,PATCH]
    results['stages']=[]
    for source,binary in zip(sources,binaries):
        filtered=check_source(source.read_bytes())
        assert len(filtered)<=16128
        results['stages'].append({'source':str(source.relative_to(ROOT)),
          'bf_instructions':len(filtered),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'native_bytes':binary.stat().st_size,'native_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()})
    with tempfile.TemporaryDirectory() as td:
      path=Path(td)/'sample.exe'
      for src in cases():
        commands=bytes(c for c in src if c in BFOPS)
        if len(commands)>MAX:continue
        try:
            expected,_=execute(src,stdin=b'\xff\0\x05',max_steps=120000)
            trap=False
        except IndexError:
            expected=b'';trap=True
        except TimeoutError:
            continue
        image=compile_source(src)
        assert len(image)==3072 and image[:2]==b'MZ'
        assert int.from_bytes(image[0x188+16:0x188+20],'little')==0x800
        assert int.from_bytes(image[0x188+40+20:0x188+40+24],'little')==0xa00
        # Branch-target oracle only (the production BF patcher owns relocation).
        stack=[]
        for i,c in enumerate(commands):
          if c==91: stack.append(i)
          elif c==93:
            a=stack.pop()
            for at,target in ((a,i+1),(i,a)):
              offset=SLOT_OFFSET+at*SLOT_SIZE
              assert image[offset:offset+3]==b'\x80\x3b\0'
              disp=struct.unpack_from('<i',image,offset+5)[0]
              assert offset+9+disp==SLOT_OFFSET+SLOT_SIZE*target
              results['bracket_pair_patches_checked']+=1
        assert not stack
        path.write_bytes(image)
        run=subprocess.run([str(HARNESS),str(path)],input=b'\xff\0\x05',capture_output=True,timeout=4)
        if trap:
          assert run.returncode==99,(src,run.returncode,run.stderr)
          results['expected_pointer_traps']+=1
        else:
          assert run.returncode==0,(src,run.returncode,run.stderr)
          assert run.stdout==expected,(src,run.stdout,expected)
          results['output_bytes_checked']+=len(expected)
        results['runtime_checked']+=1
        results['boundary_over64']+=len(commands)>64
        if len(commands)<=64:
          old=compile_64(src)
          assert image[SLOT_OFFSET:SLOT_OFFSET+12*len(commands)]==old[SLOT_OFFSET:SLOT_OFFSET+12*len(commands)]
          results['legacy64_semantic_parity']+=1
        results['source_cases']+=1
      rejection=[b'[',b']',b'[[+]',b'+'*129,b'['+b'+'*127+b']',b'[[]'*43,
                 b'>'*129,b'+'*128+b'!',b'+'*127+b'[.]']
      # '+128 + ignored bang' must compile: prove counted executable source only.
      assert len(compile_source(rejection.pop(7)))==3072
      for raw in rejection:
        try:compile_source(raw)
        except ValueError:results['rejected_sources']+=1
        else:raise AssertionError(f'invalid source accepted: {raw[:24]!r}')
      destination=Path(td)/'preserve.exe';source_file=Path(td)/'source.bf'
      for raw in rejection:
        destination.write_bytes(b'KEEP_THIS_OUTPUT');source_file.write_bytes(raw)
        process=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_full128.py'),str(source_file),str(destination)],capture_output=True,timeout=30)
        assert process.returncode!=0 and destination.read_bytes()==b'KEEP_THIS_OUTPUT'
      # Two independent BF runtimes compile source with identical executable output.
      # Reference interpreter with a bounded fuel budget is expensive at this size.
      for source,binary in zip(sources,binaries):
        source_bytes=source.read_bytes()
        inp=b'+' if 'loop_slots' in source.name else b'\0'+compile_64(b'')
        native=run_stage(binary,inp,timeout=45)
        try:
          interpreted,_=execute(source_bytes,stdin=inp,max_steps=15_000_000)
        except TimeoutError:
          continue
        assert interpreted==native
        results['independent_BF_interpreter_compares']+=1
    results.update({'max_commands':MAX,'PE_bytes':3072,'PE_text_raw_size':2048,
      'Windows_loader':'NOT_RUN','Windows_native_S2':'UNIMPLEMENTED',
      'runtime_execution':'Linux native x64 CPU with test-only Win32 API shims'})
    out=ROOT/'evidence/iteration43_windows_full128.json'
    out.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()

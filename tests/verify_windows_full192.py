#!/usr/bin/env python3
"""Iteration 44: offline x64 differential tests for BF-owned PE192 compilation.

Runs generated x64 instructions on Linux with test-only Win32 shims.
This cannot substitute for Windows loader/real API execution.
"""
from __future__ import annotations
import hashlib, json, random, struct, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from run_windows_full192 import compile_source, WRITER,PATCH
from run_windows_full128 import compile_source as compile_128
from run_windows_linear_io import run_stage
from reference import execute
from source_check import check_source
from transport import encode_source,extract_artifact

HARNESS=ROOT/'build/windows_pe_linux_x64_shim_192'
OPS=b'<>+-.,[]';MAX=192;SIZE=3584;SLOT=12;START=0x200+31

def cases():
    fixed=[b'',b'.',b'+.',b'-.',b',.',b',[-].',b'+++[->+<]>.',
      b'++[>++[>+<-]<-]>>.',b'+'*191+b'.',b'.'*192,b',.'*96,
      b'[]'*96,b'['*96+b']'*96,b'['+b'+'*190+b']',
      b'+'*184+b'[->+<]>.',b'+'*188+b'[-].',
      b'+'*127+b'[->+<]>.',b'+'*190+b'<.',
      b'>'*191+b'.',b'>'*191+b'<',b'<',b'+[<]',
      b'['*50+b']'*50+b'.',b'[->+<]'*27+b'.',
      b'ignored \x00 comments\xff [+]',b'\x00\xff+.',
      b'+'*180+b'[,]',b'>'*190+b'<.',b'+'*64+b'[->+<]>.',
      b'+'*64+b'[->+<]'*12+b'.',b'+'*130+b'[[-]].']
    rng=random.Random(44192)
    fragments=[b'+',b'-',b'>',b'<',b'.',b',',b'[-]',b'[+]',b'[->+<]',b'[->++<]',b'[]']
    for _ in range(67):
        src=bytearray();pointer=0
        while len(src)<192 and rng.random()<0.92:
            possible=[f for f in fragments if len(src)+len(f)<=192 and
              (f!=b'<' or pointer>0) and (f not in (b'[->+<]',b'[->++<]') or pointer<4) and
              (f!=b'>' or pointer<5)]
            if not possible:break
            f=rng.choice(possible);src+=f
            if f==b'>':pointer+=1
            if f==b'<':pointer-=1
        fixed.append(bytes(src))
    return fixed

def main():
    result={'iteration':44,'max_commands':MAX,'PE_bytes':SIZE,'PE_text_raw_bytes':0xA00,
      'cases':0,'runtime_executions':0,'source_cases_over128':0,'pointer_traps':0,
      'relocations_checked':0,'old128_used_slot_parity':0,'output_bytes_checked':0,
      'rejections':0,'preserved_outputs':0,'BF_stage_sources':[],
      'execution_kind':'Linux x64 CPU, test-only Win32 API shim',
      'Windows_loader':'NOT_RUN','Windows_native_S2':'UNIMPLEMENTED'}
    for name,path in [('windows_loop_slots_pe_192',WRITER),('windows_x64_loop_patch_pe_192',PATCH)]:
        source=ROOT/f'experiments/{name}.bf'
        raw=source.read_bytes(); filtered=check_source(raw)
        assert len(filtered)<=16128
        regenerated=extract_artifact(run_stage(ROOT/'build/compiler_x86_64_linux.elf',encode_source(raw)))
        assert regenerated==path.read_bytes()
        result['BF_stage_sources'].append({'path':str(source.relative_to(ROOT)),
          'BF_instructions':len(filtered),'SHA256':hashlib.sha256(raw).hexdigest(),
          'ELF_bytes':len(regenerated),'ELF_SHA256':hashlib.sha256(regenerated).hexdigest()})
    with tempfile.TemporaryDirectory() as td:
      td=Path(td); exe=td/'program.exe'
      for src in cases():
        filtered=bytes(x for x in src if x in OPS)
        if len(filtered)>MAX: continue
        try:expected,_=execute(src,stdin=b'\xff\0\x05',max_steps=180000)
        except IndexError:trap=True;expected=b''
        except TimeoutError:continue
        else:trap=False
        image=compile_source(src)
        assert len(image)==SIZE and image[:2]==b'MZ'
        # PE headers are checked by an independent Linux PE reader below.
        stack=[]
        for i,c in enumerate(filtered):
          if c==91:stack.append(i)
          elif c==93:
            a=stack.pop()
            for at,target in ((a,i+1),(i,a)):
              start=START+at*SLOT
              assert image[start:start+3]==b'\x80\x3b\x00'
              delta=struct.unpack_from('<i',image,start+5)[0]
              assert start+9+delta==START+SLOT*target
              result['relocations_checked']+=1
        assert not stack
        exe.write_bytes(image)
        run=subprocess.run([str(HARNESS),str(exe)],input=b'\xff\0\x05',capture_output=True,timeout=4)
        if trap:
          assert run.returncode==99,(src,run.returncode,run.stderr)
          result['pointer_traps']+=1
        else:
          assert run.returncode==0,(src,run.returncode,run.stderr)
          assert run.stdout==expected,(src,run.stdout,expected)
          result['output_bytes_checked']+=len(expected)
        result['runtime_executions']+=1
        if len(filtered)>128:result['source_cases_over128']+=1
        if len(filtered)<=128:
          earlier=compile_128(src)
          assert earlier[START:START+len(filtered)*SLOT]==image[START:START+len(filtered)*SLOT]
          result['old128_used_slot_parity']+=1
        result['cases']+=1
      rejected=[b'[',b']',b'[[+]',b'+'*193,b'['+b'+'*191+b']',
                b'>'*193,b'+'*191+b'[.]',b'[[]'*65]
      source_path=td/'source.bf'; dest=td/'existing.exe'
      for raw in rejected:
        try:compile_source(raw)
        except ValueError:result['rejections']+=1
        else:raise AssertionError(f'accepted invalid source: {raw[:16]!r}')
        dest.write_bytes(b'PROTECT');source_path.write_bytes(raw)
        cli=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_full192.py'),
                            str(source_path),str(dest)],capture_output=True,timeout=25)
        assert cli.returncode!=0 and dest.read_bytes()==b'PROTECT'
        result['preserved_outputs']+=1
      assert len(compile_source(b'+'*192+b'ignored!'))==SIZE
    out=ROOT/'evidence/iteration44_windows_full192.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

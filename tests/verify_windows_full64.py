#!/usr/bin/env python3
"""Offline differential/oracle checks for Brainfuck-owned x64 loop PE compilation.

A test oracle may calculate x64 jumps independently; shipping compiler stages
remain standard BF. This is not Windows-native execution proof.
"""
from pathlib import Path
import hashlib
import json
import random
import struct
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests'),str(ROOT/'tools')]
from run_windows_full64 import compile_source as compile_full, WRITER,PATCH
from run_windows_linear_io import compile_source as compile_six,run_stage
from run_windows_loop_records import produce_records,ENCODER,METADATA,PAIRS
from reference import execute
from transport import encode_source,extract_artifact
from source_check import check_source

SOURCES=('experiments/windows_x64_loop_rel32.bf',
         'experiments/windows_loop_slots_pe_64.bf',
         'experiments/windows_x64_loop_patch_pe.bf')
BINARIES=(ENCODER,WRITER,PATCH)
BF_OPS=b'<>+-.,[]'
SLOT_OFFSET=0x200+31
SLOT_WIDTH=12
BRACKET_PREFIX={91:bytes.fromhex('803b000f84'),93:bytes.fromhex('803b000f85')}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def reference_image(program):
    """Test-only expected slot relocations; not used in compilation."""
    commands=bytes(c for c in program if c in BF_OPS)
    baseline=bytearray(run_stage(WRITER,commands)[:-1])
    stack=[];pairs=[]
    for i,c in enumerate(commands):
        if c==91:stack.append(i)
        if c==93:
            assert stack
            pairs.append((stack.pop(),i))
    assert not stack
    for a,b in pairs:
        opener=12*(b-a)+3
        closer=-12*(b-a)-9
        for i,kind,displacement in ((a,91,opener),(b,93,closer)):
            start=SLOT_OFFSET+i*SLOT_WIDTH
            baseline[start:start+SLOT_WIDTH]=BRACKET_PREFIX[kind]+struct.pack('<i',displacement)+b'\x90'*3
    return bytes(baseline),len(pairs)

def random_valid(rng):
    length=rng.randrange(0,65)
    out=bytearray();depth=0
    for i in range(length):
        remaining=length-i
        ops=b'+-<>.,'
        if depth and remaining<=depth: choice=93
        else:
            candidates=list(ops)
            if depth<15 and remaining>depth+1:candidates.extend([91,91])
            if depth:candidates.extend([93,93])
            choice=rng.choice(candidates)
        if choice==91:depth+=1
        if choice==93:depth-=1
        out.append(choice)
    assert depth==0
    return bytes(out)

def main():
    compilation=[]
    for src,path in zip(SOURCES,BINARIES):
        pure=check_source((ROOT/src).read_bytes())
        output=run_stage(ROOT/'build/compiler_x86_64_linux.elf',encode_source((ROOT/src).read_bytes()),timeout=45)
        assert extract_artifact(output)==path.read_bytes(),src
        compilation.append({'source':src,'instructions':len(pure),'sha256':sha((ROOT/src).read_bytes()),'native_bytes':path.stat().st_size,'native_sha256':sha(path.read_bytes())})
    fixed=[b'',b'[]',b'[[]]',b'[[[]]]',b'+++[->+<]>.',b'[+][+]',b'++[->+<]>.',
           b'+[,.-]',b',[-].',b'[-]',b'[>]',b'[<]',b'[->+++<]',
           b'['+b'+'*62+b']',b'+'*31+b'['+b'+'*30+b']',b'.'*64,
           b',.'*32,b'[+]'*21,b'[]'*32,b'+'*64,
           b'Ignored raw\x00 comment <does not mean comment>\xff[+]',
           b'++\x00hello world\xff[->+<]>.']
    # BF ignores noninstruction characters, including NUL/FF, but literal BF
    # characters in ordinary prose are instructions. The fixture below uses
    # only ignored characters in the comment portion.
    fixed[-2]=b'ignored \x00 text \xff [+]'
    rng=random.Random(410041)
    programs=fixed+[random_valid(rng) for _ in range(230)]
    n_pairs=0;unchanged=0;ref_runs=0
    for src in programs:
        commands=bytes(c for c in src if c in BF_OPS)
        assert len(commands)<=64
        actual=compile_full(src)
        expected,pairs=reference_image(src)
        assert actual==expected, (src,sha(actual),sha(expected))
        assert len(actual)==2048 and actual[:2]==b'MZ'
        n_pairs+=pairs
        for i,c in enumerate(commands):
            if c in (91,93):
                start=SLOT_OFFSET+i*SLOT_WIDTH
                rel=struct.unpack_from('<i',actual,start+5)[0]
                target=start+9+rel
                assert SLOT_OFFSET<=target<=SLOT_OFFSET+SLOT_WIDTH*64
                assert (target-SLOT_OFFSET)%SLOT_WIDTH==0
        if not pairs:
            assert actual==compile_six(src)
            unchanged+=1
        # Reference program execution is an oracle for source semantics,
        # not evidence that the generated PE was executed on Windows.
        if ref_runs<70:
            try:execute(src,stdin=b'\x00\xff',max_steps=10000)
            except (IndexError,TimeoutError):pass
            else:ref_runs+=1
    rejections=[b'[',b']',b'[+',b'+]',b'[[]',b'[]]',b'+'*65,b'['+b'+'*63+b']',b'['*33+b']'*33]
    for raw in rejections:
        try:compile_full(raw)
        except ValueError:pass
        else:raise AssertionError(f'invalid program accepted {raw!r}')
    with tempfile.TemporaryDirectory() as td:
        src_path=Path(td)/'source.bf';output=Path(td)/'program.exe'
        for raw in rejections:
            src_path.write_bytes(raw);output.write_bytes(b'PRESERVE')
            p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_full64.py'),str(src_path),str(output)],capture_output=True)
            assert p.returncode and output.read_bytes()==b'PRESERVE'
        src_path.write_bytes(b'++[->+<]>.')
        p=subprocess.run([sys.executable,str(ROOT/'bootstrap/run_windows_full64.py'),str(src_path),str(output)],capture_output=True)
        assert p.returncode==0 and output.read_bytes()==compile_full(src_path.read_bytes())
        p=subprocess.run(['objdump','-p',str(output)],capture_output=True,text=True,check=True).stdout
        for name in ('ExitProcess','GetStdHandle','ReadFile','WriteFile'):
            assert name in p
        assembly=subprocess.run(['objdump','-d','-j','.text','-Mintel',str(output)],capture_output=True,text=True,check=True).stdout
        assert 'je' in assembly and 'jne' in assembly
    # Independent BF reference interpreter comparisons on the small new stages.
    for src in (b'[]',b'[[]]',b'+++[->+<]>.',b'[+][+]'):
        commands=bytes(c for c in src if c in BF_OPS)
        a=run_stage(METADATA,commands);b=run_stage(PAIRS,a)
        expected=run_stage(ENCODER,b)
        actual,steps=execute((ROOT/SOURCES[0]).read_bytes(),stdin=b,max_steps=15_000_000)
        assert actual==expected,(src,steps)
    assert run_stage(ENCODER,b'\x00\x01')[-1]==1
    # Full PE generation by the BF patcher must be identical even for a
    # no-relocation stream; this catches tail copying and NUL preservation.
    image=compile_six(b',.'); out=run_stage(PATCH,b'\x00'+image)
    assert out==image+b'\x00'
    result={'iteration':41,'maturity':'LINUX_EXECUTED_BF_ALL_EIGHT_PE_WINDOWS_LOADER_NOT_RUN',
      'program_cases':len(programs),'checked_loop_pairs':n_pairs,
      'linear_byte_identical_cases':unchanged,'reference_BF_execution_cases':ref_runs,
      'invalid_rejections':len(rejections),'atomic_preservation_rejections':len(rejections),
      'independent_BF_interpreter_compares':4,'source_stages':compilation,
      'max_commands':64,'PE_bytes':2048,'Windows_loader':'NOT_RUN',
      'Windows_native_S2':'UNIMPLEMENTED'}
    (ROOT/'evidence/iteration41_windows_full64.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

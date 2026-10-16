#!/usr/bin/env python3
"""Development-only BF-source authoring; emitted BF owns PE displacement patching.

Input: repeated { tag, one-based slot position, signed rel32 bytes }, zero
terminator, then a complete 3072-byte BF-generated base PE image. Output:
3072 patched PE bytes followed by one zero status byte. The caller must
validate the records came from BF pair/encoding stages and positions 1..64.
"""
from pathlib import Path
from author_windows_linear_io import BF
ROOT=Path(__file__).resolve().parents[1]
BASE=64
ROW=10
OUTPUTBASE=BASE+ROW
PREFIX=0x200+31
SLOTS=128
TAIL=3072-PREFIX-SLOTS*12

def generate():
 b=BF()
 b.at(0);b.op(',')
 b.begin(0)
 b.at(2);b.op(',')
 b.copy(2,30,31)
 b.copy(30,BASE,31)
 b.at(BASE)
 # Forward walker transfers a decreasing position across 10-cell rows.
 # Cell +9 is a breadcrumb for the return walk to row zero.
 b.op('[-[->>>>>>>>>>+<<<<<<<<<<]>>>>>>>>>+>]')
 b.op('>+') # mark slot as patched
 b.op('>,>,>,>,') # four BF input bytes -> rel32 little endian fields
 b.op('<<<<<'+'<[-<<<<<<<<<<]>') # backtrack cleared breadcrumbs to base
 b.at(0);b.op(',')
 b.end(0)
 # Every admitted slot is processed; row128 marker stays zero.
 for i in range(SLOTS):b.add(OUTPUTBASE+i*ROW+6,1)
 b.at(0);b.op(',.'*PREFIX)
 b.begin(OUTPUTBASE+6)
 # x64 branch slot: cmp r/m8,imm8 (3) + Jcc rel32 (6) + NOPs (3).
 for _ in range(5):b.at(OUTPUTBASE);b.op(',.')
 for i in range(4):
  b.at(OUTPUTBASE);b.op(',')
  b.copy(OUTPUTBASE+1,OUTPUTBASE+8,OUTPUTBASE+9)
  def patch(i=i):
   b.clear(OUTPUTBASE)
   b.copy(OUTPUTBASE+2+i,OUTPUTBASE,OUTPUTBASE+9)
  b.if_once(OUTPUTBASE+8,patch)
  b.at(OUTPUTBASE);b.op('.')
 for _ in range(3):b.at(OUTPUTBASE);b.op(',.')
 b.at(OUTPUTBASE+6);b.op('>'*ROW+']')
 # On exit pointer is at marker of zeroed sentinel row128.
 b.op(',.'*TAIL)
 b.op('.') # sentinel as output status
 program=''.join(b.code)
 comments=("# Windows BF native PE loop displacement patcher\n"
           "# Upstream native BF stages must validate all records\n"
           "# Code copies PE bytes and replaces loop jump displacements\n"
           "# Table has one hundred twenty eight rows with fixed slot ownership\n")
 out=ROOT/'experiments/windows_x64_loop_patch_pe_128.bf'
 out.write_text(comments+program+'\n',encoding='ascii')
 print('BF instructions',len(program),'output',out)
 assert len(program)<16128

if __name__=='__main__':generate()

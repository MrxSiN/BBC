#!/usr/bin/env python3
"""Development-only authoring of standard BF callable AArch64 loop stages.

The generated .bf stages perform runtime source classification, native byte
selection and 64-bit native word accounting. This script is not a compiler
stage or a production dependency.
"""
import struct
from pathlib import Path
from tools.author_android_compact_all8 import BF as Emitter
from tools.author_android_compact_offset_ledger51 import BF as Ledger
from tools.author_dynamic_callable57 import LINEAR

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments'

# An eight-word, PC-relative, signed-64-bit veneer. Registers x17 and x15
# are expendable. Critically, x11 stays the callable ABI tape address.
ADD_X17_X17_X15_SHIFT2 = (0x8b0b094a & ~(31 | (31<<5) | (31<<16))) | 17 | (17<<5) | (15<<16)
VENEER=(0x39400169, 0x350000e9, 0x10000011, 0x5800006f,
        ADD_X17_X17_X15_SHIFT2, 0xd61f0220, 0, 0)
# On a nonzero open cell, the veneer skips directly to these instructions:
# check remaining budget; if zero return status one, otherwise decrement.
# At a zero open cell, the veneer skips the entire body and its close edge.
BUDGET=(0xb50000a6, 0x52800020, 0xcb060201, 0xf90000ed,
        0xd65f03c0, 0xd10004c6)
TEMPLATES={op:struct.pack('<'+'I'*len(words),*words) for op,words in LINEAR.items()}
TEMPLATES[ord('[')]=struct.pack('<14I',*(VENEER+BUDGET))
TEMPLATES[ord(']')]=struct.pack('<8I',*(VENEER[:1]+(0x340000e9,)+VENEER[2:]))
assert all(len(t)%4==0 and len(t)<=255 for t in TEMPLATES.values())

b=Emitter();b.goto(0);b.raw(',[');b.goto(1);b.raw(',')
for op in b'+-><.,[]':
    b.compare(op)
    b.emit_data(bytes((1,len(TEMPLATES[op])))+TEMPLATES[op])
    b.end_compare()
b.goto(0);b.raw(',]');b.emit_data(b'\0');b.goto(8);b.raw('.')
source=''.join(b.code)
(OUT/'android_callable_slots58.bf').write_text(
    '# Standard BF callable native AArch64 with wide relative loop veneers\n'
    '# Source bytes arrive as a presence marker and raw data byte\n'
    '# Each instruction emits one tagged native byte template\n'
    '# Opening loops test tape and enforce the callable execution budget\n'
    '# Closing loops use an eight word wide relocation template\n'
    '# Final zero marker and status complete the code record stream\n'
    +source+'\n')
print('callable slots BF instruction count',len(source),
      'template bytes',{chr(x):len(TEMPLATES[x]) for x in b'+-><.,[]'})

l=Ledger();l.at(0);l.op(',[');l.at(1);l.op(',')
for op in b'+-><.,[]':
    l.eq(1,op);l.set(29,len(TEMPLATES[op])//4)
    if op in b'[]':l.set(26,1 if op==ord('[') else 2)
    l.endeq()
l.at(26);l.op('[');l.at(26);l.op('.');l.emit_position();l.clr(26);l.at(26);l.op(']')
l.at(29);l.op('[');l.op('-');l.inc_word();l.at(29);l.op(']')
l.at(0);l.op(',]');l.set(31,3);l.at(31);l.op('.');l.emit_position()
l.set(31,0);l.at(31);l.op('.');l.at(38);l.op('.')
led=''.join(l.parts)
(OUT/'android_callable_ledger58.bf').write_text(
    '# Standard BF callable AArch64 native word position ledger\n'
    '# All accepted source commands advance the full sixty four bit count\n'
    '# Open bracket is fourteen words and close bracket is eight words\n'
    '# Bracket tags expose eight byte unsigned absolute word positions\n'
    '# Final wide word length and overflow status end the ledger stream\n'
    +led+'\n')
print('callable ledger BF instruction count',len(led))
assert len(source)<=16128 and len(led)<=16128

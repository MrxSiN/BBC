#!/usr/bin/env python3
"""Development-only BF macro author for AArch64 64-bit PC-relative loop jumps.

The emitted standard-BF programs select, emit, count and relocate native words;
this script is NOT called by the user-source compiler.
"""
from pathlib import Path
import sys
import runpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/'experiments'
from tools.author_android_compact_all8 import BF as Emitter, template
from tools.author_android_compact_offset_ledger51 import BF as Ledger

# x9 is the cell-test register.  x10 and x11 are scratch only during branches.
# Each bracket is eight 4-byte words.  The literal holds a signed relative
# displacement in WORDS from the ADR instruction (word two) to its destination.
# ldrb w9,[x19]; cbnz/cbz w9,+28; adr x10,0; ldr x11,+12;
# add x10,x10,x11,lsl #2; br x10; .quad word_delta
# This design is base independent: no absolute dynamic relocation is needed.
LOOP_PREFIX=(0x39400269,0x350000e9,0x1000000a,0x5800006b,0x8b0b094a,0xd61f0140)
import struct

def loop_template(op):
    words=list(LOOP_PREFIX)
    if op==ord(']'):words[1]=0x340000e9
    return struct.pack('<6I2I',*words,0,0)

b=Emitter();b.goto(0);b.raw(',[');b.goto(1);b.raw(',')
for op in b'+-><.,[]':
    b.compare(op)
    t=loop_template(op) if op in b'[]' else template(op)
    b.emit_data(bytes((1,len(t)))+t)
    b.end_compare()
b.goto(0);b.raw(',]');b.emit_data(b'\0');b.goto(8);b.raw('.')
code=''.join(b.code)
(OUT/'android_compact_far_slots53.bf').write_text(
    '# Standard BF dynamic compact AArch64 with PC relative long loop jumps\n'
    '# Input marker one and one source byte for each record then marker zero\n'
    '# Output marker one size byte then native instructions or marker zero status\n'
    '# Bracket slots use eight native words and relative signed word literal\n'+code+'\n')
print('far slots BF instructions',len(code))

b=Ledger();b.at(0);b.op(',[');b.at(1);b.op(',')
for op,words,marker in ((ord('+'),3,0),(ord('-'),3,0),(ord('>'),7,0),(ord('<'),7,0),
                        (ord('.'),10,0),(ord(','),12,0),(ord('['),8,1),(ord(']'),8,2)):
    b.eq(1,op);b.set(29,words)
    if marker:b.set(26,marker)
    b.endeq()
b.at(26);b.op('[');b.at(26);b.op('.');b.emit_position();b.clr(26);b.at(26);b.op(']')
b.at(29);b.op('[');b.op('-');b.inc_word();b.at(29);b.op(']')
b.at(0);b.op(',]');b.set(31,3);b.at(31);b.op('.');b.emit_position();b.set(31,0);b.at(31);b.op('.');b.at(38);b.op('.')
ledger=''.join(b.parts)
(OUT/'android_compact_far_ledger53.bf').write_text(
    '# Standard BF wide native word offset ledger for PC relative loop code\n'
    '# Source bytes are tagged one until terminating zero\n'
    '# Bracket offsets use eight word templates and full 64 bit counters\n'
    '# Emit open tag one close tag two and final tag three and status\n'+ledger+'\n')
print('far ledger BF instructions',len(ledger))

class PatchBF:
    def __init__(self):self.p=0;self.s=[]
    def at(self,n):
        diff=n-self.p
        if diff:self.s.append(('>' if diff>0 else '<')*abs(diff));self.p=n
    def raw(self,v):self.s.append(v)
    def add(self,v):
        v%=256;self.raw('+'*v if v<=128 else '-'*(256-v))
    def clear(self,n):self.at(n);self.raw('[-]')
    def set(self,n,v):self.clear(n);self.at(n);self.add(v)
    def copy(self,a,b):
        self.clear(b);self.clear(90);self.clear(91)
        self.at(a);self.raw('[');self.raw('-');self.at(b);self.raw('+');self.at(90);self.raw('+');self.at(a);self.raw(']')
        self.at(90);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(90);self.raw(']')
    def iszero(self,n):
        self.copy(n,93);self.set(94,1)
        self.at(93);self.raw('[');self.raw('[-]');self.clear(94);self.at(93);self.raw(']')
    def inc64(self,base):
        self.set(75,1)
        for i in range(8):
            self.at(75);self.raw('[');self.raw('-');self.at(base+i);self.raw('+')
            self.iszero(base+i)
            self.at(94);self.raw('[');self.raw('-');self.at(76);self.raw('+');self.at(94);self.raw(']')
            self.at(75);self.raw(']')
            self.at(76);self.raw('[');self.raw('-');self.at(75);self.raw('+');self.at(76);self.raw(']')
        self.at(75);self.raw('[');self.raw('[-]');self.set(82,1);self.at(75);self.raw(']')
    def plusn(self,base,n):
        self.set(70,n);self.at(70);self.raw('[');self.raw('-');self.inc64(base);self.at(70);self.raw(']')
    def neg64(self,base):
        for i in range(8):
            self.copy(base+i,93);self.set(base+i,255)
            self.at(93);self.raw('[');self.raw('-');self.at(base+i);self.raw('-');self.at(93);self.raw(']')
        self.inc64(base)
    def emit_patch(self,pos,delta):
        self.set(81,ord('P'));self.at(81);self.raw('.')
        for i in range(8):self.at(pos+i);self.raw('.')
        for i in range(8):self.at(delta+i);self.raw('.')

# Position stage: one opaque eight-byte native offset per tagged input.
b=PatchBF();b.at(0);b.raw(',[')
for i in range(8):b.at(5+i);b.raw(',');b.copy(5+i,30+i)
b.plusn(30,6)
b.set(81,ord('P'));b.at(81);b.raw('.')
for i in range(8):b.at(30+i);b.raw('.')
b.at(0);b.raw(',]');b.at(82);b.raw('.')
pos=''.join(b.s)
(OUT/'android_compact_far_position53.bf').write_text(
    '# Standard BF owned far branch embedded literal word position\n'
    '# Input marker one plus one eight byte native word index then marker zero\n'
    '# Output modified eight byte index for each input and terminal status byte\n'+pos+'\n')
print('far position BF instructions',len(pos))

# Signed delta stage: one span and a mode bit, with BF-selected adjustments.
# Forward is span plus six words; reverse is complement of span plus one word.
b=PatchBF();b.at(0);b.raw(',[')
b.at(5);b.raw(',') # mode byte: zero forward, one reverse
for i in range(8):b.at(6+i);b.raw(',');b.copy(6+i,30+i)
b.set(70,6)
b.at(5);b.raw('[');b.raw('[-]');b.set(70,1);b.set(71,1);b.at(5);b.raw(']')
b.at(70);b.raw('[');b.raw('-');b.inc64(30);b.at(70);b.raw(']')
b.at(71);b.raw('[');b.raw('-')
for i in range(8):
 b.copy(30+i,93);b.set(30+i,255)
 b.at(93);b.raw('[');b.raw('-');b.at(30+i);b.raw('-');b.at(93);b.raw(']')
b.at(71);b.raw(']')
b.set(81,ord('D'));b.at(81);b.raw('.')
for i in range(8):b.at(30+i);b.raw('.')
b.at(0);b.raw(',]');b.at(82);b.raw('.')
delta=''.join(b.s)
(OUT/'android_compact_far_delta53.bf').write_text(
    '# Standard BF owned relative sixty four bit long branch literal arithmetic\n'
    '# Each input marker one carries mode zero for forward or one for reverse\n'
    '# Then eight little endian bytes carry the positive close minus open span\n'
    '# Forward result span plus six and reverse result negative span minus two\n'
    '# Eight delta bytes per record and one zero terminal status byte\n'+delta+'\n')
print('far delta BF instructions',len(delta))
assert max(len(code),len(ledger),len(pos),len(delta))<=16128

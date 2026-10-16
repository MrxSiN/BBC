#!/usr/bin/env python3
"""Development-only macro author for BF-owned compact AArch64 word offsets.

The emitted .bf program, not Python, classifies source bytes and performs
base-16 64-bit native instruction offset arithmetic. Python is never used to
calculate native offsets on behalf of the compiler in production.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_compact_native_offset_ledger.bf'

class BF:
    def __init__(self):self.p=0;self.parts=[]
    def at(self,i):
        d=i-self.p
        if d:self.parts.append(('>' if d>0 else '<')*abs(d));self.p=i
    def op(self,s):self.parts.append(s)
    def clr(self,i):self.at(i);self.op('[-]')
    def add(self,n):
        n%=256;self.op('+'*n if n<=128 else '-'*(256-n))
    def set(self,i,n):self.clr(i);self.at(i);self.add(n)
    def copy(self,src,tmp,rest):
        self.clr(tmp);self.clr(rest)
        self.at(src);self.op('[');self.op('-');self.at(tmp);self.op('+');self.at(rest);self.op('+');self.at(src);self.op(']')
        self.at(rest);self.op('[');self.op('-');self.at(src);self.op('+');self.at(rest);self.op(']')
    def eq(self,src,target):
        self.copy(src,2,3);self.at(2);self.add(-target)
        self.set(4,1)
        self.at(2);self.op('[');self.op('[-]');self.clr(4);self.at(2);self.op(']')
        self.at(4);self.op('[')
    def endeq(self):self.clr(4);self.at(4);self.op(']')
    def emit_position(self):
        # c10..25 hold 16 base-16 digits of the native 4-byte word offset.
        # c40 is the binary accumulator, c41 restores the original digit.
        for j in range(8):
            self.clr(40);self.clr(41)
            lo=10+2*j;hi=lo+1
            self.at(lo);self.op('[');self.op('-');self.at(40);self.op('+');self.at(41);self.op('+');self.at(lo);self.op(']')
            self.at(41);self.op('[');self.op('-');self.at(lo);self.op('+');self.at(41);self.op(']')
            self.at(hi);self.op('[');self.op('-');self.at(40);self.op('+'*16);self.at(41);self.op('+');self.at(hi);self.op(']')
            self.at(41);self.op('[');self.op('-');self.at(hi);self.op('+');self.at(41);self.op(']')
            self.at(40);self.op('.');self.clr(40)
    def inc_word(self):
        self.set(32,1)
        for i in range(10,26):
            self.at(32);self.op('[');self.op('-')
            self.at(i);self.op('+')
            # Decide BF-owned nibble carry; a nibble only holds values 0..15.
            self.copy(i,33,34);self.at(33);self.add(-16)
            self.set(35,1)
            self.at(33);self.op('[');self.op('[-]');self.clr(35);self.at(33);self.op(']')
            self.at(35);self.op('[');self.op('[-]');self.clr(i);self.at(36);self.op('+');self.at(35);self.op(']')
            self.at(32);self.op(']')
            self.at(36);self.op('[');self.op('-');self.at(32);self.op('+');self.at(36);self.op(']')
        self.at(32);self.op('[');self.op('[-]');self.set(38,1);self.at(32);self.op(']')

b=BF()
b.at(0);b.op(',[')
b.at(1);b.op(',')
# Tags 1/2 denote opening/closing brackets. All positions are in words.
for op,words,marker in ((ord('+'),3,0),(ord('-'),3,0),(ord('>'),7,0),(ord('<'),7,0),
                        (ord('.'),10,0),(ord(','),12,0),(ord('['),3,1),(ord(']'),3,2)):
    b.eq(1,op)
    b.set(19,words)
    if marker:b.set(26,marker)
    b.endeq()
b.at(26);b.op('[')
b.at(26);b.op('.')
b.emit_position()
b.clr(26);b.at(26);b.op(']')
b.at(19);b.op('[');b.op('-');b.inc_word();b.at(19);b.op(']')
b.at(0);b.op(',]')
b.set(31,3);b.at(31);b.op('.')
b.emit_position()
b.set(31,0);b.at(31);b.op('.')
b.at(38);b.op('.')
src=''.join(b.parts)
header=(
    '# Streaming native AArch64 compact code word position ledger\n'
    '# Each input character uses presence marker one then its raw byte\n'
    '# Source instructions are classified by standard Brainfuck only\n'
    '# Native word positions use sixteen base sixteen counter digits\n'
    '# Open bracket emits tag one and eight native word position bytes\n'
    '# Close bracket emits tag two and eight native word position bytes\n'
    '# Final tag three carries the exact native code length in words\n'
    '# Termination emits zero then arithmetic overflow status\n'
)
DEST.write_text(header+src+'\n',encoding='ascii')
print('generated',len(src),'BF instructions',DEST)

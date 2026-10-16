#!/usr/bin/env python3
"""Development-only macro author for standard-BF AArch64 signed imm26 B words."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_compact_branch_words52.bf'
class BF:
 def __init__(self):self.p=0;self.s=[]
 def at(self,i):
  d=i-self.p
  if d:self.s.append(('>' if d>0 else '<')*abs(d));self.p=i
 def raw(self,s):self.s.append(s)
 def add(self,x):
  x%=256;self.raw('+'*x if x<=128 else '-'*(256-x))
 def clr(self,i):self.at(i);self.raw('[-]')
 def set(self,i,x):self.clr(i);self.at(i);self.add(x)
 def cp(self,a,b):
  self.clr(b);self.clr(2);self.clr(3)
  self.at(a);self.raw('[');self.raw('-');self.at(b);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
 def eq(self,a,val):
  self.clr(2);self.clr(3)
  self.at(a);self.raw('[');self.raw('-');self.at(2);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
  self.at(2);self.add(-val);self.set(4,1)
  self.at(2);self.raw('[');self.raw('[-]');self.clr(4);self.at(2);self.raw(']')
  self.at(4);self.raw('[')
 def endeq(self):self.clr(4);self.at(4);self.raw(']')
 def dec_and_borrow(self,a):
  self.at(a);self.raw('-');self.eq(a,255);self.set(22,1);self.endeq()

b=BF()
b.at(0);b.raw(',[')
for i in range(8):b.at(5+i);b.raw(',')
# forward displacement c-o+1. If forward >=2**25 reject.
for i in range(4):b.cp(5+i,13+i)
b.set(23,1)
for i in range(4):
 b.at(23);b.raw('[');b.raw('-');b.at(13+i);b.raw('+');b.eq(13+i,0);b.set(24,1);b.endeq();b.at(23);b.raw(']')
 b.at(24);b.raw('[');b.raw('-');b.at(23);b.raw('+');b.at(24);b.raw(']')
b.at(23);b.raw('[');b.raw('[-]');b.set(26,1);b.at(23);b.raw(']')
# no native span bits above 31
for i in range(4,8):
 b.cp(5+i,34);b.at(34);b.raw('[');b.raw('[-]');b.set(26,1);b.at(34);b.raw(']')
# top byte low 8 must be exactly 0 or1 for positive 26bit branch
b.set(25,1)
for v in (0,1):b.eq(16,v);b.clr(25);b.endeq()
b.at(25);b.raw('[');b.raw('[-]');b.set(26,1);b.at(25);b.raw(']')
# Valid bracket slots imply a distance of at least three native words.
b.clr(25)
for v in (0,1,2):b.eq(5,v);b.set(25,1);b.endeq()
for i in range(1,4):
 b.cp(5+i,34);b.at(34);b.raw('[');b.raw('[-]');b.clr(25);b.at(34);b.raw(']')
b.at(25);b.raw('[');b.raw('[-]');b.set(26,1);b.at(25);b.raw(']')
# reverse displacement = 1 - (close-open) in signed 32-bit.
b.set(28,1)
for i in range(1,4):b.clr(28+i)
b.clr(21)
for i in range(4):
 b.clr(22);b.cp(28+i,17+i)
 b.at(21);b.raw('[');b.raw('-');b.dec_and_borrow(17+i);b.at(21);b.raw(']')
 b.cp(5+i,23)
 b.at(23);b.raw('[');b.raw('-');b.dec_and_borrow(17+i);b.at(23);b.raw(']')
 b.at(22);b.raw('[');b.raw('-');b.at(21);b.raw('+');b.at(22);b.raw(']')
# For negative signed 26 bit, top byte is FF or FE.
b.set(25,1)
b.eq(20,254);b.set(32,0x16);b.clr(25);b.endeq()
b.eq(20,255);b.set(32,0x17);b.clr(25);b.endeq()
b.at(25);b.raw('[');b.raw('[-]');b.set(26,1);b.at(25);b.raw(']')
b.cp(32,20)
b.at(16);b.add(0x14)
# header: tag one then two exact four-byte instruction words.
b.set(33,1);b.at(33);b.raw('.')
for i in list(range(13,17))+list(range(17,21)):b.at(i);b.raw('.')
b.at(0);b.raw(',]')
b.clr(33);b.at(33);b.raw('.');b.at(26);b.raw('.')
code=''.join(b.s)
comment='''# Brainfuck owned compact AArch64 B signed branch word encoding
# Input one marker then eight little endian bytes for closing minus opening
# Output one marker then forward and reverse four byte machine words
# Zero marker and status zero signal success
# A signed twenty six bit branch limit is enforced by BF
# Input spans must include distinct three word bracket slots
'''
DEST.write_text(comment+code+'\n')
print('bf_instructions',len(code))

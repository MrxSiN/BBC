#!/usr/bin/env python3
"""Development-only BF author for full-width compact word-offset subtraction.

The executable .bf, not this macro, subtracts 64-bit compact word positions,
checks unsigned ordering, and emits the exact 64-bit span with both positions.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_compact_span64_52.bf'
class BF:
 def __init__(self):self.p=0;self.s=[]
 def at(self,i):
  d=i-self.p
  if d:self.s.append(('>' if d>0 else '<')*abs(d));self.p=i
 def raw(self,s):self.s.append(s)
 def add(self,n):
  n%=256;self.raw('+'*n if n<=128 else '-'*(256-n))
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
  self.at(a);self.raw('-');self.eq(a,255);self.set(31,1);self.endeq()

b=BF()
b.at(0);b.raw(',[')
for i in range(5,21):b.at(i);b.raw(',')
b.clr(30)
for i in range(8):
 dst=21+i
 b.clr(31)
 b.cp(13+i,dst)
 b.at(30);b.raw('[');b.raw('-');b.dec_and_borrow(dst);b.at(30);b.raw(']')
 b.cp(5+i,29)
 b.at(29);b.raw('[');b.raw('-');b.dec_and_borrow(dst);b.at(29);b.raw(']')
 b.clr(30);b.at(31);b.raw('[->-<]') if False else None
 b.at(31);b.raw('[');b.raw('-');b.at(30);b.raw('+');b.at(31);b.raw(']')
b.at(30);b.raw('[');b.raw('[-]');b.set(32,1);b.at(30);b.raw(']')
b.set(33,1);b.at(33);b.raw('.')
for i in range(5,29):b.at(i);b.raw('.')
b.at(0);b.raw(',]')
b.clr(33);b.at(33);b.raw('.')
b.at(32);b.raw('.')
code=''.join(b.s)
comments='''# BF owned unsigned sixty four bit native compact span subtraction
# Input marker one then open and close native word positions each eight bytes
# Final zero input marker terminates records
# Each output starts with marker one and open close and span as raw bytes
# Final marker zero and status zero mean accepted unsigned ordering
# Underflow is rejected and native position arithmetic is entirely BF owned
'''
DEST.write_text(comments+code+'\n')
print(len(code),DEST)

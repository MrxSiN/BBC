#!/usr/bin/env python3
"""Development-only author for BF-owned native word patch positions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_compact_patch_indices52.bf'
class BF:
 def __init__(self):self.p=0;self.s=[]
 def at(self,i):
  d=i-self.p
  if d:self.s.append(('>' if d>0 else '<')*abs(d));self.p=i
 def raw(self,s):self.s.append(s)
 def add(self,x):
  x%=256;self.raw('+'*x if x<=128 else '-'*(256-x))
 def clear(self,i):self.at(i);self.raw('[-]')
 def set(self,i,x):self.clear(i);self.at(i);self.add(x)
 def cp(self,a,b):
  self.clear(b);self.clear(2);self.clear(3)
  self.at(a);self.raw('[');self.raw('-');self.at(b);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
 def equal0(self,a):
  self.clear(2);self.clear(3)
  self.at(a);self.raw('[');self.raw('-');self.at(2);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
  self.set(4,1)
  self.at(2);self.raw('[');self.raw('[-]');self.clear(4);self.at(2);self.raw(']')
  self.at(4);self.raw('[')
 def endeq(self):self.clear(4);self.at(4);self.raw(']')
 def plus2(self,idx):
  for k in range(2):
   self.set(33,1)
   for i in range(8):
    self.at(33);self.raw('[');self.raw('-');self.at(idx+i);self.raw('+')
    self.equal0(idx+i);self.at(34);self.raw('+');self.endeq()
    self.at(33);self.raw(']')
    self.at(34);self.raw('[');self.raw('-');self.at(33);self.raw('+');self.at(34);self.raw(']')
   self.at(33);self.raw('[');self.raw('[-]');self.set(35,1);self.at(33);self.raw(']')

b=BF();b.at(0);b.raw(',[')
# two 8byte word offsets followed by two fourbyte branch encodings
for i in range(16):b.at(5+i);b.raw(',')
for i in range(8):b.at(21+i);b.raw(',')
for start,word_start in ((5,21),(13,25)):
 b.plus2(start)
 b.set(30,ord('P'));b.at(30);b.raw('.')
 for i in range(8):b.at(start+i);b.raw('.')
 for i in range(4):b.at(word_start+i);b.raw('.')
b.at(0);b.raw(',]')
b.clear(30);b.at(30);b.raw('.');b.at(35);b.raw('.')
code=''.join(b.s)
comment='''# Brainfuck owned native compact relocation word index increment
# Each record carries opening and closing native word positions
# The record also carries two four byte BF produced branch words
# Each output patch position is the bracket word index plus two
# Output records contain tag P and eight position bytes and four word bytes
# Zero tag and status terminate the stream
'''
DEST.write_text(comment+code+'\n')
print('bf_instructions',len(code))

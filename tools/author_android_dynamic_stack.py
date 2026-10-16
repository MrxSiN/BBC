#!/usr/bin/env python3
"""Development-only authoring macro generator for the standard-BF pairing device.
The generated .bf owns tag recognition, match control, and mismatch decisions.
The host is an uninterpreted disk-backed eight-byte LIFO service.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_dynamic_stack_pairs.bf'

class BF:
 def __init__(self):self.p=0;self.code=[]
 def go(self,i):
  d=i-self.p
  if d:self.code.append(('>' if d>0 else '<')*abs(d));self.p=i
 def s(self,x):self.code.append(x)
 def clear(self,i):self.go(i);self.s('[-]')
 def plus(self,n):
  n%=256;self.s('+'*n if n<=128 else '-'*(256-n))
 def out(self,i):self.go(i);self.s('.')
 def get(self,i):self.go(i);self.s(',')
 def const(self,n):
  self.clear(30);self.go(30);self.plus(n);self.s('.');self.clear(30)
 def eq(self,src,n):
  # c22 temporary copy, c25 restorer, c23 boolean flag
  self.clear(22);self.clear(25)
  self.go(src);self.s('[');self.s('-');self.go(22);self.s('+');self.go(25);self.s('+');self.go(src);self.s(']')
  self.go(25);self.s('[');self.s('-');self.go(src);self.s('+');self.go(25);self.s(']')
  self.go(22);self.plus(-n)
  self.clear(23);self.go(23);self.s('+')
  self.go(22);self.s('[');self.s('[-]');self.clear(23);self.go(22);self.s(']')
  self.go(23);self.s('[')
 def endeq(self):self.clear(23);self.go(23);self.s(']')

b=BF()
b.go(21);b.s('+[') # main loop
b.const(ord('R'))
for i in range(9):b.get(i)
b.clear(24);b.go(24);b.s('+')
b.eq(0,1)
b.clear(24)
b.const(ord('P'))
for i in range(1,9):b.out(i)
b.endeq()
b.eq(0,2)
b.clear(24)
b.const(ord('O'))
# Read pop flag into 17 and eight bytes in 9..16
b.get(17)
for i in range(9,17):b.get(i)
# set c18 to 1 to reject unsuccessful pops
b.clear(18);b.go(18);b.s('+')
b.go(17);b.s('[');b.s('[-]');b.clear(18)
b.const(ord('M'))
for i in list(range(9,17))+list(range(1,9)):b.out(i)
b.go(17);b.s(']')
b.go(18);b.s('[');b.s('[-]');b.clear(19);b.go(19);b.s('+');b.go(18);b.s(']')
b.endeq()
b.eq(0,0)
b.clear(24);b.clear(21)
b.endeq()
# unknown tags or missing open are errors, and end main loop
b.go(24);b.s('[');b.s('[-]');b.clear(19);b.go(19);b.s('+');b.go(24);b.s(']')
# On failure, mark c26 before stopping; move it back into status afterwards.
b.go(19);b.s('[');b.s('[-]');b.clear(21);b.go(26);b.s('+');b.go(19);b.s(']')
b.go(21);b.s(']')
b.go(26);b.s('[');b.s('-');b.go(19);b.s('+');b.go(26);b.s(']')
b.const(ord('E'));b.get(18)
# 0 means nonempty; 1 means empty
b.clear(20);b.go(20);b.s('+')
b.go(18);b.s('[');b.s('[-]');b.clear(20);b.go(18);b.s(']')
b.go(20);b.s('[');b.s('[-]');b.clear(19);b.go(19);b.s('+');b.go(20);b.s(']')
b.const(ord('D'));b.out(19)
source=''.join(b.code)
comment=(
 '# Dynamic disk backed bracket matching protocol\n'
 '# The Brainfuck program owns tag decisions and bracket pairing\n'
 '# Host offers byte stack push pop and empty operations only\n'
 '# Events carry a tag and an opaque eight byte code offset\n'
 '# Host device has no nesting limit other than resources\n'
)
DEST.write_text(comment+source+'\n',encoding='ascii')
print('BF commands',len(source))

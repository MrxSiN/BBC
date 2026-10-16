#!/usr/bin/env python3
"""Development-only authoring of standard BF bracket event wire translation.
The executable BF stage, not Python, identifies open and closing bracket events.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class B:
 def __init__(self):self.c=[];self.p=0
 def g(self,i):
  n=i-self.p
  if n:self.c.append(('>' if n>0 else '<')*abs(n));self.p=i
 def w(self,s):self.c.append(s)
 def cl(self,i):self.g(i);self.w('[-]')
 def k(self,n):
  self.cl(30);self.g(30);v=n%256;self.w('+'*v if v<=128 else '-'*(256-v));self.w('.')
 def eq(self,n):
  self.cl(10);self.cl(11)
  self.g(0);self.w('[->+>+<<]');self.g(2);self.w('[-<<+>>]')
  self.g(1);v=(-n)%256;self.w('+'*v if v<=128 else '-'*(256-v))
  self.cl(3);self.g(3);self.w('+')
  self.g(1);self.w('[');self.w('[-]');self.cl(3);self.g(1);self.w(']')
  self.g(3);self.w('[')
 def end(self):self.cl(3);self.g(3);self.w(']')
b=B()
b.g(0);b.w(',[')
for i in range(4,8):b.g(i);b.w(',')
for c,tag in ((91,1),(93,2)):
 b.eq(c);b.k(tag)
 for i in range(4,8):b.g(i);b.w('.')
 for _ in range(4):b.k(0)
 b.end()
b.g(0);b.w(',]')
# Consume the nine-byte original 32-bit scanner footer. The last is status.
for _ in range(8):b.g(20);b.w(',')
b.g(21);b.w(',')
b.k(0);b.g(21);b.w('.')
code=''.join(b.c)
header=(
 '# Standard BF translation of bracket records to opaque eight byte offsets\n'
 '# Input bracket tag with little endian four byte positions\n'
 '# Output event code one for opening two for closing and eight byte positions\n'
 '# The first four offset bytes are preserved and the rest are zero\n'
 '# Input frame footer status is propagated with the closing record\n'
)
p=ROOT/'experiments/android_pair_event_bridge.bf';p.write_text(header+code+'\n')
print('BF',len(code))

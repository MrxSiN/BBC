#!/usr/bin/env python3
"""Development-only static ELF layout author. Runtime ELF lengths are BF-owned.

This author only creates standard BF source. No Python ELF writer runs while
compiling user programs; the BF executable emits the ELF metadata and AArch64
startup/exit instructions, while the host copies opaque code and page padding.
"""
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/android_compact_elf_layout52.bf'
# This freestanding PIE layout isolates tape before code, so ADRP startup is
# constant no matter how much the code segment grows. Android loader unverified.
HEADER=struct.pack('<16sHHIQQQIHHHHHH',b'\x7fELF\2\1\1'+bytes(9),3,183,1,0x20000,64,0,0,64,56,3,0,0,0)
HEADER+=struct.pack('<IIQQQQQQ',1,4,0,0,0,0x1000,0x1000,0x4000)
HEADER+=struct.pack('<IIQQQQQQ',1,6,0,0x4000,0x4000,0,0x10000,0x4000)
HEADER+=struct.pack('<IIQQQQQQ',1,5,0x20000,0x20000,0x20000,0,0,0x4000)
assert len(HEADER)==232
adrp_imm=(1<<21)-28
adrp=0x90000014|(((adrp_imm>>2)&0x7ffff)<<5)|((adrp_imm&3)<<29)
START=struct.pack('<4I',adrp,0x91000294,0xaa1403f3,0xd503201f)
EXIT=struct.pack('<3I',0xd2800000,0xd2800ba8,0xd4000001)

class BF:
 def __init__(self):self.p=0;self.s=[]
 def at(self,i):
  d=i-self.p
  if d:self.s.append(('>' if d>0 else '<')*abs(d));self.p=i
 def raw(self,s):self.s.append(s)
 def add(self,n):
  n%=256;self.raw('+'*n if n<=128 else '-'*(256-n))
 def clear(self,i):self.at(i);self.raw('[-]')
 def set(self,i,n):self.clear(i);self.at(i);self.add(n)
 def cp(self,a,b):
  self.clear(b);self.clear(2);self.clear(3)
  self.at(a);self.raw('[');self.raw('-');self.at(b);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
 def eq(self,a,v):
  self.clear(2);self.clear(3)
  self.at(a);self.raw('[');self.raw('-');self.at(2);self.raw('+');self.at(3);self.raw('+');self.at(a);self.raw(']')
  self.at(3);self.raw('[');self.raw('-');self.at(a);self.raw('+');self.at(3);self.raw(']')
  self.at(2);self.add(-v);self.set(4,1)
  self.at(2);self.raw('[');self.raw('[-]');self.clear(4);self.at(2);self.raw(']')
  self.at(4);self.raw('[')
 def endeq(self):self.clear(4);self.at(4);self.raw(']')
 def move(self,a,b):
  self.clear(b);self.at(a);self.raw('[');self.raw('-');self.at(b);self.raw('+');self.at(a);self.raw(']')
 def inc(self,base):
  self.set(40,1)
  for i in range(8):
   self.at(40);self.raw('[');self.raw('-');self.at(base+i);self.raw('+')
   self.eq(base+i,0);self.set(41,1);self.endeq()
   self.at(40);self.raw(']')
   self.at(41);self.raw('[');self.raw('-');self.at(40);self.raw('+');self.at(41);self.raw(']')
  self.at(40);self.raw('[');self.raw('[-]');self.set(42,1);self.at(40);self.raw(']')
 def emit_const_run(self,chunk):
  if not chunk:return
  self.clear(50);prev=0
  for target in chunk:
   self.at(50);self.add((target-prev)&255);self.raw('.')
   prev=target
  self.clear(50)


# Three small BF stages instead of a single source above the compiler input cap.
# The host transports eight opaque bytes between stages, never computes sizes.

def save(name,b,contract):
 dest=ROOT/'experiments'/name
 text=''.join(b.s)
 header='# Standard Brainfuck owned compact dynamic ELF layout stage\n# The host transports unchanged framed bytes without constructing ELF data\n'+contract
 dest.write_text(header+text+'\n')
 print(name,len(text))

b=BF()
for i in range(8):b.at(10+i);b.raw(',')
for _ in range(7):b.inc(10)
for i in range(8):b.at(10+i);b.raw('.')
b.at(42);b.raw('.')
save('android_compact_elf_word_plus7_52.bf',b,
     '# Input code words eight bytes and output that number plus seven as eight bytes then status\n')

b=BF()
for i in range(8):b.at(10+i);b.raw(',')
for i in range(8):
 b.cp(10+i,20);b.clear(21);b.clear(22)
 b.at(20);b.raw('[');b.raw('-');b.at(21);b.raw('+')
 b.eq(21,64);b.clear(21);b.at(22);b.raw('+');b.endeq()
 b.at(20);b.raw(']')
 b.move(23,30+i)
 b.at(21);b.raw('[');b.raw('-');b.at(30+i);b.raw('++++');b.at(21);b.raw(']')
 b.move(22,23)
b.at(23);b.raw('[');b.raw('[-]');b.set(42,1);b.at(23);b.raw(']')
for i in range(8):b.at(30+i);b.raw('.')
b.at(42);b.raw('.')
save('android_compact_elf_words_to_bytes52.bf',b,
     '# Input eight bytes of words and output four times that value then status\n')

b=BF()
for i in range(8):b.at(10+i);b.raw(',')
segment=bytearray()
for i,c in enumerate(HEADER):
 if i in range(208,224):
  b.emit_const_run(bytes(segment));segment.clear()
  b.at(10+((i-208)%8));b.raw('.')
 else:segment.append(c)
b.emit_const_run(bytes(segment)+START+EXIT)
b.at(42);b.raw('.')
save('android_compact_elf_header52.bf',b,
     '# Input exact code segment byte length and emit headers startup exit status\n')

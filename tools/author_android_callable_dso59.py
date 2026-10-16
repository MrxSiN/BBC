#!/usr/bin/env python3
"""Development-only author of the standard-BF ELF dynamic-library header.

The generated .bf source is the executable compiler stage. This author is
never imported by production compilation. No host assembler, linker or C code
produces the shipped policy machine instructions or their ELF metadata.
"""
import struct
from pathlib import Path
from tools.author_dynamic_callable57 import emit_bytes
from build.author_policy_stages import BF

ROOT=Path(__file__).resolve().parents[1]
CODE_OFFSET=1024
SYMBOL=b'bfc_call_v1'
HDR=bytearray(CODE_OFFSET)
HDR[:64]=b'\x7fELF\x02\x01\x01'+bytes(9)+struct.pack(
    '<HHIQQQIHHHHHH',3,183,1,0,64,0x200,0,64,56,2,64,7,6)
# Android AArch64: a 16K-aligned RX load and a read-only dynamic segment.
struct.pack_into('<IIQQQQQQ',HDR,0x40,1,5,0,0,0,0,0,16384)
struct.pack_into('<IIQQQQQQ',HDR,0x78,2,4,0x120,0x120,0x120,96,96,8)
# SysV symbol lookup hash: one bucket, two symbols including STN_UNDEF.
struct.pack_into('<IIIII',HDR,0xc0,1,2,1,0,0)
struct.pack_into('<IBBHQQ',HDR,0xf8,1,0x12,0,5,CODE_OFFSET,0)
STR=b'\0'+SYMBOL+b'\0'
assert len(STR)==13
HDR[0x110:0x110+len(STR)]=STR
for ix,(tag,value) in enumerate(((4,0xc0),(5,0x110),(6,0xe0),
                                 (10,len(STR)),(11,24),(0,0))):
    struct.pack_into('<QQ',HDR,0x120+16*ix,tag,value)
HDR[0x180:0x188]=b'BFP1'+struct.pack('<I',1)
# Section headers are not required by the dynamic loader, but let readelf
# independently inspect dynsym, dynstr, text size and the exported function.
NAMES=b'\0.hash\0.dynsym\0.dynstr\0.dynamic\0.text\0.shstrtab\0'
HDR[0x190:0x190+len(NAMES)]=NAMES
names={name:NAMES.index(b'.'+name) for name in (b'hash',b'dynsym',b'dynstr',
                                                b'dynamic',b'text',b'shstrtab')}
def section(ix,name,typ,flags,addr,offset,size,link=0,info=0,align=1,entsize=0):
    struct.pack_into('<IIQQQQIIQQ',HDR,0x200+64*ix,names[name],typ,flags,
                     addr,offset,size,link,info,align,entsize)
section(1,b'hash',5,2,0xc0,0xc0,20,2,0,4,4)
section(2,b'dynsym',11,2,0xe0,0xe0,48,3,1,8,24)
section(3,b'dynstr',3,2,0x110,0x110,len(STR))
section(4,b'dynamic',6,2,0x120,0x120,96,3,0,8,16)
section(5,b'text',1,6,CODE_OFFSET,CODE_OFFSET,0,0,0,4)
section(6,b'shstrtab',3,0,0,0x190,len(NAMES))
assert len(HDR)==CODE_OFFSET

b=BF()
for i in range(8):b.at(i);b.raw(',')
# Byte-preserving 64-bit copy; code length remains in cells 0 through 7.
for i in range(8):b.copy(i,16+i,28)
# Add 1024 to the ELF segment size, with checked byte-wise carry.
for _ in range(4):
    b.add(17,1)
    b.eq(17,0,13,9,12)
    b.once(13,lambda:b.set(8,1))
    for i in range(18,24):
        def carry(i=i):
            b.add(i,1)
            b.eq(i,0,13,9,12)
            b.once(13,lambda:b.set(14,1))
        b.once(8,carry)
        b.once(14,lambda:b.set(8,1))
        if i==23:b.once(8,lambda:b.set(31,1))
# The BF stage emits every ELF header byte, native sizes and dynsym fields.
emit_bytes(b,HDR[:96])
for pos in range(16,24):b.at(pos);b.raw('.')
for pos in range(16,24):b.at(pos);b.raw('.')
emit_bytes(b,HDR[112:0x108])
for pos in range(8):b.at(pos);b.raw('.') # ELF function st_size
emit_bytes(b,HDR[0x110:0x360])
for pos in range(8):b.at(pos);b.raw('.') # Section .text sh_size
emit_bytes(b,HDR[0x368:]);
b.at(31);b.raw('.') # 0 success, nonzero length overflow.
b.save('android_callable_dso_header59',
       'Emit AArch64 shared ELF with BFP call export and checked wide native code sizes')
print('BF program',ROOT/'experiments/android_callable_dso_header59.bf',
      'BF command count',len(''.join(b.parts)))

#!/usr/bin/env python3
"""Development-only authoring for two standard-BF dynamic callable compiler stages.

The emitted .bf programs own opcode selection, native instruction bytes, and
ELF length arithmetic. This author does not execute in the compilation path.
"""
import struct
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'build'))
from author_policy_stages import BF

PROLOGUE = [0xaa1f03ea,0xaa0403eb,0xaa1f03ec,0xaa1f03ed,0xaa0603f0,0xaa1f03ee,
            0xd503201f,0xd503201f]
EPILOGUE = [0x2a0e03e0,0x14000005,0x52800020,0x14000003,0xd10004c6,
            0x52800060,0xcb060201,0xf90000ed,0xd65f03c0]
# No pointer-proof shortcut. Each source pointer move executes its own trap.
LINEAR = {
    ord('+'): [0x39400169, 0x11000529, 0x39000169],
    ord('-'): [0x39400169, 0x51000529, 0x39000169],
    ord('>'): [0x9100054a, 0xeb05015f, 0x540000a3, 0x52800060,
               0xcb060201, 0xf90000ed, 0xd65f03c0, 0x8b0a008b],
    ord('<'): [0xd100054a, 0xeb05015f, 0x540000a3, 0x52800060,
               0xcb060201, 0xf90000ed, 0xd65f03c0, 0x8b0a008b],
    ord(','): [0xeb01019f,0x540000a2,0x386c6809,0x9100058c,
               0x39000169,0x14000002,0x3900017f],
    ord('.'): [0xeb0301bf,0x540000a2,0x39400169,0x382d6849,
               0x910005ad,0x14000002,0x5280004e]
}

def write_byte(b, cell, value):
    b.set(cell,value); b.at(cell); b.raw('.')

def emit_bytes(b,data):
    # Reuse a scratch cell to minimize the authoritative BF instruction stream.
    value=0
    for byte in data:
        b.add(30, byte-value)
        b.at(30);b.raw('.')
        value=byte
    b.clear(30)

def emitter():
    b=BF()
    # Emit no opaque wrapper here: the caller inserts these BF-authored code
    # bytes after BF-authored ELF header. Input is framed (has byte, raw byte).
    emit_bytes(b,struct.pack('<8I',*PROLOGUE))
    b.at(0);b.raw(',[')
    b.at(1);b.raw(',')
    for op,words in LINEAR.items():
        b.eq(1,op,10,11,12)
        b.once(10,lambda words=words:emit_bytes(b,struct.pack('<'+'I'*len(words),*words)))
    for op in (ord('['),ord(']')):
        b.eq(1,op,10,11,12)
        b.once(10,lambda:b.set(2,1))
    b.at(0);b.raw(',]')
    emit_bytes(b,struct.pack('<9I',*EPILOGUE))
    b.at(2);b.raw('.') # Nonzero = unsupported brackets, image must not commit.
    b.save('android_callable_linear57','Emit dynamically sized AArch64 callable linear native code')

def header():
    # Reads a little-endian 64-bit size of the BF-emitted CODE ONLY. The ELF
    # header is 128 bytes, so BF adds 128 with carry and rejects overflow.
    b=BF()
    for i in range(8):b.at(i);b.raw(',')
    # Keep a separate original code length only if future header fields need it.
    b.set(9,128)
    b.at(9);b.raw('[')
    b.add(0,1)
    b.eq(0,0,10,11,12)
    b.once(10,lambda:b.add(8,1))
    b.add(9,-1)
    b.at(9);b.raw(']')
    for i in range(1,8):
        def increment(i=i):
            b.add(i,1)
            b.eq(i,0,10,11,12)
            b.once(10,lambda:b.set(14,1))
        b.once(8,increment)
        b.once(14,lambda:b.set(8,1))
    # Executable segment starts at zero; file size == memory image size.
    h = b'\x7fELF\x02\x01\x01'+bytes(9)
    h+=struct.pack('<HHIQQQIHHHHHH',3,183,1,128,64,0,0,64,56,1,0,0,0)
    h+=struct.pack('<IIQQQQQQ',1,5,0,0,0,0,0,16384)
    h+=b'BFP1'+bytes(4)
    assert len(h)==128
    emit_bytes(b,h[:96]);
    for _ in range(2):
        for i in range(8):b.at(i);b.raw('.')
    emit_bytes(b,h[112:]);
    b.at(8);b.raw('.') # Nonzero means size overflow.
    b.save('android_callable_header57','Emit AArch64 callable ELF header with BF owned 64 bit length')

if __name__=='__main__':
    emitter();header()

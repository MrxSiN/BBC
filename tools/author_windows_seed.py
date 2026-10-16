#!/usr/bin/env python3
"""Development-only authoring of a fixed Windows PE import/exit BF byte emitter.

The saved .bf stream owns output at execution. This script must never be in
production compilation, and the primitive does not compile source programs.
"""
from pathlib import Path
import struct
ROOT = Path(__file__).resolve().parents[1]

def template():
    blob = bytearray(0x600)
    blob[0:2] = b'MZ'
    struct.pack_into('<I', blob, 0x3c, 0x80)
    blob[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', blob, 0x84, 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    p = 0x98
    struct.pack_into('<HBBIIIIIQII', blob, p, 0x20b, 0, 0, 0x200, 0x200, 0,
                     0x1000, 0x1000, 0x140000000, 0x1000, 0x200)
    struct.pack_into('<HHHHHHIIIIHHQQQQII', blob, p + 40,
                     6, 0, 0, 0, 6, 0, 0, 0x3000, 0x200, 0, 3, 0x100,
                     0x100000, 0x1000, 0x100000, 0x1000, 0, 16)
    # Import table and import address table data directories.
    struct.pack_into('<II', blob, p + 112 + 1*8, 0x2010, 40)
    struct.pack_into('<II', blob, p + 112 + 12*8, 0x2000, 16)
    s = 0x80 + 4 + 20 + 0xF0
    for i, row in enumerate([
        (b'.text', 16, 0x1000, 0x200, 0x200, 0x60000020),
        (b'.idata', 0x70, 0x2000, 0x200, 0x400, 0xC0000040),
    ]):
        name,vsize,rva,rsize,off,flags=row
        struct.pack_into('<8sIIIIIIHHI',blob,s+i*40,name.ljust(8,b'\0'),vsize,rva,rsize,off,0,0,0,0,flags)
    # Win64 stack alignment, call imported ExitProcess(0), trap if it returns.
    code = b'\x48\x83\xec\x28\x31\xc9\xff\x15' + struct.pack('<i',0x2000-(0x1000+12)) + b'\x0f\x0b'
    blob[0x200:0x200+len(code)] = code
    # IAT first, import descriptor second, DLL name and hint/name entry.
    struct.pack_into('<Q',blob,0x400,0x2050)
    struct.pack_into('<IIIII',blob,0x410,0,0,0,0x2038,0x2000)
    blob[0x438:0x438+len(b'KERNEL32.dll\0')] = b'KERNEL32.dll\0'
    blob[0x450:0x450+2+len(b'ExitProcess\0')] = b'\0\0ExitProcess\0'
    return bytes(blob)

def main():
    blob=template(); curr=0; code=[]
    for c in blob:
        delta=(c-curr)%256
        code.append(('+'*delta if delta<=128 else '-'*(256-delta))+'.')
        curr=c
    stream=''.join(code)
    target=ROOT/'experiments/windows_pe_exit_seed.bf'
    target.write_text('# Windows PE console exit primitive\n# Emits fixed PE bytes with imported ExitProcess\n'+stream+'\n',encoding='ascii')
    print(f'BF commands={len(stream)} image={len(blob)} bytes')
if __name__ == '__main__': main()

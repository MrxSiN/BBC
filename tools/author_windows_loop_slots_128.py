#!/usr/bin/env python3
"""Development-only authoring of bracket-placeholder Windows PE backend.

This program writes *only* the authoritative Brainfuck code. At compile time,
that Brainfuck executable selects the source-dependent x64 slots, writes all
PE bytes, and rejects unsupported source. Python is not in the compile path.
"""
from pathlib import Path
import struct
from author_windows_linear import BF as BFBase, SLOTS as OLD_SLOTS, SLOT_LEN
SLOT_COUNT = 128
TEXT_SIZE = 0x800
IDATA_RAW = 0xA00

ROOT=Path(__file__).resolve().parents[1]
NOP=b'\x90'*SLOT_LEN

class BF(BFBase):
    def emit(self, data):
        # Runtime byte emitter. Cell eight is always zero before and after each
        # fast constant change; both the multiplier loop and final byte are BF.
        self.clear(9)
        last=0
        for c in data:
            delta=(c-last)%256
            signed=delta if delta<=128 else delta-256
            cost=abs(signed)
            best=None
            for sign in (1,-1):
                target=(signed if sign==1 else -signed)%256
                # Up to 128 increments in either direction.
                if target>128:continue
                for stride in (8,16,32):
                    for k in range(1,9):
                        remainder=target-stride*k
                        if abs(remainder)>128:continue
                        candidate=2+k+stride+6+abs(remainder)
                        if candidate<cost:
                            cost=candidate
                            best=(sign,stride,k,remainder)
            if best is None:
                self.add(9,signed)
            else:
                sign,stride,k,remainder=best
                self.at(8);self.op('+'*k+'[->'+('+' if sign==1 else '-')*stride+'<]')
                self.at(9);self.op(('+' if sign==1 else '-')*max(remainder,0)+('-' if sign==1 else '+')*max(-remainder,0))
            self.at(9);self.op('.')
            last=c
        self.clear(9)




def relcall_iat(code:bytearray, base_rva:int, iat_rva:int):
    """Append call [rip+relative displacement] to one fixed Win32 import."""
    # Fixed, source-independent host API glue; encoded into BF source constants.
    src_rva=base_rva+len(code)
    code+=b'\xff\x15'+struct.pack('<i',iat_rva-(src_rva+6))


def make_io_helper(helper_rva:int, handle:int, api_rva:int, check_write:bool):
    code=bytearray()
    code+=bytes.fromhex('4883ec30')        # aligned call frame, 32-byte shadow, fifth arg + count
    if not check_write:
        code+=bytes.fromhex('c60300')      # zero cell before a ReadFile: EOF -> zero
    code+=b'\xb9'+struct.pack('<i',handle)
    relcall_iat(code, helper_rva, 0x2008) # GetStdHandle
    code+=bytes.fromhex('4889c1')        # handle in RCX
    code+=bytes.fromhex('4889da')        # current cell in RDX
    code+=bytes.fromhex('41b801000000')  # number of bytes R8D = 1
    code+=bytes.fromhex('4c8d4c2428')    # pointer to count in R9
    code+=bytes.fromhex('48c744242000000000') # fifth arg OVERLAPPED = NULL
    code+=bytes.fromhex('c744242800000000') # initialize count
    relcall_iat(code,helper_rva,api_rva)
    code+=bytes.fromhex('85c0')          # check BOOL return
    code+=bytes.fromhex('75020f0b')      # if failed trap via UD2
    if check_write:
        code+=bytes.fromhex('837c242801')  # cmp DWORD [rsp+0x28], 1
        code+=bytes.fromhex('74020f0b')    # incomplete output -> trap
    code+=bytes.fromhex('4883c430c3')   # restore stack and RET
    return bytes(code)


def template():
    image=bytearray(0xc00)
    image[:2]=b'MZ'
    struct.pack_into('<I',image,0x3c,0x80)
    image[0x80:0x84]=b'PE\0\0'
    struct.pack_into('<HHIIIHH',image,0x84,0x8664,3,0,0,0,0xf0,0x0022)
    p=0x98
    struct.pack_into('<HBBIIIIIQII',image,p,0x20b,0,0,TEXT_SIZE,0x200,0,
                     0x1000,0x1000,0x140000000,0x1000,0x200)
    struct.pack_into('<HHHHHHIIIIHHQQQQII',image,p+40,
                     6,0,0,0,6,0,0,0x13000,0x200,0,3,0x100,
                     0x100000,0x1000,0x100000,0x1000,0,16)
    struct.pack_into('<II',image,p+112+8,0x2030,40)  # import dir
    struct.pack_into('<II',image,p+112+96,0x2000,40) # IAT directory
    sec=0x188
    for i,(name,vsize,rva,raw,off,flags) in enumerate([
        (b'.text',TEXT_SIZE,0x1000,TEXT_SIZE,0x200,0x60000020),
        (b'.idata',0xd0,0x2000,0x200,IDATA_RAW,0xc0000040),
        (b'.tape',0x10000,0x3000,0,0,0xc0000080),
    ]):
        struct.pack_into('<8sIIIIIIHHI',image,sec+i*40,
                         name.ljust(8,b'\0'),vsize,rva,raw,off,0,0,0,0,flags)
    # IAT holds four imported functions and a zero terminator.
    for i,rva in enumerate((0x2090,0x20a0,0x20b0,0x20c0)):
        struct.pack_into('<Q',image,IDATA_RAW+8*i,rva)
    struct.pack_into('<IIIII',image,IDATA_RAW+0x30,0,0,0,0x2070,0x2000)
    image[IDATA_RAW+0x70:IDATA_RAW+0x70+len(b'KERNEL32.dll\0')]=b'KERNEL32.dll\0'
    for rva,name in ((0x2090,b'ExitProcess'),(0x20a0,b'GetStdHandle'),
                     (0x20b0,b'ReadFile'),(0x20c0,b'WriteFile')):
        image[IDATA_RAW+rva-0x2000:IDATA_RAW+rva-0x2000+3+len(name)]=b'\0\0'+name+b'\0'

    # All offsets below are fixed for 128 source-independent slot positions.
    # Load cell base and end, then keep stable helper pointers in R14 and R15.
    pro=bytearray()
    def lea_reg(prefix,target):
        instr_rva=0x1000+len(pro)
        pro.extend(prefix+struct.pack('<i',target-(instr_rva+7)))
    lea_reg(bytes.fromhex('4c8d25'),0x3000) # R12 tape base
    pro+=bytes.fromhex('4c89e3')           # RBX current tape cell
    lea_reg(bytes.fromhex('4c8d2d'),0x13000) # R13 tape end
    # helper entry points are immediately after main ExitProcess call.
    io_write_rva=0x1000+31+SLOT_COUNT*SLOT_LEN+14
    write_helper=make_io_helper(io_write_rva,-11,0x2018,True)
    io_read_rva=io_write_rva+len(write_helper)
    read_helper=make_io_helper(io_read_rva,-10,0x2010,False)
    lea_reg(bytes.fromhex('4c8d35'),io_write_rva) # R14 = write function
    lea_reg(bytes.fromhex('4c8d3d'),io_read_rva) # R15 = read function
    assert len(pro)==31
    exit_rva=0x1000+len(pro)+SLOT_COUNT*SLOT_LEN
    epi=bytearray(bytes.fromhex('4883ec2831c9'))
    relcall_iat(epi,exit_rva,0x2000)
    epi+=bytes.fromhex('0f0b')
    assert len(epi)==14
    assert 31+SLOT_COUNT*SLOT_LEN+len(epi)+len(write_helper)+len(read_helper)<=TEXT_SIZE
    return image,bytes(pro),bytes(epi),write_helper+read_helper


def main():
    image,prologue,epilogue,helpers=template()
    slots=dict(OLD_SLOTS)
    slots[ord('.')]=bytes.fromhex('41ffd6')+b'\x90'*9 # call R14
    slots[ord(',')]=bytes.fromhex('41ffd7')+b'\x90'*9 # call R15
    slots[ord('[')]=bytes.fromhex('803b000f8400000000909090')
    slots[ord(']')]=bytes.fromhex('803b000f8500000000909090')
    bf=BF()
    bf.set(5,SLOT_COUNT)
    bf.emit(image[:0x200]+prologue)
    bf.at(0);bf.op(',');bf.begin(0)
    bf.copy(5,10,11)
    bf.set(12,1);bf.clear(4)
    def enable():bf.set(4,1);bf.clear(12)
    bf.if_once(10,enable)
    def process():
        bf.add(5,-1);bf.clear(7)
        for c,slot in slots.items():
            bf.equal(c)
            def write(slot=slot):bf.emit(slot);bf.set(7,1)
            bf.if_once(3,write)
        bf.set(13,1)
        def found():bf.clear(13)
        bf.if_once(7,found)
        def unknown():bf.emit(NOP);bf.set(6,1)
        bf.if_once(13,unknown)
    bf.if_once(4,process)
    def overflow():bf.set(6,1)
    bf.if_once(12,overflow)
    bf.at(0);bf.op(',');bf.end(0)
    bf.begin(5);bf.emit(NOP);bf.add(5,-1);bf.end(5)
    bf.emit(epilogue+helpers)
    pad=TEXT_SIZE-len(prologue)-SLOT_COUNT*SLOT_LEN-len(epilogue)-len(helpers)
    assert pad>=0
    bf.emit(b'\x90'*pad+image[IDATA_RAW:])
    bf.at(6);bf.op('.')
    bf.at(0)
    program=''.join(bf.code)
    source=('# Windows loop slot PE compiler with Win32 byte IO\n'
            '# Produces three section image with checked tape semantics\n'
            '# Loop displacement values are placeholders and must be patched\n'
            '# Each source instruction selects one of eight x64 slots\n'
            +program+'\n')
    target=ROOT/'experiments/windows_loop_slots_pe_128.bf'
    target.write_text(source,encoding='ascii')
    print(f'{len(program)} Brainfuck commands; {len(helpers)} helper bytes; {pad} padding')
    assert len(program)<=16128,'source over compiler limit'

if __name__=='__main__': main()

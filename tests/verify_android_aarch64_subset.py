#!/usr/bin/env python3
"""Independent structural and instruction-level checks of the *experimental* BF Android emitter.

This does NOT execute on Android or establish native self-hosting.  The tiny
AArch64 instruction simulator below is an oracle for this deliberately bounded
instruction set, not a replacement for a device/emulator execution test.
"""
import hashlib
import json
import pathlib
import random
import shutil
import struct
import subprocess
import tempfile

import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from source_check import check_source
SOURCE = ROOT / 'experiments/android_aarch64_pie_subset.bf'
NATIVE = ROOT / 'build/android_pie_emitter_linux_x86_64.elf'
SAMPLES = [
    b'', b'+', b'-', b'.', b'+.', b'-.', b'+-.', b'-+.',
    b'+++++++++.', b'----------', b'.....', b'Hello World',
    b'+++   +++...', b'++comment++.', b'++\xff++.', b'\n--.\n',
    b'>+.<.', b'>+.<', b'>>++.<--.', b'><+.', b'>.>', b'<', b'<.', b'++<+.',
    b',', b',.', b',>,.<.', b',<>.', b'>,.<.', b'>+++.<.',
]
INVALID = [b'[', b']', b'[+]',
           b'+++++++++++', b'.'*11, b'++++++++++.', b'++[]', b'<[', b'<>[', b'>++++++++++', b'[,]', b'++[,.]', b'>>[', b'<>]', b'+++++[>+++++]' ]
NOP = 0xd503201f
ADD = [0x39400269, 0x11000529, 0x39000269]
SUB = [0x39400269, 0x51000529, 0x39000269]
WRITE = [0xd2800020,0xaa1303e1,0xd2800022,0xd2800808,0xd4000001,
         0xf100041f,0x54000080,0xd2800060,0xd2800ba8,0xd4000001]
# Unsigned pointer offset is checked after each movement. All trap paths exit(2).
RIGHT = [0x91000673,0xcb140269,0xf140413f,0x54000083,0xd2800040,
         0xd2800ba8,0xd4000001] + [NOP]*5
LEFT = [0xd1000673] + RIGHT[1:]
# AArch64 read: one byte, EOF clears cell, unexpected read return exits(4).
READ = [0xd2800000,0xaa1303e1,0xd2800022,0xd28007e8,0xd4000001,
        0xb40000c0,0xf100041f,0x540000a0,0xd2800080,0xd2800ba8,
        0xd4000001,0x3900027f]
PACK = lambda words: struct.pack('<'+'I'*len(words), *words)
TEMPLATES = {ord('+'):PACK(ADD+[NOP]*9),ord('-'):PACK(SUB+[NOP]*9),
             ord('.'):PACK(WRITE+[NOP]*2),ord('>'):PACK(RIGHT),ord('<'):PACK(LEFT),ord(','):PACK(READ)}


def check_elf(img,static=False,tape_on_stack=False):
    assert len(img)==4192 and img[:8]==b'\x7fELF\x02\x01\x01\x00'
    e_type,mach,ver,entry,phoff,shoff,flags,ehsz,phsz,phnum,shsz,shnum,shstr=struct.unpack_from('<HHIQQQIHHHHHH',img,16)
    assert (e_type,mach,ver,entry,phoff,shoff,ehsz,phsz,phnum,shnum)==(3,183,1,0x200,64,0,64,56,5,0)
    phdrs=[struct.unpack_from('<IIQQQQQQ',img,64+56*i) for i in range(5)]
    types=[x[0] for x in phdrs]
    assert types==[6,0 if static else 3,1,0 if tape_on_stack else 1,0 if tape_on_stack else 2]
    phdr,interp,rx,rw,dyn=phdrs
    assert (phdr[2],phdr[5],phdr[6])==(64,280,280)
    assert (interp[2],interp[5])==(0x160,21)
    assert img[0x160:0x175]==b'/system/bin/linker64\0'
    assert (rx[1],rx[2],rx[3],rx[5],rx[6],rx[7])==(5,0,0,0x1000,0x1000,0x4000)
    assert (rw[1],rw[2],rw[3],rw[5],rw[6],rw[7])==(6,0x1000,0x5000,96,65632,0x4000)
    assert (dyn[2],dyn[3],dyn[5],dyn[6])==(0x1000,0x5000,96,96)
    for p in (rx,rw):
        assert p[3]%p[7]==p[2]%p[7]
    assert img[0x180:0x198]==bytes(24)
    assert img[0x198]==0
    assert struct.unpack_from('<IIII',img,0x1a0)==(1,1,0,0)
    assert [struct.unpack_from('<QQ',img,0x1000+i*16) for i in range(6)]==[(5,0x198),(6,0x180),(11,24),(10,1),(4,0x1a0),(0,0)]
    entry_words=(0xd10043ff,0x910003f4,0xaa1403f3,0xa9007fff) if tape_on_stack else (0xb0000034,0x91018294,0xaa1403f3,NOP)
    assert struct.unpack_from('<IIII',img,0x200)==entry_words
    assert struct.unpack_from('<III',img,0x3f0)==(0xd2800000,0xd2800ba8,0xd4000001)
    assert img[0x3fc:0x1000]==PACK([NOP]*((0x1000-0x3fc)//4))


def check_slots(img,src):
    instr=[c for c in src if c in b'+-.><,']
    assert len(instr)<=10
    for i in range(10):
        chunk=img[0x210+i*48:0x210+(i+1)*48]
        assert chunk==(TEMPLATES[instr[i]] if i<len(instr) else PACK([NOP]*12)), (i,chunk[:12].hex())


def emulate(img,load_bias,fail_write=False,initial_pointer=0,input_bytes=b'',fail_read=False,max_steps=1100,tape_snapshot=None, tape_base_rva=0x5060, code_limit=0x1000, code_start_rva=0x200):
    # Only executes known AArch64 encodings, trapping unknown instruction words.
    tape=bytearray(65536)
    regs={0:0,1:0,2:0,8:0,9:0,10:0,11:0,19:0,20:0}
    ip=code_start_rva
    out=bytearray()
    input_index=0
    flags_equal=False
    pointer_in_range=False
    tape_base=load_bias+tape_base_rva
    regs[19]=tape_base+initial_pointer
    for steps in range(max_steps):
        assert code_start_rva<=ip<code_limit and ip%4==0, hex(ip)
        op=struct.unpack_from('<I',img,ip)[0]
        next_ip=ip+4
        if (op & 0xfc000000) == 0x14000000:
            displacement = op & 0x3ffffff
            if displacement & (1<<25): displacement -= 1<<26
            next_ip=ip+4*displacement
        elif (op & 0xff00001f) == 0x54000002:
            displacement=(op >> 5) & 0x7ffff
            if displacement & (1<<18): displacement -= 1<<19
            if not pointer_in_range:next_ip=ip+4*displacement
        elif (op & 0xff00001f) in (0x34000009,0x35000009):
            displacement = (op >> 5) & 0x7ffff
            if displacement & (1<<18): displacement -= 1<<19
            if (regs[9] == 0) == ((op & 0xff00001f) == 0x34000009):
                next_ip=ip+4*displacement
        elif op==0x1000000a:regs[10]=load_bias+ip # ADR x10, current PC
        elif op==0x5800006b:regs[11]=struct.unpack_from('<Q',img,ip+12)[0] # LDR literal signed-word delta
        elif op==0x8b0b094a:regs[10]=(regs[10]+(regs[11]<<2))&((1<<64)-1)
        elif op==0xd61f0140:next_ip=regs[10]-load_bias # BR x10, position-independent
        elif op==NOP:pass
        elif (op & 0x9f00001f) == 0x90000014:
            # ADRP x20: sign extended 21-bit page displacement from PC page.
            imm21 = (((op >> 5) & 0x7ffff) << 2) | ((op >> 29) & 3)
            if imm21 & (1 << 20): imm21 -= 1 << 21
            regs[20] = ((load_bias + ip) & ~0xfff) + (imm21 << 12)
        elif op==0x90000054:regs[20]=load_bias+0x8000 # Extended 16 KiB RX layout
        elif op==0x90000094:regs[20]=load_bias+0x10000 # Two file size classes; fixed safe RW RVA
        elif op==0xd10043ff:pass # Model sixteen reserved stack bytes at tape_base.
        elif op==0x910003f4:regs[20]=tape_base
        elif op==0xa9007fff:tape[:16]=bytes(16)
        elif op==0x91018294:regs[20]+=96
        elif op==0x91000294:pass  # BF emitted fixed tape-page startup
        elif op==0xaa1403f3:regs[19]=regs[20]+initial_pointer
        elif op==0x91000673:regs[19]=(regs[19]+1)&((1<<64)-1)
        elif op==0xd1000673:regs[19]=(regs[19]-1)&((1<<64)-1)
        elif op==0x9100066a:regs[10]=(regs[19]+1)&((1<<64)-1)
        elif op==0xd100066a:regs[10]=(regs[19]-1)&((1<<64)-1)
        elif op==0xcb14014a:regs[10]=(regs[10]-regs[20])&((1<<64)-1)
        elif op==0xf140415f:pointer_in_range=regs[10]<65536
        elif op in (0x3940066a,0x385ff26a):
            destination=regs[19]-tape_base+(1 if op==0x3940066a else -1)
            assert 0<=destination<65536
            regs[10]=tape[destination]
        elif op==0x0b09014a:regs[10]=(regs[10]+regs[9])&0xffffffff
        elif op in (0x3900066a,0x381ff26a):
            destination=regs[19]-tape_base+(1 if op==0x3900066a else -1)
            assert 0<=destination<65536
            tape[destination]=regs[10]&255
        elif op==0xcb140269:regs[9]=(regs[19]-regs[20])&((1<<64)-1)
        elif op==0xf140413f:pointer_in_range=regs[9]<65536
        elif op==0x54000083:
            if pointer_in_range:next_ip=ip+16
        elif op==0xd2800040:regs[0]=2
        elif op==0x39400269:
            assert 0<=regs[19]-tape_base<65536
            regs[9]=tape[regs[19]-tape_base]
        elif op==0x11000529:regs[9]=(regs[9]+1)&0xffffffff
        elif op==0x51000529:regs[9]=(regs[9]-1)&0xffffffff
        elif op==0x39000269:
            assert 0<=regs[19]-tape_base<65536
            tape[regs[19]-tape_base]=regs[9]&255
        elif op==0x39000669:
            destination=regs[19]-tape_base+1
            assert 0<=destination<65536
            tape[destination]=regs[9]&255
        elif op==0x3900027f:
            assert 0<=regs[19]-tape_base<65536
            tape[regs[19]-tape_base]=0
        elif op==0xd2800020:regs[0]=1
        elif op==0xaa1303e1:regs[1]=regs[19]
        elif op==0xd2800022:regs[2]=1
        elif op==0xd2800808:regs[8]=64
        elif op==0xd28007e8:regs[8]=63
        elif op==0xf100041f:flags_equal=(regs[0]==1)
        elif op==0x54000080:
            if flags_equal:next_ip=ip+16
        elif op==0xb40000c0:
            if regs[0]==0:next_ip=ip+24
        elif op==0x540000a0:
            if flags_equal:next_ip=ip+20
        elif op==0xd2800060:regs[0]=3
        elif op==0xd2800080:regs[0]=4
        elif op==0xd2800ba8:regs[8]=93
        elif op==0xd2800000:regs[0]=0
        elif op==0xd4000001:
            if regs[8]==63:
                assert regs[0]==0 and regs[1]==regs[19] and regs[2]==1
                if fail_read:regs[0]=(-5)&((1<<64)-1)
                elif input_index>=len(input_bytes):regs[0]=0
                else:
                    assert 0<=regs[1]-tape_base<65536
                    tape[regs[1]-tape_base]=input_bytes[input_index]
                    input_index+=1
                    regs[0]=1
            elif regs[8]==64:
                assert regs[0]==1 and regs[1]==regs[19] and regs[2]==1
                if fail_write:regs[0]=(-5)&((1<<64)-1)
                else:
                    assert 0<=regs[1]-tape_base<65536
                    out.append(tape[regs[1]-tape_base]);regs[0]=1
            elif regs[8]==93:
                if tape_snapshot is not None:tape_snapshot[:]=tape
                return bytes(out),regs[0],steps+1
            else:raise AssertionError(f'unknown syscall {regs[8]}')
        else:raise AssertionError(f'unknown AArch64 opcode {op:08x} at {ip:x}')
        ip=next_ip
    raise AssertionError('program did not exit')


def run(executable,source):
    result=subprocess.run([str(executable)],input=source,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=12,check=True)
    assert len(result.stdout)==4193, (source,len(result.stdout),result.stderr)
    return result.stdout[:-1],result.stdout[-1]


def main():
    assert NATIVE.is_file(), 'Build the experimental BF emitter with bootstrap/run_compiler.py'
    assert len(check_source(SOURCE.read_bytes()))<16128
    assert NATIVE.read_bytes()[:4]==b'\x7fELF'
    assert len(NATIVE.read_bytes())==215+32*len(check_source(SOURCE.read_bytes()))
    samples=list(SAMPLES)
    rng=random.Random(21)
    for _ in range(80):
        samples.append(bytes(rng.choice(b'+-.><,') for _ in range(rng.randint(0,10))))
    good=0
    errors=0
    for sample in samples:
        img,status=run(NATIVE,sample)
        assert status==0, (sample,status)
        check_elf(img)
        check_slots(img,sample)
        runtime_input = bytes((i*113+7)&255 for i in range(10))
        input_cursor=0
        reference_tape=bytearray(65536);reference_output=bytearray()
        ref_ptr=0;reference_trap=False
        for b in sample:
            if b==ord('>'):ref_ptr+=1
            elif b==ord('<'):ref_ptr-=1
            elif b==ord(','):
                reference_tape[ref_ptr] = runtime_input[input_cursor] if input_cursor < len(runtime_input) else 0
                input_cursor += 1
            elif b==ord('+'):reference_tape[ref_ptr]=(reference_tape[ref_ptr]+1)&255
            elif b==ord('-'):reference_tape[ref_ptr]=(reference_tape[ref_ptr]-1)&255
            elif b==ord('.'):reference_output.append(reference_tape[ref_ptr])
            if not 0<=ref_ptr<65536:
                reference_trap=True
                break
        for base in (0,0x40000000):
            output,status,steps=emulate(img,base,input_bytes=runtime_input)
            assert output==reference_output and status==(2 if reference_trap else 0) and steps<=1100, (sample,output,status,reference_output)
        if b'.' in sample and not reference_trap:
            output,status,_=emulate(img,0x40000000,fail_write=True,input_bytes=runtime_input)
            assert status==3
        good+=1
    # EOF clears an existing nonzero cell; read errors have a distinct exit(4).
    for source, data_in, expected in ((b'+,.',b'',b'\x00'),(b',.',b'\xff',b'\xff'),
                                      (b',.,.',b'\x00\x80',b'\x00\x80')):
        img,ok=run(NATIVE,source)
        assert ok==0
        for base in (0,0x40000000):
            output,exit_code,_=emulate(img,base,input_bytes=data_in)
            assert exit_code==0 and output==expected,(source,output,expected)
    img,ok=run(NATIVE,b',')
    assert ok==0
    for base in (0,0x40000000):
        _,exit_code,_=emulate(img,base,input_bytes=b'\x01',fail_read=True)
        assert exit_code==4
    # Inject near-boundary pointer locations; ten-command program limit would
    # otherwise make the upper bound unreachable through ordinary source.
    for source, initial in ((b'>',65535),(b'<',0)):
        img,status=run(NATIVE,source)
        assert status==0
        for base in (0,0x40000000):
            output,exit_code,_=emulate(img,base,initial_pointer=initial)
            assert output==b'' and exit_code==2
    for sample in INVALID:
        img,status=run(NATIVE,sample)
        assert status==1, (sample,status)
        assert len(img)==4192
        errors+=1
    # Independent BF seeds running precisely the same BF emitter source.
    seeds=0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as tmp:
            for src in ('seed_interpreter.c','seed_interpreter_alt.c'):
                exe=pathlib.Path(tmp)/src
                subprocess.run(['cc','-O2','-o',str(exe),str(ROOT/'bootstrap'/src)],check=True)
                for sample in (b'',b'+-..',b'++++++++++',b'[+]',b'+++++++++++',b'>+.<.',b'<',b'>>>++.<-.',b',.',b'>,'):
                    native=run(NATIVE,sample)
                    derived=run_seed(exe,sample)
                    assert native==derived, (src,sample)
                    seeds+=1
    # Host adapter only places validated output; failed sources cannot overwrite it.
    with tempfile.TemporaryDirectory() as tmp:
        dest=pathlib.Path(tmp)/'prog.elf'
        sourcefile=pathlib.Path(tmp)/'program.bf'
        sourcefile.write_bytes(b'+++..')
        result=subprocess.run(['python3',str(ROOT/'bootstrap/run_android_subset.py'),str(sourcefile),str(dest)],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # The adapter requires the previously verified evidence hash. If it is
        # missing in a new checkout, tests must first generate the report.
        assert result.returncode==0,(result.stdout,result.stderr)
        original=dest.read_bytes()
        assert original==run(NATIVE,b'+++..')[0]
        for bad in (b'[+]',b'+'*11,b'++\x00++.'):
            sourcefile.write_bytes(bad)
            result=subprocess.run(['python3',str(ROOT/'bootstrap/run_android_subset.py'),str(sourcefile),str(dest)],
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            assert result.returncode!=0 and dest.read_bytes()==original
    data={
      'classification':'STRUCTURAL AArch64 PIE + SIMULATED native instructions; NOT Android execution',
      'target':'aarch64-linux-android21 (shell prototype; actual minimum API untested)',
      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'host_emitter_sha256':hashlib.sha256(NATIVE.read_bytes()).hexdigest(),
      'source_instructions':len(check_source(SOURCE.read_bytes())),
      'host_emitter_bytes':NATIVE.stat().st_size,
      'aarch64_image_bytes':4192,
      'accepted_sources_tested':good,
      'rejected_sources_tested':errors,
      'independent_seed_comparisons':seeds,
      'aslr_base_values_tested':['0x00000000','0x40000000'],
      'linker_metadata':'PT_INTERP PT_DYNAMIC DT_HASH DT_STRTAB DT_SYMTAB DT_STRSZ DT_SYMENT',
      'supported_commands':['+','-','.', '>','<',','],
      'boundary_witnesses':4,
      'read_eof_witnesses':6,
      'read_failure_witnesses':2,
      'unverified':['Android loader acceptance','execution on actual Android','all 8 BF operations',
                    'Bionic/host syscall behavior','native Android compiler execution','Android native selfhosting'],
    }
    out=ROOT/'evidence/android_aarch64_subset.json'
    out.write_text(json.dumps(data,indent=2)+'\n')
    print(f'PASS Android subset prototype: {good} accepted, {errors} rejected, {seeds} independent seed cases; ELF parsed, code simulated under 2 bases')


def run_seed(executable,source):
    result=subprocess.run([str(executable),str(SOURCE)],input=source,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,check=True)
    assert len(result.stdout)==4193
    return result.stdout[:-1],result.stdout[-1]


if __name__=='__main__':
    main()

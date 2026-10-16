#!/usr/bin/env python3
"""Development-only translation of already BF-owned AArch64 byte templates into
an optimized standard BF source emitter. This tool is not invoked by users'
source compilation. The resulting .bf file owns all source classification and
all native output bytes at runtime; no Python assembler participates.
"""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/android_wide_slot_emitter_x86_64_linux.elf'
TARGET=ROOT/'experiments/android_streaming_compact_slots.bf'
NOP=bytes.fromhex('1f2003d5')
OPS=b'+-><.,'

class BF:
    def __init__(self):self.code=[];self.p=0
    def goto(self,idx):
        d=idx-self.p
        if d:self.code.append(('>' if d>0 else '<')*abs(d));self.p=idx
    def raw(self,s):self.code.append(s)
    def add(self,x):
        delta=x%256
        self.raw('+'*delta if delta<=128 else '-'*(256-delta))
    def clear(self,idx):self.goto(idx);self.raw('[-]')
    def copy_c1_to_c2(self):
        self.clear(2);self.clear(3)
        self.goto(1);self.raw('[->+>+<<]')
        self.goto(3);self.raw('[-<<+>>]')
        self.goto(1)
    def compare(self,op):
        # c4 = 1 if c1 == op. c1 preserved, c2 destroyed.
        self.copy_c1_to_c2();self.goto(2);self.add(-op)
        self.clear(4);self.goto(4);self.raw('+')
        self.goto(2);self.raw('[');self.raw('[-]');self.goto(4);self.raw('[-]');self.goto(2);self.raw(']')
        self.goto(4);self.raw('[')
    def end_compare(self):
        self.clear(4);self.goto(4);self.raw(']')
    def emit_data(self,data):
        # c5 output accumulator, c6 multiplicative scratch (zero before and after).
        # c5 must be zero at function entry and end.
        self.goto(5)
        prev=0
        for target in data:
            delta=(target-prev)%256
            signed=delta if delta<=128 else delta-256
            linear=abs(signed)
            # Factor a*b+r for shorter source when delta is large.
            best=(linear,'linear',0,0,0)
            for a in range(1,18):
                for b in range(2,33):
                    for r in range(0,4):
                        if (a*b+r)&255 != target:continue
                        # clear output, scratch init and loop; source code length not runtime steps.
                        cost=3+1+a+1+3+b+1+1+r+1+1+1 # conservative BF chars
                        if cost<best[0]:best=(cost,'factor',a,b,r)
            if best[1]=='factor':
                _,_,a,b,r=best
                self.clear(5);self.clear(6);self.goto(6);self.raw('+'*a+'[-');self.goto(5);self.raw('+'*b);self.goto(6);self.raw(']');self.goto(5);self.raw('+'*r)
            else:self.goto(5);self.add(signed)
            self.raw('.')
            prev=target
        self.clear(5)

def template(op):
    p=subprocess.run([str(BASE)],input=bytes((op,0)),capture_output=True,check=True)
    assert len(p.stdout)==53 and p.stdout[-5:-2]==b'\1\0\0',p.stdout[-5:]
    result=p.stdout[:48]
    while result.endswith(NOP):result=result[:-4]
    assert len(result)%4==0
    return result

def main():
    b=BF()
    b.goto(0);b.raw(',[')
    b.goto(1);b.raw(',')
    templates={op:template(op) for op in OPS}
    for op in OPS:
        b.compare(op)
        b.emit_data(bytes((1,len(templates[op])))+templates[op])
        b.end_compare()
    for op in b'[]':
        b.compare(op)
        b.goto(8);b.raw('[-]+')
        b.end_compare()
    b.goto(0);b.raw(',]')
    b.emit_data(b'\0')
    b.goto(8);b.raw('.')
    src=''.join(b.code)
    comment=(
      '# Brainfuck owned compact AArch64 streaming instruction bytes\n'
      '# The transport sends marker one and raw byte per record\n'
      '# A zero marker closes input\n'
      '# Output is tag one length byte and exact native instruction bytes\n'
      '# Trailing NOOP padding is not included\n'
      '# Brackets are rejected until dynamic relocation is connected\n'
      '# Final two bytes are zero terminator and error status\n'
    )
    TARGET.write_text(comment+src+'\n',encoding='ascii')
    print('source_commands',len(src),'template_lengths',{chr(k):len(v) for k,v in templates.items()})

if __name__=='__main__':main()

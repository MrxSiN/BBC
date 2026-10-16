#!/usr/bin/env python3
"""Development-only Brainfuck authoring aid for x64 loop branch displacements.

Runtime pairing data is processed exclusively by the saved .bf program.
The host-side code does not participate in production branch calculation.
"""
from pathlib import Path
from author_windows_linear_io import BF
ROOT=Path(__file__).resolve().parents[1]

def generate():
    b=BF()
    # Cells: 0 tag 1..6 three-byte positions 7 status 18..19 16-bit
    # displacement 10 loop distance 11 scratch 12 tag-test 13 zero-test
    # 14 fixed count 15 scratch 16 temp 17 scratch.
    def inc16():
        b.add(18,1)
        b.copy(18,11,15)
        b.set(13,1)
        b.if_once(11,lambda:b.clear(13))
        b.if_once(13,lambda:b.add(19,1))
    def record():
        # Already validated by upstream Brainfuck metadata and pairing passes.
        for pos in range(1,7):
            b.at(pos);b.op(',')
        for p in (2,3,5,6):
            b.if_once(p,lambda:b.set(7,1))
        b.copy(4,10,15)
        b.copy(1,11,15)
        b.begin(11);b.add(11,-1);b.add(10,-1);b.end(11)
        # [ opening byte position, and x64 rel32 for JE after closing slot.
        b.set(18,3);b.clear(19)
        b.begin(10)
        b.set(14,12)
        b.begin(14);inc16();b.add(14,-1);b.end(14)
        b.add(10,-1)
        b.end(10)
        b.emit(b'[');b.at(1);b.op('.')
        b.at(18);b.op('.');b.at(19);b.op('.')
        b.emit(b'\x00\x00')
        # Close JNE returns to the opening slot for the BF zero check:
        # negative (open rel32 + 6), sign extended to 32 bits.
        for _ in range(6):inc16()
        b.copy(18,11,15);b.clear(13)
        b.if_once(11,lambda:b.set(13,1))
        b.clear(11)
        b.begin(18);b.add(18,-1);b.add(11,-1);b.end(18)
        b.copy(11,18,15)
        b.clear(11)
        b.begin(19);b.add(19,-1);b.add(11,-1);b.end(19)
        b.copy(11,19,15)
        b.if_once(13,lambda:b.add(19,-1))
        b.emit(b']');b.at(4);b.op('.')
        b.at(18);b.op('.');b.at(19);b.op('.')
        b.emit(b'\xff\xff')
    b.at(0);b.op(',')
    b.begin(0)
    b.equal(93)
    b.set(12,1)
    b.if_once(3,lambda:b.clear(12))
    b.if_once(12,lambda:b.set(7,1))
    record()
    b.at(0);b.op(',')
    b.end(0)
    b.at(0);b.op(',') # source pairing status
    b.if_once(0,lambda:b.set(7,1))
    b.at(7);b.op('.')
    b.at(0)
    program=''.join(b.code)
    prefix=("# Windows x64 signed loop branch displacement records\n"
            "# Input is native Brainfuck bracket pairing records\n"
            "# Positions use one based offsets and at most sixty four commands\n"
            "# Each result contains both branch displacement values\n"
            "# Nonzero final status invalidates all preceding output\n")
    path=ROOT/'experiments/windows_x64_loop_rel32.bf'
    path.write_text(prefix+program+'\n', encoding='ascii')
    print('BF instructions',len(program),'path',path)
    assert len(program)<16128

if __name__=='__main__':generate()

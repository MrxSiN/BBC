#!/usr/bin/env python3
"""Author the opt-in streaming standard-BF canonical-clear IR prepass.

Only development source authoring. The emitted policy_clear56.bf performs
all detection, rewriting, and output itself. This helper is not part of the
compilation path and does not inspect program policy inputs.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'build'))
from author_policy_stages import BF


def main():
    b = BF()
    # Input/output are trusted RLE records (op,amount), ended by (0,0).
    # The BF-owned lookahead buffer uses 3 pairs and at most two pending pairs.
    # Cells 1..6 queue records, cell 7 pending count, cell 8 incoming amount.
    # Cells 20..26 serve boolean arithmetic; all remain zero between records.
    def emit(op, amount):
        b.at(op); b.raw('.')
        b.at(amount); b.raw('.')

    def store(src, dst):
        b.copy(src, dst, 26)

    def triple():
        b.set(23, 1)
        for cell, val in ((1, ord('[')), (2, 0),
                          (3, ord('-')), (4, 1),
                          (5, ord(']')), (6, 0)):
            b.eq(cell, val, 20, 21, 22)
            b.set(24, 1)
            b.once(20, lambda: b.clear(24))
            b.once(24, lambda: b.clear(23))
        b.copy(23, 25, 26)
        def folded():
            b.set(9, ord('0'))
            emit(9, 10)  # constant amount zero
            b.clear(9)
            for i in range(1, 7):b.clear(i)
            b.clear(7)
        b.once(25, folded)
        b.set(24, 1); b.once(23, lambda: b.clear(24))
        def unmodified():
            emit(1, 2)
            b.clear(1); b.clear(2)
            b.move(3, 1); b.move(4, 2)
            b.move(5, 3); b.move(6, 4)
            b.set(7, 2)
        b.once(24, unmodified)
        b.clear(23)

    b.at(0); b.raw(',[')
    b.at(8); b.raw(',')
    b.copy(7, 11, 26)  # Snapshot the queue length before mutation.
    for queued, cells in ((0, (1, 2)), (1, (3, 4)), (2, (5, 6))):
        b.eq(11, queued, 20, 21, 22)
        def append(cells=cells, queued=queued):
            store(0, cells[0]); store(8, cells[1])
            b.set(7, queued+1)
            if queued == 2:triple()
        # Predicates use the snapshot so a newly filled queue slot does not
        # get incorrectly processed again during the same input record.
        b.once(20, append)
    b.at(0); b.raw(',]')
    # Flush remaining 1 or 2 queue entries on source termination.
    b.eq(7, 1, 20, 21, 22); b.once(20, lambda: emit(1, 2))
    b.eq(7, 2, 20, 21, 22)
    b.once(20, lambda: (emit(1, 2), emit(3, 4)))
    # RLE's terminal marker consists of an opcode 0 and status 0.
    b.clear(0); b.at(0); b.raw('..')
    b.save('policy_clear56', 'Streaming canonical clear loop records in standard Brainfuck')

if __name__ == '__main__':main()

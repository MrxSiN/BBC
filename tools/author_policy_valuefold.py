"""Development-time assembly of the BF-only optional policy valuefold pass.

The generated experiments/policy_valuefold.bf interprets IR record bytes and
performs all value tracking itself.  This Python file is never a compiler
backend and is not imported by the production policy compiler.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'build'))
from author_policy_stages import BF

b = BF()

def eq(cell, value):
    b.eq(cell, value, flag=13, temp=11, restore=14)

def equal_pointer():
    b.equal(4, 7, flag=13, first=11, second=12, restore=14)
    b.once(13, lambda: b.equal(5, 8, flag=15, first=11, second=12, restore=14))

def source_write():
    b.copy(10, 19, 18)
    b.at(19); b.raw('[-')
    # Keep tracking a different cell: its value is not modified here.
    equal_pointer()
    b.once(15, lambda: b.clear(10))
    b.at(19); b.raw(']')

def arithmetic(op):
    b.copy(10, 19, 18)
    b.at(19); b.raw('[-')
    equal_pointer()
    def known():
        b.copy(1, 17, 18)
        b.at(17); b.raw('[-'); b.add(9, 1 if op == ord('+') else -1)
        b.at(17); b.raw(']')
        b.copy(9, 1, 18)
        eq(9, 0)
        b.set(0, ord('K')); b.set(6, 2)
        b.once(13, lambda: (b.set(0, ord('0')), b.set(6, 1)))
    b.once(15, known)
    # b.once must not retain its own loop flag. The arithmetic path leaves
    # known flag 10 equal to 1; consume a copy as the loop controller.
    b.at(19); b.raw(']')

# Per-record layout is opcode, operand, branch span (2), static ptr (2), cost.
# Known state occupies cells 7..10 and is never transported by the host.
for i in range(7):
    b.at(20); b.raw(',')
    b.at(20); b.raw('.')
    if i == 4: b.copy(20, 23, 22)
# Read opcode into cell 0, stop on the zero sentinel.
b.at(0); b.raw(',[')
for i in range(1, 7):
    b.at(i); b.raw(',')
for op in b'[I]E':
    eq(0, op)
    b.once(13, lambda: b.clear(10))
# A prior known direct clear yields an immediate constant store, rather than
# an AArch64 load/ALU/store sequence. Unknown writes invalidate only the
# tracked cell; intervening reads/pointer moves do not.
for op in b'+-':
    eq(0, op)
    b.once(13, lambda op=op: arithmetic(op))
for op in b',A':
    eq(0, op)
    b.once(13, source_write)
eq(0, ord('0'))
def reset_known():
    b.copy(4, 7, 17); b.copy(5, 8, 17)
    b.clear(9); b.set(10, 1)
b.once(13, lambda: (b.copy(23, 24, 25), b.once(24, reset_known)))
for i in range(7):
    b.at(i); b.raw('.')
b.at(0); b.raw(',]')
# Include the two-byte sentinel. Cell zero is known to be zero here.
b.at(0); b.raw('..')
b.save('policy_valuefold55', 'Fold statically known byte values into direct native stores')

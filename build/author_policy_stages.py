"""Development-only arrangement of raw BF; never imported by a compiler adapter."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRIDE, BASE = 15, 128


class BF:
    def __init__(self):
        self.p = 0
        self.parts = []

    def raw(self, code):
        self.parts.append(code)

    def at(self, cell):
        d = cell - self.p
        self.raw('>' * max(d, 0) + '<' * max(-d, 0))
        self.p = cell

    def clear(self, cell):
        self.at(cell); self.raw('[-]')

    def add(self, cell, amount):
        self.at(cell)
        amount %= 256
        self.raw('+' * amount if amount <= 128 else '-' * (256 - amount))

    def set(self, cell, value):
        self.clear(cell); self.add(cell, value)

    def move(self, source, target, scale=1):
        self.at(source); self.raw('[-'); self.add(target, scale)
        self.at(source); self.raw(']')

    def copy(self, source, target, temp):
        assert len({source, target, temp}) == 3
        self.clear(target); self.clear(temp)
        self.at(source); self.raw('[-'); self.add(target, 1); self.add(temp, 1)
        self.at(source); self.raw(']'); self.move(temp, source)

    def once(self, flag, body):
        self.at(flag); self.raw('[-'); body(); self.at(flag); self.raw(']')

    def eq(self, cell, value, flag=13, temp=9, restore=12):
        self.copy(cell, temp, restore)
        # copy restores this scratch to zero; use it for short constant construction.
        delta = (-value) % 256
        shortest = '+'*delta if delta <= 128 else '-'*(256-delta)
        d = restore-temp
        there = '>'*max(d,0)+'<'*max(-d,0)
        back = '<'*max(d,0)+'>'*max(-d,0)
        for sign in (1,-1):
            for a in range(1,17):
                for factor in range(1,17):
                    remainder = (delta-sign*a*factor) % 256
                    tail = '+'*remainder if remainder <= 128 else '-'*(256-remainder)
                    candidate = there+'+'*a+'[-'+back+('+' if sign == 1 else '-')*factor+there+']'+back+tail
                    if len(candidate) < len(shortest):shortest = candidate
        self.at(temp); self.raw(shortest); self.set(flag, 1)
        self.once(temp, lambda: (self.clear(temp), self.clear(flag)))

    def equal(self, left, right, flag=13, first=9, second=10, restore=12):
        self.copy(left, first, restore); self.copy(right, second, restore)
        self.at(second); self.raw('[-'); self.add(first, -1); self.at(second); self.raw(']')
        self.set(flag, 1); self.once(first, lambda: (self.clear(first), self.clear(flag)))

    def nonzero(self, cell, flag, temp, restore):
        self.copy(cell, temp, restore); self.clear(flag)
        self.once(temp, lambda: (self.clear(temp), self.set(flag, 1)))

    def inc16(self, low, high, temp=9, restore=12, flag=13):
        self.add(low, 1); self.eq(low, 0, flag, temp, restore)
        self.once(flag, lambda: self.add(high, 1))

    def dec16(self, low, high, temp=9, restore=12, flag=13):
        self.eq(low, 0, flag, temp, restore)
        self.once(flag, lambda: self.add(high, -1)); self.add(low, -1)

    def pair_flag(self, low, high, flag=9, temp=12, restore=13):
        self.clear(flag)
        for cell in (low, high):
            self.copy(cell, temp, restore)
            self.once(temp, lambda: (self.clear(temp), self.set(flag, 1)))

    def shift(self, records):
        self.at(records * STRIDE); self.p = 0

    def record_start(self):
        self.at(BASE); self.p = 0

    def rewind(self, carry=()):
        for cell in carry:self.move(cell, cell - STRIDE)
        self.shift(-1)
        self.at(0); self.raw('[')
        for cell in carry:self.move(cell, cell - STRIDE)
        self.shift(-1); self.raw(']')
        self.p = BASE - STRIDE

    def save(self, name, comment):
        code = ''.join(self.parts)
        # Adjacent bounded pointer/arithmetic runs can be shortened on this byte tape.
        import re
        code = re.sub(r'[<>]+', lambda m: '>' * max(m[0].count('>')-m[0].count('<'), 0)
                      + '<' * max(m[0].count('<')-m[0].count('>'), 0), code)
        code = re.sub(r'[+-]+', lambda m: ('+' * ((m[0].count('+')-m[0].count('-')) % 256)
                      if (m[0].count('+')-m[0].count('-')) % 256 <= 128
                      else '-' * (256-(m[0].count('+')-m[0].count('-')) % 256)), code)
        code = re.sub(r'(?:\[-\]){2,}', '[-]', code)
        assert not set(comment.encode()) & set(b'><+-.,[]')
        path = ROOT / 'experiments' / (name + '.bf')
        path.write_bytes(('# ' + comment + '\n' + code + '\n').encode())
        print(name, len(code))


def lexer():
    b = BF()
    def flush():
        b.nonzero(2, 9, 5, 6)
        b.once(9, lambda: (b.at(1), b.raw('.'), b.at(2), b.raw('.'), b.clear(2)))
    b.at(0); b.raw(',[')
    b.clear(3)
    for char in b'><+-':
        b.eq(0, char, 4, 5, 6); b.once(4, lambda: b.set(3, 1))
    b.equal(0, 1, 4, 5, 6, 8)
    b.set(7, 1)
    b.copy(3, 9, 8)
    b.once(4, lambda: b.once(9, lambda: b.clear(7)))
    b.once(7, lambda: (flush(), b.copy(0, 1, 8)))
    b.add(2, 1)
    b.eq(2, 255, 4, 5, 6); b.once(4, flush)
    b.set(4, 1); b.once(3, lambda: b.clear(4))
    b.once(4, lambda: (b.at(1), b.raw('.'), b.clear(2), b.raw('.'), b.clear(1)))
    b.at(0); b.raw(',]'); flush(); b.clear(0); b.raw('..')
    b.save('policy_rle', 'Stream validated commands into run length records with byte counts')


def load(b, width, prefix=0):
    for i in range(prefix):b.at(32+i); b.raw(',')
    b.record_start(); b.at(0); b.raw(',[')
    # The next record carries the count. Stop before allocating record 4097.
    b.eq(5, 16, 13, 9, 12)
    b.once(13, lambda: (b.set(14, 1), b.clear(0)))
    b.set(13, 1); b.nonzero(14, 12, 9, 10); b.once(12, lambda: b.clear(13))
    def ordinary():
        for i in range(1, width):b.at(i); b.raw(',')
        b.set(8, 1)
        b.move(4, 4+STRIDE); b.move(5, 5+STRIDE)
        b.shift(1); b.inc16(4, 5); b.at(0); b.raw(',')
    b.once(13, ordinary); b.at(0); b.raw(']')
    b.rewind((4, 5, 14))
    b.move(BASE-STRIDE+4, 20); b.move(BASE-STRIDE+5, 21)
    b.move(BASE-STRIDE+14, 22)


def match(b):
    b.set(4, 1); b.copy(8, 10, 9); b.clear(11); b.set(14, 1)
    b.at(4); b.raw('[')
    for cell in (4, 10, 11):b.move(cell, cell+STRIDE)
    b.shift(1)
    b.copy(8, 9, 12)
    b.at(9); b.raw('[-'); b.inc16(10, 11, 12, 13, 5)
    b.at(9); b.raw(']')
    # Cell five is free after the increment helper consumes its flag.
    b.eq(0, 0)
    b.once(13, lambda: (b.set(5, 1), b.clear(4)))
    b.eq(0, ord('['))
    def nested():
        b.eq(4, 255)
        b.once(13, lambda: (b.set(5, 1), b.clear(4)))
        b.nonzero(5, 13, 9, 12)
        b.set(12, 1); b.once(13, lambda: b.clear(12))
        b.once(12, lambda: b.add(4, 1))
    b.once(13, nested)
    b.eq(0, ord(']')); b.once(13, lambda: b.add(4, -1))
    b.at(4); b.raw(']')
    b.copy(10, 2, 12); b.copy(11, 3, 12)
    b.set(9, 1); b.copy(14, 12, 13)
    b.once(12, lambda: (b.clear(12), b.clear(9)))
    b.at(9); b.raw('['); b.clear(9)
    for cell in (10, 11, 5):b.move(cell, cell-STRIDE)
    b.shift(-1)
    b.set(9, 1); b.copy(14, 12, 13)
    b.once(12, lambda: (b.clear(12), b.clear(9)))
    b.at(9); b.raw(']')
    b.clear(2); b.clear(3); b.move(10, 2); b.move(11, 3)
    b.once(5, lambda: (b.clear(5), b.set(0, ord('?')))); b.clear(14)


def resolve_pass(b):
    b.record_start(); b.at(0); b.raw('[')
    b.eq(0, ord('[')); b.once(13, lambda: match(b))
    b.eq(0, ord(']'))
    def close():
        b.pair_flag(2, 3, 9, 12, 13)
        b.set(13, 1); b.once(9, lambda: b.clear(13))
        b.once(13, lambda: b.set(0, ord('?')))
    b.once(13, close)
    b.shift(1); b.at(0); b.raw(']'); b.rewind()


def output(b, fields, prefix):
    for cell in prefix:b.at(cell); b.raw('.')
    b.record_start(); b.at(0); b.raw('[')
    b.eq(0, ord('?')); b.once(13, lambda: b.set(4, 1))
    for i in range(fields) if isinstance(fields, int) else fields:b.at(i); b.raw('.')
    b.move(4, 4+STRIDE); b.shift(1); b.at(0); b.raw(']')
    b.raw('.')
    b.rewind((4,)); b.nonzero(BASE-STRIDE+4, 23, 24, 25)
    b.once(23, lambda: b.set(22, 1)); b.at(22); b.raw('.')


def resolver():
    b = BF(); load(b, 2); resolve_pass(b); output(b, 4, (20, 21))
    b.save('policy_resolve', 'Resolve bounded run length records entirely in standard Brainfuck')


def optimizer():
    b = BF(); load(b, 4, 2)
    # Fold only the clear pattern already eliminated by GM's BF compiler.
    b.record_start(); b.at(0); b.raw('[')
    def clear_candidate():
        def replace():
            b.set(0, ord('0')); b.set(STRIDE, ord('N')); b.set(2*STRIDE, ord('N'))
        b.eq(2, 3); b.once(13, lambda: (
            b.eq(3, 0), b.once(13, lambda: (
                b.eq(STRIDE, ord('-')), b.once(13, lambda: (
                    b.eq(STRIDE+1, 1), b.once(13, replace)))))))
    b.eq(0, ord('[')); b.once(13, clear_candidate)
    b.shift(1); b.at(0); b.raw(']'); b.rewind()

    # Annotate linear positions. Every loop must be checked before using these.
    b.record_start(); b.at(0); b.raw('[')
    b.copy(4, 6, 9); b.copy(5, 7, 9); b.clear(8)
    for op, direction in [(ord('>'), 1), (ord('<'), -1)]:
        def pointer_run(direction=direction):
            b.copy(1, 9, 10); b.at(9); b.raw('[-')
            (b.inc16 if direction == 1 else b.dec16)(4, 5, 10, 12, 13)
            b.at(9); b.raw(']'); b.copy(4, 6, 9); b.copy(5, 7, 9)
        b.eq(0, op); b.once(13, pointer_run)
    b.nonzero(5, 13, 9, 12); b.once(13, lambda: b.set(8, 1))
    b.eq(4, 255); b.once(13, lambda: b.set(8, 1))
    b.move(4, 4+STRIDE); b.move(5, 5+STRIDE)
    b.shift(1); b.at(0); b.raw(']'); b.rewind((4, 5))
    b.clear(BASE-STRIDE+4); b.clear(BASE-STRIDE+5)

    # Compare each opening's static position with its matching closing.
    b.record_start(); b.at(0); b.raw('[')
    def check_loop():
        b.copy(2, 10, 9); b.copy(3, 11, 9); b.dec16(10, 11, 9, 12, 13)
        b.copy(6, 4, 9); b.copy(7, 5, 9); b.set(14, 1)
        b.pair_flag(10, 11, 9, 12, 13)
        b.at(9); b.raw('['); b.clear(9); b.dec16(10, 11, 9, 12, 13)
        for cell in (4, 5, 10, 11):b.move(cell, cell+STRIDE)
        b.shift(1); b.pair_flag(10, 11, 9, 12, 13); b.at(9); b.raw(']')
        for left, right in [(4, 6), (5, 7)]:
            b.equal(left, right, 13, 9, 10, 12)
            b.set(12, 1); b.once(13, lambda: b.clear(12))
            b.once(12, lambda: b.set(8, 1))
        b.clear(4); b.clear(5)
        b.set(9, 1); b.copy(14, 12, 13)
        b.once(12, lambda: (b.clear(12), b.clear(9)))
        b.at(9); b.raw('['); b.clear(9); b.shift(-1)
        b.set(9, 1); b.copy(14, 12, 13)
        b.once(12, lambda: (b.clear(12), b.clear(9)))
        b.at(9); b.raw(']'); b.clear(14)
    b.eq(0, ord('[')); b.once(13, check_loop)
    b.shift(1); b.at(0); b.raw(']'); b.rewind()

    # Aggregate proof failure and the maximum annotated address.
    b.record_start(); b.at(0); b.raw('[')
    b.nonzero(8, 13, 9, 10); b.once(13, lambda: b.set(5, 1)); b.clear(8)
    b.copy(6, 9, 12); b.copy(4, 10, 12)
    b.at(9); b.raw('[-'); b.set(14, 1); b.nonzero(10, 11, 12, 13)
    b.once(11, lambda: (b.clear(14), b.add(10, -1)))
    b.once(14, lambda: b.set(8, 1)); b.at(9); b.raw(']')
    b.once(8, lambda: b.copy(6, 4, 12))
    b.move(4, 4+STRIDE); b.move(5, 5+STRIDE)
    b.shift(1); b.at(0); b.raw(']'); b.rewind((4, 5))
    b.move(BASE-STRIDE+4, 24); b.move(BASE-STRIDE+5, 25)
    b.add(24, 1); b.set(26, 1); b.nonzero(25, 27, 30, 31)
    b.once(27, lambda: b.clear(26)); b.clear(27)

    # Code lengths are in four byte instruction words, with no fixed slots.
    b.copy(26, BASE+4, 30); b.record_start(); b.at(0); b.raw('[')
    b.clear(8)
    for op, cost in [(ord('+'), 3), (ord('-'), 3), (ord('>'), 4), (ord('<'), 4),
                     (ord(','), 7), (ord('.'), 7), (ord('['), 4), (ord(']'), 2), (ord('0'), 1)]:
        def assign(op=op, cost=cost):
            b.set(8, cost)
            if op in b'><':
                b.copy(4, 9, 12); b.once(9, lambda: (b.clear(9), b.clear(8)))
        b.eq(0, op); b.once(13, assign)
    b.move(4, 4+STRIDE); b.shift(1); b.at(0); b.raw(']'); b.rewind((4,))
    b.clear(BASE-STRIDE+4)

    b.record_start(); b.at(0); b.raw('[')
    b.copy(8, 9, 10); b.at(9); b.raw('[-'); b.inc16(4, 5, 10, 11, 12)
    b.at(9); b.raw(']'); b.move(4, 4+STRIDE); b.move(5, 5+STRIDE)
    b.shift(1); b.at(0); b.raw(']'); b.rewind((4, 5))
    b.move(BASE-STRIDE+4, 28); b.move(BASE-STRIDE+5, 29)
    resolve_pass(b)
    output(b, (0, 1, 2, 3, 6, 7, 8), (20, 21, 28, 29, 26, 24, 27))
    b.save('policy_optimize', 'Prove balanced pointer loops and assign compact native word spans')


def affine():
    b = BF()
    # Initialize the coefficient ledger in unused record lanes of the first 256 records.
    def reset_coefficients():
        b.record_start(); b.set(5, 255); b.at(5); b.raw('[')
        b.clear(4); b.clear(9); b.set(12, 1); b.move(5, 5+STRIDE)
        b.shift(1); b.add(5, -1); b.at(5); b.raw(']')
        b.clear(4); b.clear(9); b.set(12, 1); b.at(12)
        b.raw('['+'<'*STRIDE+']'); b.p = BASE-STRIDE+12
    reset_coefficients()
    for i in range(7):b.at(32+i); b.raw(',')
    # Preserve the ledger markers while loading the BF-owned IR.
    b.record_start(); b.at(0); b.raw(',[')
    b.eq(5, 16, 13, 9, 10); b.once(13, lambda: (b.set(11, 1), b.clear(0)))
    b.set(13, 1); b.nonzero(11, 14, 9, 10); b.once(14, lambda: b.clear(13))
    def read_record():
        for cell in (1,2,3,6,7,8):b.at(cell); b.raw(',')
        b.move(4, 4+STRIDE); b.move(5, 5+STRIDE); b.shift(1)
        b.inc16(4, 5, 9, 10, 13); b.at(0); b.raw(',')
    b.once(13, read_record); b.at(0); b.raw(']'); b.rewind((4,5,11))
    b.move(BASE-STRIDE+4, 20); b.move(BASE-STRIDE+5, 21); b.move(BASE-STRIDE+11, 22)

    def home(carry=()):
        b.rewind(carry)

    def restore_visit():
        b.move(BASE-STRIDE+9, BASE+9)
        b.record_start(); b.set(5, 1); b.copy(10, 11, 13)
        b.once(11, lambda: (b.clear(11), b.clear(5)))
        b.at(5); b.raw('['); b.clear(5); b.move(9, 9+STRIDE); b.shift(1)
        b.set(5, 1); b.copy(10, 11, 13); b.once(11, lambda: (b.clear(11), b.clear(5)))
        b.at(5); b.raw(']'); b.clear(10)

    def reset_at_cursor():
        b.set(10, 1); home(); reset_coefficients(); restore_visit()

    def ledger_walk():
        b.record_start(); b.at(5); b.raw('[-')
        b.move(5, 5+STRIDE); b.move(9, 9+STRIDE); b.shift(1); b.at(5); b.raw(']')

    def ledger_rewind(carry=False):
        b.at(12); b.raw('[')
        if carry:b.move(9, 9-STRIDE)
        b.shift(-1); b.at(12); b.raw(']'); b.p = BASE-STRIDE+12

    def add_coefficient():
        b.set(10, 1); b.copy(1, 9, 5); b.copy(6, 11, 5); b.copy(0, 13, 5)
        home((9,11,13))
        for op, direction in [(ord('+'),1),(ord('-'),-1)]:
            def update(direction=direction):
                b.move(BASE-STRIDE+11, BASE+5); b.move(BASE-STRIDE+9, BASE+9)
                ledger_walk(); b.move(9, 4, direction); ledger_rewind()
            b.eq(BASE-STRIDE+13, op, 100, 101, 102); b.once(100, update)
        b.clear(BASE-STRIDE+13); restore_visit()

    def take_coefficient():
        b.set(10, 1); b.copy(6, 11, 5); home((11,))
        b.move(BASE-STRIDE+11, BASE+5); ledger_walk(); b.move(4, 9)
        ledger_rewind(True); restore_visit()

    def body_flag():
        b.clear(13)
        for op in b'+-><N':
            b.eq(0, op, 11, 9, 5); b.once(11, lambda: b.set(13, 1))

    b.copy(36, 40, 41)
    def run_fusion():
        b.record_start(); b.at(0); b.raw('[')
        def candidate():
            b.set(14, 1); reset_at_cursor(); b.shift(1); body_flag()
            b.at(13); b.raw('['); b.clear(13)
            for op in b'+-':
                b.eq(0, op, 11, 9, 5); b.once(11, add_coefficient)
            b.shift(1); body_flag(); b.at(13); b.raw(']')
            b.eq(0, ord(']'), 11, 9, 5)
            # Save recognition at the opening before consulting its coefficient.
            b.set(13, 1); b.once(11, lambda: b.clear(13))
            b.set(9, 1); b.copy(14, 10, 5); b.once(10, lambda: (b.clear(10),b.clear(9)))
            b.at(9); b.raw('['); b.clear(9); b.move(13, 13-STRIDE); b.shift(-1)
            b.set(9, 1); b.copy(14, 10, 5); b.once(10, lambda: (b.clear(10),b.clear(9)))
            b.at(9); b.raw(']')
            b.set(11, 1); b.once(13, lambda: b.clear(11))
            def recognized():
                take_coefficient(); b.eq(9, 255, 11, 13, 5)
                def replace():
                    b.set(0, ord('F')); b.set(8, 1); b.clear(9); b.shift(1)
                    b.eq(0, ord(']'), 11, 9, 5); b.set(13, 1); b.once(11, lambda: b.clear(13))
                    b.at(13); b.raw('['); b.clear(13); take_coefficient()
                    b.set(0, ord('N')); b.clear(8)
                    b.nonzero(9, 11, 13, 5)
                    b.once(11, lambda: (b.set(0, ord('A')), b.set(8, 4), b.copy(9, 1, 5)))
                    b.clear(9); b.shift(1)
                    b.eq(0, ord(']'), 11, 9, 5); b.set(13, 1); b.once(11, lambda: b.clear(13))
                    b.at(13); b.raw(']'); b.set(0, ord('0')); b.set(8, 1)
                    b.set(9, 1); b.copy(14, 10, 5); b.once(10, lambda: (b.clear(10),b.clear(9)))
                    b.at(9); b.raw('['); b.clear(9); b.shift(-1)
                    b.set(9, 1); b.copy(14, 10, 5); b.once(10, lambda: (b.clear(10),b.clear(9)))
                    b.at(9); b.raw(']')
                b.once(11, replace); b.clear(9)
            b.once(11, recognized); b.clear(14)
        b.eq(0, ord('['), 11, 9, 5); b.once(11, candidate)
        b.shift(1); b.at(0); b.raw(']')
        reset_at_cursor(); b.rewind()
    b.once(40, run_fusion)
    # New code lengths and spans follow the transformed IR, not the old slots.
    b.record_start(); b.at(0); b.raw('[')
    b.copy(8, 9, 10); b.at(9); b.raw('[-'); b.inc16(4, 5, 10, 11, 13)
    b.at(9); b.raw(']'); b.move(4, 4+STRIDE); b.move(5, 5+STRIDE)
    b.shift(1); b.at(0); b.raw(']'); b.rewind((4,5))
    b.move(BASE-STRIDE+4, 28); b.move(BASE-STRIDE+5, 29)
    b.copy(36, 26, 30); b.copy(37, 24, 30); b.copy(38, 27, 30)
    resolve_pass(b)
    output(b, (0,1,2,3,6,7,8), (20,21,28,29,26,24,27))
    b.save('policy_affine', 'Fuse proven bounded linear decrement loops into direct native multiply adds')


class BytesBF(BF):
    def __init__(self):
        super().__init__(); self.known = 0

    def byte(self, value):
        start = self.known
        reset = '[-]' if start is None else ''
        delta = (value-(start or 0)) % 256
        shortest = '+'*delta if delta <= 128 else '-'*(256-delta)
        for sign in (1, -1):
            for a in range(1, 17):
                for factor in range(1, 17):
                    remainder = (delta-sign*a*factor) % 256
                    tail = '+'*remainder if remainder <= 128 else '-'*(256-remainder)
                    candidate = '>'+'+'*a+'[-<'+('+' if sign == 1 else '-')*factor+'>]<'+tail
                    if len(candidate) < len(shortest):shortest = candidate
        self.at(20); self.raw(reset+shortest+'.'); self.known = value

    def word(self, value):
        for byte in value.to_bytes(4, 'little'):self.byte(byte)

    def var(self, cell):
        self.at(cell); self.raw('.')

    def imm(self, word, amount):
        self.copy(amount, 30, 33); self.set(31, (word >> 8) & 255)
        self.set(32, (word >> 16) & 255); self.set(34, 64)
        self.at(30); self.raw('[-'); self.add(31, 4); self.add(34, -1)
        self.eq(34, 0, 35, 36, 37)
        self.once(35, lambda: (self.set(34, 64), self.add(32, 1)))
        self.at(30); self.raw(']')
        self.byte(word & 255); self.var(31); self.var(32); self.byte(word >> 24)

    def memory(self, static, generic):
        self.copy(4, 13, 14); self.set(15, 1)
        self.known = None
        self.once(13, lambda: (self.clear(15), self.imm(static, 11)))
        self.known = None
        self.once(15, lambda: self.word(generic)); self.known = None

    def branch(self, word, low, high, adjustment=0, negative=False):
        self.copy(low, 30, 35); self.copy(high, 31, 35)
        if negative:
            self.clear(32); self.clear(33)
            self.at(30); self.raw('[-'); self.dec16(32, 33, 35, 36, 37)
            self.at(30); self.raw(']'); self.at(31); self.raw('[-')
            self.add(33, -1); self.at(31); self.raw(']')
            self.move(32, 30); self.move(33, 31)
        for _ in range(abs(adjustment)):
            (self.inc16 if adjustment > 0 else self.dec16)(30, 31, 35, 36, 37)
        self.set(32, word & 255); self.set(33, (word >> 8) & 255); self.set(34, (word >> 16) & 255)
        self.copy(31, 35, 36); self.at(35); self.raw('[-'); self.add(33, 32)
        self.eq(33, 0, 38, 36, 39); self.once(38, lambda: self.add(34, 1))
        self.at(35); self.raw(']')
        self.copy(30, 35, 36); self.set(37, 8)
        self.at(35); self.raw('[-'); self.add(32, 32); self.add(37, -1)
        self.eq(37, 0, 38, 36, 39)
        self.once(38, lambda: (self.set(37, 8), self.add(33, 1)))
        self.at(35); self.raw(']')
        if negative:self.add(34, 224)
        self.var(32); self.var(33); self.var(34); self.byte(word >> 24)


def operands():
    b = BytesBF()
    for i in range(7):b.at(i); b.raw(',')
    for i in (2, 3, 4, 5, 6):b.var(i)
    b.branch(0x54000003, 2, 3, 3)
    def immediate(amount):
        b.copy(amount, 30, 33); b.clear(31); b.clear(32); b.set(34, 64)
        b.at(30); b.raw('[-'); b.add(31, 4); b.add(34, -1)
        b.eq(34, 0, 35, 36, 37)
        b.once(35, lambda: (b.set(34, 64), b.add(32, 1)))
        b.at(30); b.raw(']'); b.var(31); b.var(32)
    immediate(5)
    b.copy(2, 16, 14); b.copy(3, 17, 14)
    b.at(7); b.raw(',[')
    # Each record starts with the previous record's output accumulator.
    b.known = None
    for i in range(8, 14):b.at(i); b.raw(',')
    b.var(7); immediate(8); immediate(11)
    b.branch(0x34000009, 9, 10, -1)
    b.branch(0x35000009, 9, 10, 1, True)
    b.branch(0xb4000006, 16, 17, 2)
    b.branch(0x54000002, 16, 17)
    b.clear(41); b.branch(0x52800011, 8, 41)
    b.copy(13, 40, 41); b.at(40); b.raw('[-'); b.dec16(16, 17, 35, 36, 37)
    b.at(40); b.raw(']'); b.at(7); b.raw(',]'); b.clear(7); b.raw('..')
    b.save('policy_operands', 'Encode native immediates and compact branch operands in Brainfuck')


def oneshot():
    b = BF()
    for i in range(7): b.at(32+i); b.raw(',')
    b.record_start(); b.at(0); b.raw(',[')
    b.eq(5, 16); b.once(13, lambda: (b.set(14, 1), b.clear(0)))
    b.set(13, 1); b.nonzero(14, 12, 9, 10); b.once(12, lambda: b.clear(13))
    def read_record():
        for cell in (1,2,3,6,7,8): b.at(cell); b.raw(',')
        b.move(4,4+STRIDE); b.move(5,5+STRIDE); b.shift(1)
        b.inc16(4,5); b.at(0); b.raw(',')
    b.once(13,read_record); b.at(0); b.raw(']'); b.rewind((4,5,14))
    b.move(BASE-STRIDE+4,20); b.move(BASE-STRIDE+5,21); b.move(BASE-STRIDE+14,22)
    def candidate():
        b.set(14,1); b.copy(6,4,9); b.clear(5); b.set(10,1)
        b.at(10); b.raw('[')
        for cell in (4,5,10): b.move(cell,cell+STRIDE)
        b.shift(1)
        for op in b'+-,A0':
            def write(op=op):
                b.equal(6,4,13,9,11,12)
                b.once(13,lambda: b.set(5,int(op==ord('0'))))
            b.eq(0,op); b.once(13,write)
        # Nested control flow invalidates the clear fact until a later direct clear.
        for op in b'[I':
            b.eq(0,op); b.once(13,lambda: (b.add(10,1),b.clear(5)))
        for op in b']E':
            def close():
                b.add(10,-1); b.nonzero(10,13,9,12)
                b.once(13,lambda: b.clear(5))
            b.eq(0,op); b.once(13,close)
        b.eq(0,0); b.once(13,lambda: (b.clear(10),b.clear(5)))
        b.at(10); b.raw(']')
        b.copy(5,9,12); b.once(9,lambda: (b.set(0,ord('E')),b.clear(8)))
        b.clear(4); b.set(9,1); b.copy(14,12,13)
        b.once(12,lambda: (b.clear(12),b.clear(9)))
        b.at(9); b.raw('['); b.clear(9); b.move(5,5-STRIDE); b.shift(-1)
        b.set(9,1); b.copy(14,12,13); b.once(12,lambda: (b.clear(12),b.clear(9)))
        b.at(9); b.raw(']'); b.clear(14)
        b.once(5,lambda: (b.set(0,ord('I')),b.set(8,2)))
    def transform():
        b.record_start(); b.at(0); b.raw('[')
        b.eq(0,ord('[')); b.once(13,candidate)
        b.shift(1); b.at(0); b.raw(']'); b.rewind()
    b.copy(36,40,41); b.once(40,transform)
    # The existing matcher sees ordinary brackets; the amount lane remembers kind.
    b.record_start(); b.at(0); b.raw('[')
    for op, normal in [(ord('I'),ord('[')),(ord('E'),ord(']'))]:
        b.eq(0,op); b.once(13,lambda normal=normal: (b.set(0,normal),b.set(1,1)))
    b.copy(8,9,10); b.at(9); b.raw('[-'); b.inc16(4,5,10,11,13)
    b.at(9); b.raw(']'); b.move(4,4+STRIDE); b.move(5,5+STRIDE)
    b.shift(1); b.at(0); b.raw(']'); b.rewind((4,5))
    b.move(BASE-STRIDE+4,28); b.move(BASE-STRIDE+5,29); resolve_pass(b)
    b.record_start(); b.at(0); b.raw('[')
    for normal, op in [(ord('['),ord('I')),(ord(']'),ord('E'))]:
        def restore(op=op):
            b.eq(1,1); b.once(13,lambda: (b.set(0,op),b.clear(1)))
        b.eq(0,normal); b.once(13,restore)
    b.shift(1); b.at(0); b.raw(']'); b.rewind()
    output(b,(0,1,2,3,6,7,8),(20,21,28,29,36,37,38))
    b.save('policy_oneshot','Remove loop backedges only after a guaranteed source cell clear')


def codegen():
    b = BytesBF()
    # Literal output cells sixty and sixty one stay clear of encoded operands.
    b.known = None
    def byte(value):
        old_parts, old_pointer = b.parts, b.p
        temporary = BytesBF(); temporary.p = b.p-40; temporary.known = b.known
        temporary.byte(value)
        b.parts.extend(temporary.parts); b.p = temporary.p+40; b.known = temporary.known
    def word(value):
        for value in value.to_bytes(4, 'little'):byte(value)
    def raw_word(first, last, fields):
        byte(first)
        for c in fields:b.var(c)
        byte(last)
    def memory(load, zero=False, source=False):
        b.copy(2, 10, 11); b.set(12, 1)
        b.known = None
        def bounded():
            b.clear(12); byte(0x9f if zero else (0x8f if source else 0x89)); b.var(19)
            if load:b.add(20, 64)
            b.var(20)
            if load:b.add(20, -64)
            byte(0x39)
        b.once(10, bounded); b.known = None
        b.once(12, lambda: word((0x3940016f if source else 0x39400169) if load else (0x3900017f if zero else 0x39000169)))
        b.known = None
    for i in range(11):b.at(i); b.raw(',')
    for i in range(5):b.var(i)
    for value in (0xaa1f03ea, 0xaa0403eb, 0xaa1f03ec, 0xaa1f03ed, 0xaa0603f0, 0xaa1f03ee):word(value)
    b.copy(2, 43, 44); b.set(45, 1); b.known = None
    b.once(43, lambda: (b.clear(45), raw_word(0xbf, 0xf1, (9,10)),
                        *[b.var(i) for i in range(5,9)]))
    b.known = None; b.once(45, lambda: (word(0xd503201f), word(0xd503201f)))
    b.known = None
    b.at(16); b.raw(',[')
    for i in range(17, 41):b.at(i); b.raw(',')
    for op in (ord('+'), ord('-')):
        def arithmetic(op=op):
            memory(True); b.add(17, 1); raw_word(0x29, 0x11 if op == ord('+') else 0x51, (17,18))
            b.add(17, -1); memory(False)
        b.eq(16, op, 7, 8, 9); b.known = None; b.once(7, arithmetic); b.known = None
    for op in (ord('>'), ord('<')):
        def pointer(op=op):
            b.copy(2, 10, 11); b.set(12, 1); b.once(10, lambda: b.clear(12))
            def generic():
                b.add(17, 1); raw_word(0x4a, 0x91 if op == ord('>') else 0xd1, (17,18)); b.add(17, -1)
                word(0xeb05015f)
                for i in range(33,37):b.var(i)
                word(0x8b0a008b)
            b.once(12, generic)
        b.eq(16, op, 7, 8, 9); b.known = None; b.once(7, pointer); b.known = None
    def read():
        word(0xeb01019f); word(0x540000a2); word(0x386c6809); word(0x9100058c)
        memory(False); word(0x14000002); memory(False, True)
    b.eq(16, ord(','), 7, 8, 9); b.known = None; b.once(7, read); b.known = None
    def write():
        word(0xeb0301bf); word(0x540000a2); memory(True)
        for value in (0x382d6849, 0x910005ad, 0x14000002, 0x5280004e):word(value)
    b.eq(16, ord('.'), 7, 8, 9); b.known = None; b.once(7, write); b.known = None
    def opening():
        memory(True)
        for i in range(21,25):b.var(i)
        for i in range(29,33):b.var(i)
        word(0xd10004c6)
    b.eq(16, ord('['), 7, 8, 9); b.known = None; b.once(7, opening); b.known = None
    def conditional():
        memory(True)
        for i in range(21,25): b.var(i)
    b.eq(16,ord('I'),7,8,9); b.known = None; b.once(7,conditional); b.known = None
    def closing():
        memory(True)
        for i in range(25,29):b.var(i)
    b.eq(16, ord(']'), 7, 8, 9); b.known = None; b.once(7, closing); b.known = None
    b.eq(16, ord('0'), 7, 8, 9); b.known = None
    b.once(7, lambda: memory(False, True)); b.known = None
    b.eq(16, ord('F'), 7, 8, 9); b.known = None
    b.once(7, lambda: memory(True, source=True)); b.known = None
    def multiply_add():
        memory(True)
        for i in range(37,41):b.var(i)
        word(0x1b1125e9); memory(False)
    b.eq(16, ord('A'), 7, 8, 9); b.known = None
    b.once(7, multiply_add); b.known = None
    b.at(16); b.raw(',]')
    for value in (0x2a0e03e0, 0x14000005, 0x52800020, 0x14000003, 0xd10004c6,
                  0x52800060, 0xcb060201, 0xf90000ed, 0xd65f03c0):word(value)
    b.clear(16); b.var(16)
    b.save('policy_codegen', 'Emit compact AArch64 callable code from BF encoded operands')


def elf():
    import struct
    b = BytesBF()
    for i in range(5):b.at(i); b.raw(',')
    # Input is words low high proof tape low tape high then the native code.
    b.set(30, 196); b.clear(31); b.clear(32)
    b.copy(1, 33, 34); b.at(33); b.raw('[-'); b.add(31, 4)
    b.eq(31, 0, 35, 36, 37); b.once(35, lambda: b.add(32, 1))
    b.at(33); b.raw(']'); b.copy(0, 33, 34); b.at(33); b.raw('[-'); b.add(30, 4)
    b.eq(30, 0, 35, 36, 37)
    b.once(35, lambda: (b.add(31, 1), b.eq(31, 0, 35, 36, 37),
                       b.once(35, lambda: b.add(32, 1))))
    b.at(33); b.raw(']')
    header = bytearray(b'\x7fELF\x02\x01\x01'+bytes(9))
    header += struct.pack('<HHIQQQIHHHHHH', 3, 183, 1, 128, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    header += struct.pack('<IIQQQQQQ', 1, 5, 0, 0, 0, 0, 0, 16384)
    for i, byte in enumerate(header):
        if i in (96, 97, 98, 104, 105, 106):b.var(30+(i % 8))
        else:b.byte(byte)
    for byte in b'BFP1':b.byte(byte)
    b.var(3); b.var(4); b.var(2); b.byte(0)
    # Code length is ELF length minus the 128 byte header.
    b.copy(30, 40, 43); b.copy(31, 41, 43); b.copy(32, 42, 43)
    b.set(48, 128); b.at(48); b.raw('[-')
    b.eq(40, 0, 44, 45, 46)
    b.once(44, lambda: (b.eq(41, 0, 44, 45, 46),
                        b.once(44, lambda: b.add(42, -1)), b.add(41, -1)))
    b.add(40, -1); b.at(48); b.raw(']')
    def flag():
        b.clear(44)
        for c in (40, 41, 42):
            b.copy(c, 45, 46); b.once(45, lambda: (b.clear(45), b.set(44, 1)))
    flag(); b.at(44); b.raw('[')
    b.at(47); b.raw(',.')
    b.eq(40, 0, 44, 45, 46)
    b.once(44, lambda: (b.eq(41, 0, 44, 45, 46), b.once(44, lambda: b.add(42, -1)), b.add(41, -1)))
    b.add(40, -1); flag(); b.at(44); b.raw(']')
    b.at(47); b.raw(',.')
    b.save('policy_elf', 'Pack BF generated callable code into a position independent ELF image')


if __name__ == '__main__':
    lexer(); resolver(); optimizer(); affine(); oneshot(); operands(); codegen(); elf()

"""Development-only BF text authoring. Runtime compilation uses the saved BF only."""
import importlib.util
from pathlib import Path
import struct
import itertools

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bf_text', ROOT / 'build/author_policy_stages.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class BF(module.BF):
    def shift4(self, direction):
        self.at(4 * direction); self.p = 0

    def eq4(self, cell, value, flag=5, temp=6, restore=7):
        self.eq(cell, value, flag, temp, restore)

    def inc(self, low=1, high=2):
        self.add(low, 1); self.eq4(low, 0)
        self.once(5, lambda: self.add(high, 1))

    def dec(self, low=1, high=2):
        self.eq4(low, 0); self.once(5, lambda: self.add(high, -1)); self.add(low, -1)

    def byte(self, value, out=1, scratch=2):
        # A constant construction optimization of BF text, not runtime encoding.
        self.at(out)
        delta = (value - getattr(self, 'literal_value', 0)) % 256
        best = '+' * delta if delta <= 128 else '-' * (256 - delta)
        for sign in (1, -1):
            for a in range(1, 17):
                for factor in range(1, 17):
                    tail = (delta - sign * a * factor) % 256
                    tailcode = '+' * tail if tail <= 128 else '-' * (256 - tail)
                    distance = scratch - out
                    there = '>' * max(distance, 0) + '<' * max(-distance, 0)
                    back = '<' * max(distance, 0) + '>' * max(-distance, 0)
                    candidate = there + '+' * a + '[-' + back + ('+' if sign == 1 else '-') * factor + there + ']' + back + tailcode
                    if len(candidate) < len(best): best = candidate
        self.raw(best + '.'); self.literal_value = value

    def literal(self, data, out=1, scratch=2):
        self.clear(out); self.clear(scratch); self.literal_value = 0
        for value in data: self.byte(value, out, scratch)
        self.clear(out); self.literal_value = 0

    def words(self, words):
        for word, group in itertools.groupby(words):
            count = len(list(group))
            if count == 1:
                self.literal(struct.pack('<I', word))
            else:
                self.set(3, count); self.at(3); self.raw('[-')
                self.literal(struct.pack('<I', word)); self.at(3); self.raw(']')


NOP = 0xd503201f
EXIT = [0xd2800000, 0xd2800ba8, 0xd4000001]
# x19 current pointer, x20 tape base, x21 exclusive end; x9 byte scratch.
ADD = [0x39400269, 0x11000529, 0x39000269]
SUB = [0x39400269, 0x51000529, 0x39000269]
RIGHT = [0x91000673, 0xeb15027f, 0x540001c3, 0xd2800040, 0xd2800ba8, 0xd4000001]
LEFT = [0xd1000673, 0xeb14027f, 0x540001c2, 0xd2800040, 0xd2800ba8, 0xd4000001]
# EINTR retries reconstruct syscall arguments; EOF is zero.
READ = [0x3900027f, 0xd2800000, 0xaa1303e1, 0xd2800022, 0xd28007e8, 0xd4000001,
        0xb100101f, 0x54ffff40, 0xb4000100, 0xf100041f, 0x540000c0,
        0xd2800080, 0xd2800ba8, 0xd4000001]
WRITE = [0xd2800020, 0xaa1303e1, 0xd2800022, 0xd2800808, 0xd4000001,
         0xb100101f, 0x54ffff40, 0xf100041f, 0x54000100,
         0xd2800060, 0xd2800ba8, 0xd4000001]


def validate(b):
    # Bracket depth travels in record lane one; neighboring lanes are scratch.
    b.at(68); b.p = 0; b.at(0); b.raw('[')
    for char, opening in ((91, True), (93, False)):
        b.eq4(0, char, 2, 3, 1 + 4)
        def bracket(opening=opening):
            if opening: b.add(1, 1)
            b.copy(1, 0, 2); b.set(3, 1)
            b.once(0, lambda: (b.clear(0), b.clear(3)))
            b.set(0, char)
            def invalid():
                b.clear(4); b.set(1, 1)
            if opening:
                b.once(3, invalid)
            else:
                b.set(2, 1); b.once(3, lambda: (invalid(), b.clear(2)))
                b.once(2, lambda: b.add(1, -1))
        b.once(2, bracket)
    b.move(1, 5); b.shift4(1); b.at(0); b.raw(']')
    b.move(1, -3); b.shift4(-1); b.at(0); b.raw('[')
    b.move(1, -3); b.shift4(-1); b.at(0); b.raw(']')
    b.p = 64; b.copy(65, 66, 67)
    b.once(66, lambda: (b.clear(66), b.set(0, 1)))


def carry(b, direction, cells=(1, 2, 3)):
    for c in cells: b.move(c, c + 4 * direction)
    b.shift4(direction)


def branch(b, opening):
    b.clear(0); b.set(3, 1)
    b.set(1, 1 if opening else 255); b.set(2, 0 if opening else 255)
    direction = 1 if opening else -1
    carry(b, direction); b.at(3); b.raw('[')
    b.inc()
    for char, change in ((91, direction), (93, -direction)):
        b.eq4(0, char); b.once(5, lambda change=change: b.add(3, change))
    carry(b, direction); b.at(3); b.raw(']')
    carry(b, -direction, (1, 2)); b.at(0); b.raw('[')
    carry(b, -direction, (1, 2)); b.at(0); b.raw(']')
    b.set(0, 91 if opening else 93)
    # Encode imm19 shifted five bits: low byte is E9; upper pair is 2*n-1.
    b.move(2, 6, 2); b.move(6, 2); b.move(1, 5)
    b.at(5); b.raw('[-'); b.add(1, 2)
    b.eq4(1, 0, 3, 6, 7); b.once(3, lambda: b.add(2, 1))
    b.at(5); b.raw(']')
    if not opening:
        b.copy(1, 5, 6); b.once(5, lambda: (b.clear(5), b.add(2, 1)))
        b.move(1, 5, -1); b.move(5, 1)
        b.move(2, 6, -1); b.move(6, 2)
    b.dec()
    b.literal(struct.pack('<I', 0x39400269), out=5, scratch=6)
    b.literal(bytes([233]), out=5, scratch=6)
    b.at(1); b.raw('.'); b.at(2); b.raw('.')
    b.literal(bytes([0x34 if opening else 0x35]), out=5, scratch=6)
    b.clear(1); b.clear(2)
    b.words([NOP] * 14)


def author_core():
    old = bytes(c for c in (ROOT / 'compiler/core.bf').read_bytes() if c in b'><+-.,[]')
    b = BF(); b.raw(old[:2462].decode()); b.p = 60
    b.clear(0); b.move(69, 0)
    for cell in range(1, 68): b.clear(cell)
    validate(b)
    b.set(1, 1); b.copy(0, 2, 3); b.once(2, lambda: (b.clear(2), b.clear(1)))
    b.at(1); b.raw('[-')
    # Accumulate exact ELF size into cells 10..12, one 64-byte slot per command.
    b.set(10, 208); b.set(11, 0); b.set(12, 0)
    b.at(68); b.p = 0; b.at(0); b.raw('[')
    b.inc(); carry(b, 1, (1, 2)); b.at(0); b.raw(']')
    carry(b, -1, (1, 2)); b.at(0); b.raw('[')
    carry(b, -1, (1, 2)); b.at(0); b.raw(']')
    b.p = 64; b.move(65, 14); b.move(66, 15)
    # size = 208 + count*64; three-byte increment by 64, repeated count times.
    b.at(0)
    b.copy(14, 16, 17); b.copy(15, 18, 19); b.clear(20)
    def count_flag():
        b.clear(20)
        for c in (16, 18):
            b.copy(c, 21, 22); b.once(21, lambda: (b.clear(21), b.set(20, 1)))
    count_flag(); b.at(20); b.raw('[')
    b.add(10, 64); b.eq(10, 16, 23, 21, 22)
    b.once(23, lambda: (b.add(11, 1), b.eq(11, 0, 23, 21, 22), b.once(23, lambda: b.add(12, 1))))
    b.eq(16, 0, 23, 21, 22); b.once(23, lambda: b.add(18, -1)); b.add(16, -1)
    count_flag(); b.at(20); b.raw(']')
    # 64-byte ELF header, two PT_LOAD headers, 20-byte startup, 12-byte exit.
    header = struct.pack('<16sHHIQQQIHHHHHH', b'\x7fELF\x02\x01\x01'+bytes(9), 3, 183, 1,
                         176, 64, 0, 0, 64, 56, 2, 0, 0, 0)
    rx = struct.pack('<IIQQQQQQ', 1, 5, 0, 0, 0, 0, 0, 0x4000)
    rw = struct.pack('<IIQQQQQQ', 1, 6, 0, 0x200000, 0x200000, 0, 65536, 0x4000)
    layout = header + rx + rw
    for i, value in enumerate(layout):
        if i in (96, 97, 98, 104, 105, 106):
            b.copy(10 + (i % 8), 1, 2); b.at(1); b.raw('.'); b.clear(1); b.literal_value = 0
        else: b.byte(value)
    b.clear(1)
    b.words([0x90001014, 0xaa1403f3, 0x91404295, NOP, NOP])
    b.at(68); b.p = 0; b.at(0); b.raw('[')
    for char, words in [(43, ADD), (45, SUB), (62, RIGHT), (60, LEFT), (44, READ), (46, WRITE)]:
        b.eq4(0, char, 1, 2, 3)
        b.once(1, lambda words=words: b.words(words + [NOP] * (16 - len(words))))
    for char, opening in ((91, True), (93, False)):
        b.eq4(0, char, 1, 2, 3); b.once(1, lambda opening=opening: branch(b, opening))
    b.clear(1); b.clear(2); b.clear(3); b.shift4(1); b.at(0); b.raw(']')
    b.shift4(-1); b.at(0); b.raw('[<<<<]'); b.p = 64
    b.at(1); b.p = 1; b.words(EXIT)
    b.at(1); b.raw(']'); b.at(0); b.raw('.')
    # Preserve the audited decoder bytes verbatim; normalize only the new suffix.
    b.parts[0] = ''
    b.save('android_selfhost_core', 'Android freestanding native compiler using the canonical BF decoder')
    path = ROOT / 'experiments/android_selfhost_core.bf'
    title, suffix = path.read_bytes().split(b'\n', 1)
    path.write_bytes(title + b'\n# Retain the canonical Linux decoder\n' + old[:2462] +
                     b'\n# Validate brackets then emit Android code\n' + suffix)
    path.replace(ROOT / 'compiler/android_core.bf')


def compact_elf(words):
    code = struct.pack('<' + 'I' * len(words), *words)
    size = 128 + len(code)
    return (struct.pack('<16sHHIQQQIHHHHHH', b'\x7fELF\x02\x01\x01'+bytes(9),
                        3, 183, 1, 128, 64, 0, 0, 64, 56, 1, 0, 0, 0)
            + struct.pack('<IIQQQQQQ', 1, 5, 0, 0, 0, size, size, 0x4000) + bytes(8) + code)


def compact_words(stream):
    # Development-only fixed-template labels. Saved BF emits these bytes itself.
    words = []; labels = {}; patches = []
    def label(name): labels[name] = len(words)
    def emit(*values): words.extend(values)
    def jump(base, target, bits=19, shift=5):
        patches.append((len(words), base, target, bits, shift)); emit(base)
    emit(0xd10043ff, 0xa9007fff, 0x910003e1 if stream else 0x910007e1, 0xd2800022)
    label('read')
    emit(0xd2800000, 0xd28007e8, 0xd4000001, 0xb100101f)
    jump(0x54000000, 'read')
    jump(0xb4000000, 'eof' if stream else 'write')
    emit(0xf100041f); jump(0x54000001, 'read_fail')
    if stream:
        emit(0x39400029); jump(0x34000009, 'normal')
    label('write')
    emit(0xd2800020, 0xd2800808, 0xd4000001, 0xb100101f)
    jump(0x54000000, 'write')
    emit(0xf100041f); jump(0x54000001, 'write_fail')
    if stream:
        jump(0x14000000, 'read', 26, 0)
        label('eof'); emit(0x3900003f)
    label('normal'); emit(0xd2800000)
    label('exit'); emit(0xd2800ba8, 0xd4000001)
    label('read_fail'); emit(0xd2800080); jump(0x14000000, 'exit', 26, 0)
    label('write_fail'); emit(0xd2800060); jump(0x14000000, 'exit', 26, 0)
    for index, base, target, bits, shift in patches:
        distance = labels[target] - index
        assert -(1 << (bits-1)) <= distance < (1 << (bits-1))
        words[index] = base | ((distance & ((1 << bits)-1)) << shift)
    return words


def author_compact():
    b = BF(); b.at(1); b.raw(',[>,]<[<]'); b.p = 0
    b.set(19, 1); b.clear(17); b.clear(18)
    for pattern, target in ((b',[>+<-]>.', 18), (b',[->+<]>.', 18), (b',[.,]', 17)):
        b.set(12, 1)
        for i, value in enumerate(pattern + b'\0'):
            b.eq(i + 1, value, 13, 14, 15)
            b.set(16, 1); b.once(13, lambda: b.clear(16))
            b.once(16, lambda: b.clear(12))
        b.once(12, lambda target=target: (b.set(target, 1), b.clear(19)))
    b.once(18, lambda: b.literal(compact_elf(compact_words(False))))
    b.once(17, lambda: b.literal(compact_elf(compact_words(True))))
    # Consume the trusted two-load-header ELF emitted by the native BF core.
    # BF reads the image size itself; the transport never calculates ELF sizes.
    def image_byte():
        b.at(50); b.raw(','); b.copy(19, 51, 53)
        b.once(51, lambda: (b.at(50), b.raw('.')))
    for count, save in ((96, None), (1, 40), (1, 41), (1, 42), (77, None)):
        b.set(52, count); b.at(52); b.raw('[-'); image_byte()
        if save is not None: b.copy(50, save, 53)
        b.at(52); b.raw(']')
    b.eq(40, 208, 51, 53, 54); b.set(55, 1)
    b.once(51, lambda: b.clear(55))
    def borrow():
        b.eq(41, 0, 51, 53, 54); b.once(51, lambda: b.add(42, -1)); b.add(41, -1)
    b.once(55, borrow); b.add(40, -176)
    def remaining():
        b.clear(55)
        for cell in (40, 41, 42):
            b.copy(cell, 51, 53); b.once(51, lambda: (b.clear(51), b.set(55, 1)))
    remaining(); b.at(55); b.raw('[')
    b.eq(40, 0, 51, 53, 54); b.once(51, borrow); b.add(40, -1)
    image_byte(); remaining(); b.at(55); b.raw(']')
    b.at(56); b.raw(',.')
    b.save('android_compact_optimize', 'Compact proven small BF programs into one freestanding code mapping')


if __name__ == '__main__':
    author_core(); author_compact()

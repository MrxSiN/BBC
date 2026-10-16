"""Independent RLE/bracket oracle; production transformation runs in raw BF."""
from itertools import groupby
from pathlib import Path
import random
import subprocess
import sys
import struct
import platform

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build/policy_native'
BUILD.mkdir(exist_ok=True)
SEEDS = ROOT / 'build/android_optimization'
_LINUX_SEED = None


def linux_seed():
    global _LINUX_SEED
    if _LINUX_SEED is None:
        sys.path.insert(0, str(ROOT))
        from bootstrap.linux_policy_native import LinuxPolicyNative
        _LINUX_SEED = LinuxPolicyNative(BUILD / 'fast_seed', mode='seed')
    return _LINUX_SEED


def stage(name, payload, seed='seed'):
    if platform.system() == 'Linux':
        # Development BF interpreter only; optimization and machine-code
        # generation remain entirely in experiments/policy_*.bf.
        return linux_seed().stage(name, payload)
    process = subprocess.run([str(SEEDS / (seed + '.exe')),
                              str(ROOT / 'experiments' / (name + '.bf')), '10000000000'],
                             input=payload, capture_output=True, check=True, timeout=180)
    return process.stdout


def rle(source):
    tokens = []
    for command, grouped in groupby(source):
        count = sum(1 for _ in grouped)
        if command in b'><+-':
            tokens.extend((command, min(255, count-index)) for index in range(0, count, 255))
        else:tokens.extend((command, 0) for _ in range(count))
    return tokens


def resolve(tokens):
    stack, spans = [], {}
    for index, (op, _) in enumerate(tokens):
        if op == ord('['):
            if len(stack) == 255:return None
            stack.append(index)
        elif op == ord(']'):
            if not stack:return None
            opening = stack.pop()
            spans[index] = spans[opening] = index-opening+1
    if stack or len(tokens) > 4096:return None
    return len(tokens).to_bytes(2, 'little') + b''.join(
        bytes([op, count]) + spans.get(index, 0).to_bytes(2, 'little')
        for index, (op, count) in enumerate(tokens)) + b'\0\0'


def optimize(resolved):
    count = int.from_bytes(resolved[:2], 'little')
    records = [[resolved[2+4*i], resolved[3+4*i],
                int.from_bytes(resolved[4+4*i:6+4*i], 'little'), 0]
               for i in range(count)]
    for i, record in enumerate(records):
        if record[0] == ord('[') and record[2] == 3 and records[i+1][:2] == [ord('-'), 1]:
            record[0] = ord('0'); records[i+1][0] = records[i+2][0] = ord('N')
    pointer, bounded = 0, True
    for record in records:
        if record[0] == ord('>'):pointer = (pointer+record[1]) & 65535
        elif record[0] == ord('<'):pointer = (pointer-record[1]) & 65535
        record[3] = pointer
        if pointer >= 255:bounded = False
    for i, record in enumerate(records):
        if record[0] == ord('[') and record[3] != records[i+record[2]-1][3]:bounded = False
    costs = {ord('+'):3, ord('-'):3, ord('>'):0 if bounded else 4, ord('<'):0 if bounded else 4,
             ord(','):7, ord('.'):7, ord('['):4, ord(']'):2, ord('0'):1, ord('N'):0}
    total = sum(costs[record[0]] for record in records)
    for i, record in enumerate(records):
        if record[0] == ord('['):
            closing = i+record[2]-1
            record[2] = records[closing][2] = sum(costs[r[0]] for r in records[i:closing+1])
    tape = ((max((r[3] & 255 for r in records), default=0)+1) & 255)
    prefix = count.to_bytes(2, 'little') + total.to_bytes(2, 'little') + bytes([bounded, tape, 0])
    return prefix + b''.join(bytes([op, amount]) + span.to_bytes(2, 'little')
                             + pointer.to_bytes(2, 'little') + bytes([costs[op]])
                             for op, amount, span, pointer in records) + b'\0\0'


def native_oracle(optimized):
    count, total = struct.unpack_from('<HH', optimized)
    proof, needed, high = optimized[4:7]
    words = [0xaa1f03ea, 0xaa0403eb, 0xaa1f03ec, 0xaa1f03ed, 0xaa0603f0, 0xaa1f03ee]
    branch = lambda base, distance: base | ((distance & 0x7ffff) << 5)
    words += [0xf10000bf | (needed << 10), branch(0x54000003, total+3)] if proof else [0xd503201f]*2
    remaining = total
    for i in range(count):
        op, arg, span, ptr, cost = struct.unpack_from('<BBHHB', optimized, 7+7*i)
        load = (0x39400089 | (ptr << 10)) if proof else 0x39400169
        store = (0x39000089 | (ptr << 10)) if proof else 0x39000169
        zero = (0x3900009f | (ptr << 10)) if proof else 0x3900017f
        start = len(words)
        if op in b'+-':
            words += [load, (0x11000129 if op == ord('+') else 0x51000129) | (arg << 10), store]
        elif op in b'><' and not proof:
            words += [(0x9100014a if op == ord('>') else 0xd100014a) | (arg << 10),
                      0xeb05015f, branch(0x54000002, remaining), 0x8b0a008b]
        elif op == ord(','):
            words += [0xeb01019f, 0x540000a2, 0x386c6809, 0x9100058c, store, 0x14000002, zero]
        elif op == ord('.'):
            words += [0xeb0301bf, 0x540000a2, load, 0x382d6849, 0x910005ad, 0x14000002, 0x5280004e]
        elif op in b'[I':
            words += [load, branch(0x34000009, span-1), branch(0xb4000006, remaining+2), 0xd10004c6]
            if op == ord('I'): del words[-2:]
        elif op == ord(']'):words += [load, branch(0x35000009, 1-span)]
        elif op == ord('0'):words += [zero]
        elif op == ord('K'):words += [0x52800009 | (arg << 5), store]
        elif op == ord('F'):words += [(0x3940008f | (ptr << 10)) if proof else 0x3940016f]
        elif op == ord('A'):words += [load, 0x52800011 | (arg << 5), 0x1b1125e9, store]
        assert len(words)-start == cost
        remaining -= cost
    assert remaining == 0
    words += [0x2a0e03e0, 0x14000005, 0x52800020, 0x14000003, 0xd10004c6,
              0x52800060, 0xcb060201, 0xf90000ed, 0xd65f03c0]
    code = struct.pack('<'+'I'*len(words), *words)
    file_size = 128+len(code)
    header = b'\x7fELF\x02\x01\x01'+bytes(9)
    header += struct.pack('<HHIQQQIHHHHHH', 3, 183, 1, 128, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    header += struct.pack('<IIQQQQQQ', 1, 5, 0, 0, 0, file_size, file_size, 16384)
    header += b'BFP1'+bytes([needed, high, proof, 0])
    return header+code


def fuse(optimized):
    count, total = struct.unpack_from('<HH', optimized)
    records = [list(struct.unpack_from('<BBHHB', optimized, 7+7*i)) for i in range(count)]
    if optimized[4]:
        for i, record in enumerate(records):
            if record[0] != ord('['):continue
            j = i+1
            while j < count and records[j][0] in b'+-><N':j += 1
            if j == count or records[j][0] != ord(']'):continue
            coefficients = {}
            for op, amount, _, ptr, _ in records[i+1:j]:
                if op in b'+-':coefficients[ptr] = (coefficients.get(ptr,0)+(amount if op == ord('+') else -amount)) & 255
            source = record[3]
            if coefficients.pop(source, 0) != 255:continue
            record[0], record[4] = ord('F'), 1
            for body in records[i+1:j]:
                coefficient = coefficients.pop(body[3], 0)
                if coefficient:body[0],body[1],body[4] = ord('A'),coefficient,4
                else:body[0],body[4] = ord('N'),0
            records[j][0],records[j][4] = ord('0'),1
    stack = []
    for i, record in enumerate(records):
        if record[0] == ord('['):stack.append(i)
        elif record[0] == ord(']'):
            opening = stack.pop()
            span = sum(r[4] for r in records[opening:i+1])
            records[opening][2] = record[2] = span
    total = sum(r[4] for r in records)
    return optimized[:2]+total.to_bytes(2,'little')+optimized[4:7]+b''.join(
        struct.pack('<BBHHB', *r) for r in records)+b'\0\0'


def emit(optimized):
    encoded = stage('policy_operands', optimized)
    code = stage('policy_codegen', encoded)
    assert len(code) == 5+68+4*int.from_bytes(optimized[2:4], 'little')+1, (len(code), optimized[:7])
    image = stage('policy_elf', code)
    assert image[-1] == 0
    return image[:-1]


def oneshot(optimized):
    count = int.from_bytes(optimized[:2], 'little')
    records = [list(struct.unpack_from('<BBHHB', optimized, 7+7*i)) for i in range(count)]
    stack = []
    pairs = {}
    for i, r in enumerate(records):
        if r[0] == ord('['): stack.append(i)
        elif r[0] == ord(']'): pairs[stack.pop()] = i
    if optimized[4]:
        for i, j in pairs.items():
            pointer = records[i][3]
            zero = False
            for op, _, _, address, _ in records[i+1:j]:
                if op in b'[]IE': zero = False
                elif address == pointer and op in b'+-,A0K': zero = op == ord('0')
            if zero:
                records[i][0], records[i][4] = ord('I'), 2
                records[j][0], records[j][4] = ord('E'), 0
    for i, j in pairs.items():
        records[i][2] = records[j][2] = sum(r[4] for r in records[i:j+1])
    total = sum(r[4] for r in records)
    return optimized[:2]+total.to_bytes(2,'little')+optimized[4:7]+b''.join(
        struct.pack('<BBHHB', *r) for r in records)+b'\0\0'


def main():
    rng = random.Random(20261013)
    sources = [b'', b'+', b'.', b',[>+<-]>.', b'[[]]', b'[+][-]', b'[', b']', b'][',
               b'[' * 256 + b']' * 256, b'.' * 4096, b'.' * 4097,
               b'+' * 255, b'+' * 256, b'+' * 511, b'+' * 512, b'-' * 1024,
               b',[>+[-]<[-]]>.', b',[>+[-]<]', b',[[-]+++]']
    sources += [bytes(rng.choice(b'><+-.,[]') for _ in range(rng.randrange(80))) for _ in range(100)]
    for source in sources:
        tokens = rle(source)
        encoded = b''.join(bytes(token) for token in tokens) + b'\0\0'
        actual = stage('policy_rle', source)
        assert actual == encoded, (source, actual, encoded)
        expected = resolve(tokens)
        actual = stage('policy_resolve', encoded)
        if expected is None:assert actual[-1] != 0, source
        else:
            assert actual == expected, (source, actual, expected)
            optimized = stage('policy_optimize', actual)
            assert optimized == optimize(expected), (source, optimized, optimize(expected))
            fused = stage('policy_affine', optimized)
            assert fused == fuse(optimized), (source, fused, fuse(optimized))
            conditional = stage('policy_oneshot', fused)
            assert conditional == oneshot(fused), (source, conditional, oneshot(fused))
            assert emit(conditional) == native_oracle(conditional), source
            image = emit(optimized)
            assert image == native_oracle(optimized), source
            if source in (b',[>+<-]>.', b'[[]]'):
                assert emit(fused) == native_oracle(fused), source
    for name in ('row', 'scope'):
        source_root = Path(r'D:\Android\AndroidStudioProjects\GM\brainfuck/src')
        if not source_root.exists():
            source_root = ROOT / 'evidence/gm_native_20261014_v4/GM/brainfuck/src'
        source_path = source_root / (name + '.bf')
        raw = source_path.read_bytes()
        source = bytes(c for c in raw if c in b'><+-.,[]')
        expected = resolve(rle(source))
        first = stage('policy_rle', source)
        resolved = stage('policy_resolve', first)
        assert resolved == expected, name
        assert stage('policy_rle', source, 'seed_alt') == first
        assert stage('policy_resolve', first, 'seed_alt') == resolved
        (BUILD / (name + '.resolved')).write_bytes(resolved)
        optimized = stage('policy_optimize', resolved)
        assert optimized == optimize(resolved), name
        assert stage('policy_optimize', resolved, 'seed_alt') == optimized
        (BUILD / (name + '.optimized')).write_bytes(optimized)
        fused = stage('policy_affine', optimized)
        assert fused == fuse(optimized), name
        (BUILD / (name + '.fused')).write_bytes(fused)
        fused_image = emit(fused)
        assert fused_image == native_oracle(fused), name
        (BUILD / (name + '.affine.elf')).write_bytes(fused_image)
        conditional = stage('policy_oneshot', fused)
        assert conditional == oneshot(fused), name
        conditional_image = emit(conditional)
        assert conditional_image == native_oracle(conditional), name
        (BUILD / (name + '.conditional.elf')).write_bytes(conditional_image)
        image = emit(optimized)
        assert image == native_oracle(optimized), name
        (BUILD / (name + '.elf')).write_bytes(image)
        print(f'PASS {name}: {len(source)} BF commands, {len(rle(source))} RLE records', flush=True)
    print(f'PASS {len(sources)} RLE/bracket cases and independent GM seed comparisons')


if __name__ == '__main__':main()

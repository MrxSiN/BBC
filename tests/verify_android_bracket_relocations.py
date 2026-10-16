#!/usr/bin/env python3
"""Test the bounded, independent BF bracket-span resolver.

This does not change the Android code emitter and does not establish Android
execution. All pairing and span computations in the tested program are BF.
"""
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source

SOURCE = ROOT / 'experiments/android_bracket_relocations.bf'
ELF = ROOT / 'build/android_bracket_relocations_x86_64_linux.elf'
ALPHABET = b'><+-.,[]'


def reference(commands):
    if any(c not in ALPHABET for c in commands) or len(commands) > 10:
        return None
    stack = []
    result = bytearray()
    for close_pos, c in enumerate(commands, 1):
        if c == ord('['):
            stack.append(close_pos)
        elif c == ord(']'):
            if not stack:
                return None
            open_pos = stack.pop()
            result.extend((close_pos-open_pos+1, close_pos))
    if stack:
        return None
    result.extend((0, 0))
    return bytes(result)


def native(program):
    p = subprocess.run([str(ELF)], input=program, capture_output=True,
                       timeout=12, check=True)
    assert not p.stderr, p.stderr
    return p.stdout


def seed(exe, program):
    p = subprocess.run([str(exe), str(SOURCE)], input=program,
                       capture_output=True, timeout=20, check=True)
    return p.stdout


def main():
    commands = check_source(SOURCE.read_bytes())
    assert len(commands) == 2252
    assert ELF.read_bytes()[:4] == b'\x7fELF'
    assert ELF.stat().st_size == 215 + 32 * len(commands)
    rng = random.Random(20261012)
    valid = [b'', b'+', b'[-]', b'[+]', b'[[]]', b'[[-]]', b'[][]',
             b'[[[]]]', b'++[->+<]', b'[+][-]', b'[]++[[]]']
    invalid = [b'[', b']', b'][', b'[[]', b'[]]', b'[[[]',
               b'!', b'a', b'+ +', b'++\xff', b'['*11, b'+'*11,
               b'.'*32, b'[]'*6, b'[['+b'+'*9+b']]']
    # Balanced, shuffled nested and sequential programs within ten commands.
    for _ in range(320):
        target = rng.randint(0, 10)
        out = bytearray()
        depth = 0
        while len(out) < target:
            remaining = target - len(out)
            choices = [ord('+'), ord('-'), ord('.'), ord(','), ord('>'), ord('<')]
            if remaining > depth + 1:
                choices.append(ord('['))
            if depth:
                choices.append(ord(']'))
            c = rng.choice(choices)
            if c == ord('['): depth += 1
            if c == ord(']'): depth -= 1
            out.append(c)
        if depth: out[-depth:] = b']'*depth
        if reference(out) is not None:
            valid.append(bytes(out))
        else:
            invalid.append(bytes(out))
    # Exhaustive bracket-only streams up to the ten-command source limit.
    for n in range(0, 11):
        for mask in range(1 << n):
            b = bytes(ord(']') if (mask >> i) & 1 else ord('[') for i in range(n))
            if reference(b) is None: invalid.append(b)
            else: valid.append(b)
    for _ in range(200):
        b = bytes(rng.choice(ALPHABET) for _ in range(rng.randint(1, 14)))
        if reference(b) is None: invalid.append(b)
        else: valid.append(b)
    # The nonzero status makes it safe for a transport adapter to discard
    # malformed output; it is not an ELF relocation protocol until integrated.
    for sample in valid:
        want = reference(sample)
        assert want is not None, sample
        got = native(sample)
        assert got == want, (sample, got, want)
        # Span is enough to determine both branch destinations. Current
        # emitter slots are 48 bytes, so each branch immediate is in 4B words.
        for span, close_pos in zip(got[0:-2:2], got[1:-2:2]):
            opening = close_pos - span + 1
            cbz_words = (12*span)-1  # slot opening offset +4 to slot after close
            cbnz_words = (12*(2-span))-1  # closing offset +4 to after opening
            assert 1 <= opening < close_pos <= 10
            assert 0 < cbz_words < 2**18
            assert -(2**18) <= cbnz_words < 0
            for imm in (cbz_words, cbnz_words):
                encoded = imm & ((1 << 19) - 1)
                signed = encoded if encoded < 2**18 else encoded - 2**19
                assert signed == imm
    for sample in invalid:
        got = native(sample)
        assert len(got) >= 2 and got[-2] == 0 and got[-1] != 0, (sample, got)
    seeds = 0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as tmp:
            for interp in ('seed_interpreter.c', 'seed_interpreter_alt.c'):
                exe = Path(tmp) / interp
                subprocess.run(['cc', '-O2', '-o', str(exe), str(ROOT / 'bootstrap' / interp)],
                               check=True, capture_output=True)
                for sample in (valid[:14]+invalid[:8]):
                    assert seed(exe, sample) == native(sample), (interp, sample)
                    seeds += 1
    out = {
        'classification': 'EXECUTED independent Linux native Brainfuck bracket-span stage; not integrated Android codegen',
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'linux_native_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
        'brainfuck_instructions': len(commands),
        'linux_native_elf_bytes': ELF.stat().st_size,
        'valid_streams_passed': len(valid),
        'invalid_streams_rejected': len(invalid),
        'independent_interpreter_equivalences': seeds,
        'input_protocol': 'prefiltered non-NUL command stream up to 10 commands',
        'output_protocol': 'each matched close emits (span, one-based close index); zero terminator then status byte',
        'semantic_limits': ['Only relocation metadata, not Android machine code',
                            'NUL terminates input', 'Untrusted input must be independently length bounded',
                            'No Android device execution', 'No AArch64 compiler selfhosting'],
    }
    (ROOT/'evidence/android_bracket_relocations.json').write_text(json.dumps(out,indent=2)+'\n')
    print(f'PASS BF bracket resolver: {len(valid)} valid streams, {len(invalid)} invalid rejections, {seeds} independent seed cases')


if __name__ == '__main__':
    main()

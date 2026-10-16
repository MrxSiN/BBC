#!/usr/bin/env python3
"""Streaming, independent byte-contract validation of BF-emitted AArch64 code.

Only *checks* compiler output; never lowers BF or synthesizes native code.
The whitelist is the currently versioned BFP1/iteration-58 emitter's set of
fixed instruction byte sequences. Every loop veneer must resolve exactly to
its matching bracket boundary. A file-backed stack avoids a fixed depth cap.
This is structural validation, NOT arbitrary AArch64 verification or device proof.
"""
from __future__ import annotations

from pathlib import Path
import struct
import tempfile

_PREFIX = bytes.fromhex('ea031faaeb0304aaec031faaed031faaf00306aaee031faa1f2003d51f2003d5')
_SUFFIX = bytes.fromhex('e0030e2a050000142000805203000014c60400d160008052010206cbed0000f9c0035fd6')
_TEMPLATES = {
    'plus': bytes.fromhex('690140392905001169010039'),
    'minus': bytes.fromhex('690140392905005169010039'),
    'right': bytes.fromhex('4a0500915f0105eba300005460008052010206cbed0000f9c0035fd68b000a8b'),
    'left': bytes.fromhex('4a0500d15f0105eba300005460008052010206cbed0000f9c0035fd68b000a8b'),
    'input': bytes.fromhex('9f0101eba200005409686c388c05009169010039020000147f010039'),
    'output': bytes.fromhex('bf0103eba20000546901403949682d38ad050091020000144e008052'),
}
_OPEN_START = bytes.fromhex('69014039e9000035110000106f000058310a0f8b20021fd6')
_OPEN_END = bytes.fromhex('a60000b520008052010206cbed0000f9c0035fd6c60400d1')
_CLOSE_START = bytes.fromhex('69014039e9000034110000106f000058310a0f8b20021fd6')
_STACK_RECORD = struct.Struct('<QQ')  # code-relative opening position and target
_MAX_PEEK = 56


def validate_code(path: str | Path) -> dict:
    """Validate BFP1 emitted code in constant heap space. Raise ValueError on error."""
    path = Path(path)
    length = path.stat().st_size
    if length < 1024 + len(_PREFIX) + len(_SUFFIX):
        raise ValueError('BF native code truncated')
    code_len = length - 1024
    end = code_len - len(_SUFFIX)
    pairs = count = peak = depth = 0
    with path.open('rb') as f, tempfile.TemporaryFile(mode='w+b') as stack:
        f.seek(1024)
        if f.read(len(_PREFIX)) != _PREFIX:
            raise ValueError('BF callable prologue mismatch')
        pos = len(_PREFIX)
        while pos < end:
            f.seek(1024 + pos)
            peek = f.read(min(_MAX_PEEK, end-pos))
            matched = False
            for template in _TEMPLATES.values():
                if peek.startswith(template):
                    pos += len(template)
                    count += 1
                    matched = True
                    break
            if matched:
                continue
            if len(peek) >= 56 and peek.startswith(_OPEN_START) and peek[32:56] == _OPEN_END:
                delta = struct.unpack_from('<q', peek, 24)[0]
                target = pos + 8 + delta * 4
                if not (pos + 56 <= target <= end and target % 4 == 0):
                    raise ValueError('BF opening veneer outside code or reversed')
                stack.seek(depth * _STACK_RECORD.size)
                stack.write(_STACK_RECORD.pack(pos, target))
                depth += 1
                peak = max(peak, depth)
                pos += 56
                count += 1
                continue
            if len(peek) >= 32 and peek.startswith(_CLOSE_START):
                if not depth:
                    raise ValueError('BF closing veneer without opening')
                delta = struct.unpack_from('<q', peek, 24)[0]
                target = pos + 8 + delta * 4
                depth -= 1
                stack.seek(depth * _STACK_RECORD.size)
                record = stack.read(_STACK_RECORD.size)
                if len(record) != _STACK_RECORD.size:
                    raise ValueError('BF bracket stack truncated')
                opening, expected_end = _STACK_RECORD.unpack(record)
                if target != opening or expected_end != pos + 32:
                    raise ValueError('BF callable bracket relocation mismatch')
                pairs += 1
                count += 1
                pos += 32
                continue
            raise ValueError(f'BF emitted unknown or incomplete AArch64 template at code offset {pos}')
        if pos != end or depth:
            raise ValueError('BF callable body length or unmatched opening veneer')
        f.seek(1024 + end)
        if f.read(len(_SUFFIX)) != _SUFFIX:
            raise ValueError('BF callable epilogue mismatch')
        if f.read(1):
            raise ValueError('unexpected trailing bytes in BF native code')
    return {'validation':'PASS_BFP1_OPCODE_TEMPLATES_AND_BRACKET_TARGETS',
            'native_code_bytes':code_len,'native_instruction_records':count,
            'bracket_pairs':pairs, 'maximum_nesting_depth':peak,
            'fixed_nesting_limit':None,'android_executed':False}

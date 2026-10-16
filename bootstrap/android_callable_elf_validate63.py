#!/usr/bin/env python3
"""Bounded-memory structural validation for BF-generated Android callable DSOs.

Validation only: this module neither emits machine code nor repairs ELF headers.
The ELF bytes and their length fields are produced by standard Brainfuck
stages. Read a constant-size prefix so validation scales with artifact size.
"""
from __future__ import annotations

from pathlib import Path
import struct

_PREFIX = 1024
_U64 = 1 << 64
_EXPECTED_SECTIONS = (
    # sh_name, type, flags, address, offset, size (None = code), link, info, align, entsize
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (1, 5, 2, 0xc0, 0xc0, 20, 2, 0, 4, 4),
    (7, 11, 2, 0xe0, 0xe0, 48, 3, 1, 8, 24),
    (15, 3, 2, 0x110, 0x110, 13, 0, 0, 1, 0),
    (23, 6, 2, 0x120, 0x120, 96, 3, 0, 8, 16),
    (32, 1, 6, 0x400, 0x400, None, 0, 0, 4, 0),
    (38, 3, 0, 0, 0x190, 48, 0, 0, 1, 0),
)


def validate_dso(path: str | Path) -> dict:
    """Raise ValueError for an invalid exported BFP1 ELF. Never load entire image."""
    path = Path(path)
    length = path.stat().st_size
    if length < _PREFIX + 68 or length >= _U64 or (length - _PREFIX) % 4:
        raise ValueError('invalid BF callable ELF length or alignment')
    code_size = length - _PREFIX
    with path.open('rb') as stream:
        head = stream.read(_PREFIX)
    if len(head) != _PREFIX:
        raise ValueError('truncated BF DSO header')

    def require(actual, wanted, reason):
        if actual != wanted:
            raise ValueError(f'BF DSO {reason} mismatch: {actual!r}')

    require(head[:16], b'\x7fELF\x02\x01\x01' + b'\0'*9, 'identity')
    require(struct.unpack_from('<HHIQQQIHHHHHH', head, 16),
            (3, 183, 1, 0, 64, 512, 0, 64, 56, 2, 64, 7, 6), 'ELF64 header')
    require(struct.unpack_from('<IIQQQQQQ', head, 64),
            (1, 5, 0, 0, 0, length, length, 16384), 'RX load segment')
    require(struct.unpack_from('<IIQQQQQQ', head, 120),
            (2, 4, 288, 288, 288, 96, 96, 8), 'dynamic segment')
    require(struct.unpack_from('<IIIII', head, 0xc0),
            (1, 2, 1, 0, 0), 'SysV hash symbol chain')
    require(head[0xe0:0xf8], bytes(24), 'null dynamic symbol')
    require(struct.unpack_from('<IBBHQQ', head, 0xf8),
            (1, 0x12, 0, 5, 1024, code_size), 'exported function')
    require(head[0x110:0x11d], b'\0bfc_call_v1\0', 'exported symbol name')
    require([struct.unpack_from('<QQ', head, 0x120+16*i) for i in range(6)],
            [(4, 0xc0), (5, 0x110), (6, 0xe0), (10, 13), (11, 24), (0, 0)],
            'dynamic lookup contract')
    require(head[0x180:0x188], b'BFP1\x01\0\0\0', 'callable ABI marker')
    require(head[0x190:0x1c0],
            b'\0.hash\0.dynsym\0.dynstr\0.dynamic\0.text\0.shstrtab\0',
            'section names')
    for i, expected in enumerate(_EXPECTED_SECTIONS):
        actual = struct.unpack_from('<IIQQQQIIQQ', head, 512 + 64 * i)
        wanted = tuple(code_size if value is None else value for value in expected)
        require(actual, wanted, f'section {i}')
    return {'format': 'ELF64_AARCH64_BFP1_DSO', 'bytes': length,
            'native_code_bytes': code_size, 'export': 'bfc_call_v1',
            'validation': 'PASS_CONSTANT_PREFIX_AND_DECLARED_LENGTH',
            'runtime_loader_verified': False}

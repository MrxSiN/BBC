"""Validate ignored Brainfuck comments without inventing another language.

The canonical source may contain whitespace and explanatory lines beginning
with #. Since # has no meaning to Brainfuck, its prose must not contain
any of the eight executable bytes. This is a lint convention only.
"""

import hashlib

OPS = frozenset(b'><+-.,[]')
WHITESPACE = frozenset(b' \t\r\n')


def check_source(source: bytes) -> bytes:
    """Return the exact eight-command stream or reject unsafe annotations."""
    if not source:
        raise ValueError('empty authoritative compiler source')
    for line_number, line in enumerate(source.splitlines(keepends=True), 1):
        body = line.lstrip(b' \t')
        if body.startswith(b'#'):
            offender = OPS.intersection(body)
            if offender:
                raise ValueError(f'Brainfuck instruction in ignored comment on line {line_number}: '
                                 f'{bytes(sorted(offender))!r}')
            continue
        # An inline # is permitted after real Brainfuck commands, but the rest
        # of the line is ignored *only by convention*. Check every byte.
        if b'#' in line:
            executable, explanation = line.split(b'#', 1)
            if OPS.intersection(explanation):
                raise ValueError(f'Brainfuck instruction in inline comment on line {line_number}')
        else:
            executable = line
        if set(executable) - OPS - WHITESPACE:
            raise ValueError(f'Unexpected noninstruction byte on line {line_number}')
    code = bytes(ch for ch in source if ch in OPS)
    stack = 0
    for ch in code:
        if ch == ord('['):
            stack += 1
        elif ch == ord(']'):
            stack -= 1
            if stack < 0:
                raise ValueError('Unmatched closing bracket in compiler source')
    if stack:
        raise ValueError('Unmatched opening bracket in compiler source')
    return code


def source_digests(source: bytes) -> tuple[str, str]:
    return (hashlib.sha256(source).hexdigest(),
            hashlib.sha256(check_source(source)).hexdigest())

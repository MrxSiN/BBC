# BFX v1 portable contract

BBC emits **BFX — Ballsdeep Brainfuck XAX** modules with extension `.bfx`.
This contract defines the compiler request and response. Native target support
and executed evidence are listed in [STATUS.md](STATUS.md).

All multi-byte integers are unsigned little endian. One invocation compiles
one request. Framing and response bytes are data, never executable Brainfuck.

## Compiler request

`source_length:u16le || source:byte[source_length] || 01`

Length counts every raw source byte, including NUL, ignored text and whitespace.
It must not exceed **65,535**. The sender must reject larger input before
encoding; splitting or wrapping the length is invalid. The final byte must be
hex `01`. A missing or different terminator fails; EOF-as-zero cannot satisfy
that check. Bytes after this frame belong to the caller.

This known-length request accepts binary source. The optional text bootstrap
framer has a separate NUL-termination rule and 7,680-byte capacity; see
[BOOTSTRAP.md](BOOTSTRAP.md).

## Compiler response

Success: `42 46 58 || 01 || 00 || instruction_count:u16le || instructions`

Failure: `42 46 58 || 01 || error:u8`

| Offset | Field | Rule |
|---|---|---|
| 0..2 | Magic | ASCII `BFX`, hex `42 46 58` |
| 3 | Version | Binary `01`, not ASCII `1` |
| 4 | Compiler status | Zero for success; nonzero for failure |
| 5..6 | Instruction count | Present only on success |
| 7 onward | Payload | Exactly the stated number of original instruction bytes |

A successful response is exactly `7 + instruction_count` bytes. A failed
response is exactly five bytes, with no count or payload.

| Compiler status | Meaning |
|---|---|
| 0 | Successful validation and emission |
| 1 | Missing or invalid request terminator, including truncated input |
| 2 | Unmatched brackets |
| 3 | Instruction count or nesting exceeds the supported resource limit |

If several errors occur, framing wins, then size, then unmatched brackets.
The frontend consumes the declared source and checks its terminator before
emitting a response. It emits no partial success record for rejected source.
OS-level writes are not atomic: callers must reject truncated output and must
not publish it as a module.

## Payload and resource limits

The frontend filters exactly `><+-.,[]`, preserves their order and performs
no optimization. All other bytes are ignored, including raw `00` and `FF`.
A hash character is not a comment delimiter; instruction characters in
annotations still participate in compilation.

At most **3,840 instructions** and **255 nested loops** are accepted. Every
bracket must match. These are frontend resource limits, not changes to the
[Brainfuck execution profile](BRAINFUCK_PROFILE.md).

The compiler itself runs on a zeroed 65,536-cell tape. A sentinel precedes its
sixteen-cell instruction slots and working slot. At the instruction limit,
the working slot spans cells 61,456..61,471. See the
[tape notes](../compiler/compiler.bf.notes.md) for exact state and bounds.

## Import acceptance and versioning

The XAX importer independently checks magic, supported version, exact response
length, successful status, instruction/nesting limits, payload opcodes and
bracket balance. It rejects compiler-error records and incomplete or trailing
bytes before emitting a decision store.

BFX v1 carries neither a target selection nor platform capabilities. Every
target must preserve the same tape, byte, input/output and error semantics.
Importer validation errors and native decision-call statuses are separate
interfaces, documented in [XAX_INTEGRATION.md](XAX_INTEGRATION.md).

Changing a filename does not convert record contents. Incompatible records
require a new version byte; compatible metadata additions require an explicit
framing rule. No extension mechanism is currently defined.

## Exact examples

| Source/request | Complete response |
|---|---|
| Empty source: `00 00 01` | `42 46 58 01 00 00 00` |
| Unmatched opening bracket: `01 00 5B 01` | `42 46 58 01 02` |
| Truncated terminator fixture | `42 46 58 01 01` |

The tracked [fixture pairs](../tests/bfx/README.md) are exact binary compiler
requests and expected responses. Compile source to create `.bfx` modules;
the portable record is not a human-written source language.

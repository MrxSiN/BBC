# BFX v1 portable contract

BBC emits **BFX — Ballsdeep Brainfuck XAX** modules with extension `.bfx`.
This contract defines the compiler request and response. Native target support
and executed evidence are listed in [05_STATUS.md](05_STATUS.md).

All multi-byte integers are unsigned little endian. One invocation compiles
one request. Framing and response bytes are data, never executable Brainfuck.

## Compiler request

`source_length:u16le || source:byte[source_length] || 01`

This is **BBC source-request v1**, independently versioned from the BFX output
record. It has no in-band version field; future versions require explicit
out-of-band selection or a separately specified unambiguous frame.

Length counts every raw source byte, including NUL, ignored text and whitespace.
The u16 field can encode 65,535, but the accepted limit is **65,533**:

| Limit | Bytes | Meaning |
|---|---|---|
| `MAX_SOURCE_BYTES` | 65,533 | Maximum accepted raw source |
| `MAX_REQUEST_FRAME_BYTES` | 65,536 | Accepted source plus two length bytes and terminator |
| `NATIVE_INPUT_VIEW_BYTES` | 65,536 | Existing XAX decision input extent |

BBC itself rejects declared source lengths 65,534 and 65,535 with compiler
status 3 after consuming the declared frame and checking the terminator.
A missing or invalid terminator still takes priority and returns status 1.
Those two complete oversized frames cannot be passed through the native
input view: the native core rejects logical input lengths above 65,536 with
native status 3 before executing BBC. A shorter, truncated frame is never
a substitute for a complete oversized request. External senders must reject
source above the accepted limit; splitting or wrapping the length is invalid.
The final byte must be
hex `01`. A missing or different terminator fails; EOF-as-zero cannot satisfy
that check. Bytes after this frame belong to the caller.

The terminator detects truncation at physical EOF, including a last source
byte of NUL. It does not detect arbitrary insertion, deletion or corruption
when later bytes remain: a later byte may accidentally satisfy the terminator.
Hosts requiring integrity must isolate and validate each frame or use an
independently validated transport. Optional host validation owns transport
only; BBC still validates framing, filters source and validates brackets.

This known-length request accepts binary source. The optional text bootstrap
framer has a separate NUL-termination rule and 7,680-byte capacity; see
[04_BOOTSTRAP.md](04_BOOTSTRAP.md).

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
| 3 | Source length, instruction count or nesting exceeds the supported resource limit |

If several errors occur, framing wins, then size, then unmatched brackets.
The frontend consumes the declared source and checks its terminator before
emitting a response. It emits no partial success record for rejected source.
OS-level writes are not atomic: callers must reject truncated output and must
not publish it as a module.
Even a complete success-looking record is invalid if the compiler invocation
failed. The caller must establish successful compiler termination as well as
complete record validation and exact consumption before publishing a module.

## Payload and resource limits

The frontend filters exactly `><+-.,[]` and preserves their order without
source-program rewrites. P0 optimizes compiler bookkeeping only; BFX v1 bytes
for the same request are unchanged. All other bytes are ignored, including raw `00` and `FF`.
A hash character is not a comment delimiter; instruction characters in
annotations still participate in compilation.

The current capacity flag is private compiler bookkeeping. It replaces a
per-byte instruction-count comparison with a carry-event update, without
changing accepted payloads, limits or serialized bytes. See
[the proof](07_OPTIMIZATION_PROOFS.md#p0-carry-triggered-capacity-flag).

At most **3,840 instructions** and **255 nested loops** are accepted. Every
bracket must match. These are frontend resource limits, not changes to the
[Brainfuck execution profile](01_BRAINFUCK_PROFILE.md).

The compiler itself runs on a zeroed 65,536-cell tape. A sentinel precedes its
sixteen-cell instruction slots and working slot. At the instruction limit,
the working slot spans cells 61,456..61,471. See the
[tape notes](../compiler/compiler.bf.notes.md) for exact state and bounds.

## Import acceptance and versioning

The XAX importer independently checks magic, supported version, exact response
length, successful status, instruction/nesting limits, payload opcodes and
bracket balance. It rejects compiler-error records and incomplete or trailing
bytes before emitting a decision store.

Serialized data remains untrusted before publication. BFX v1's bracket check
and loop-edge derivation are defensive import validation, not raw-source
filtering or Brainfuck optimization. Any future safety annotation must be
validated independently or retain runtime checks; producer authentication
alone never authorizes unchecked memory access.

BFX v1 carries neither a target selection nor platform capabilities. Every
target must preserve the same tape, byte, input/output and error semantics.
Importer validation errors and native decision-call statuses are separate
interfaces, documented in [03_XAX_INTEGRATION.md](03_XAX_INTEGRATION.md).

Changing a filename does not convert record contents. Incompatible records
require a new version byte; compatible metadata additions require an explicit
framing rule. [BFX v2](10_BFX_V2_CLEAR.md) is an explicit separate version
with CLEAR and an optional Brainfuck optimization stage; it does not change
these v1 request/response bytes or v1 opcode validation. The authoritative
frontend continues to emit v1.

## Exact examples

| Source/request | Complete response |
|---|---|
| Empty source: `00 00 01` | `42 46 58 01 00 00 00` |
| Unmatched opening bracket: `01 00 5B 01` | `42 46 58 01 02` |
| Truncated terminator fixture | `42 46 58 01 01` |

The tracked [fixture pairs](../tests/bfx/README.md) are exact binary compiler
requests and expected responses. Compile source to create `.bfx` modules;
the portable record is not a human-written source language.

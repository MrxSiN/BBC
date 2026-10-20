# BFX

BFX (Ballsdeep Brainfuck XAX), extension `.bfx`, is BBC's portable handoff to
XAX. This is the single authoritative wire specification. All optimization
levels, supported source sizes and target architectures use this format.
Integers are unsigned little endian. The [execution profile](01_BRAINFUCK_PROFILE.md)
defines the resulting program's behavior.

## Record

Success: `42 46 58 00 || 01 || 00 || count:u32le || payload:byte[count]`.

Failure: `42 46 58 00 || 01 || status:u8`, with nonzero status.

| Offset | Field | Required value |
|---|---|---|
| 0..3 | Magic | `42 46 58 00` (ASCII BFX followed by NUL) |
| 4 | Format identifier | Exactly `01` |
| 5 | Producer status | Zero for success, nonzero for failure |
| 6..9 | Instruction count | Present only on success, u32 little endian |
| 10 onward | Instructions | Exactly count bytes |

A success has exactly `10 + count` bytes; a failure has exactly six bytes.
No padding, extension fields, trailing bytes or alternate count widths are
accepted. Count arithmetic must be checked for overflow before length comparison.
A failure is a valid producer response but never an importable program.
The bounded BF producers use status 1 for missing/invalid terminator, 2 for
unmatched brackets and 3 for resource limits; framing takes priority, then
resource limits, then brackets. A caller must establish native/process success
as well as a complete successful record. Discard incomplete or failed output.
OS writes are not promised to be atomic.

The identifier is binary `01`, not ASCII `1`. No other identifier is accepted
or emitted. This intentional migration changes the magic so old records using
three-byte magic and identifiers 01 through 05 are unambiguously rejected.
There is no probing, legacy fallback or production legacy decoder. Convert
old inputs by recompiling source, never by changing a filename or header.
Historical evidence retains its original bytes and meaning.

## Instructions

| Byte | Meaning |
|---|---|
| ASCII `+ - > < . , [ ]` | The corresponding Brainfuck instruction |
| `00` | CLEAR: write zero to the current cell |
| `01..07` | Add `2^opcode`, modulo 256 |
| `08..0E` | Subtract `2^(opcode - 7)`, modulo 256 |
| `0F..15` | Move right `2^(opcode - 14)` cells |
| `16..1C` | Move left `2^(opcode - 21)` cells |

Every other byte is invalid. CLEAR is an instruction, so zero bytes must not
serve as payload terminators. Counts include all instructions, including brackets
and CLEAR. Brackets must balance. The frontend may preserve ASCII instructions;
optimizers may use any declared opcode. These are representations in one format,
not different decoder modes. A record carries no optimization-level marker,
source-size marker, target selection, unchecked-memory permission or platform API.

Packed movement has the same first-crossing failure as its constituent unit
moves. On failure the cursor remains at the last valid cell. Opposite moves
cannot cancel. A skipped zero-entry loop executes no movement. Arithmetic wraps
modulo 256. CLEAR has the semantics of an exact unit-step clear loop.

## Validation and implementation budgets

The one canonical XAX decoder checks length, magic, identifier, successful status,
count, every opcode and bracket pairing before the importer publishes a graph.
Its scalar validation statuses are separate from producer statuses: 1 framing
or magic, 2 unsupported identifier, 3 producer failure, 4 resource limit,
5 invalid opcode, 6 unmatched brackets. Exact framing is checked even for a
failure response. Imported data remains untrusted until validation succeeds.

The count field can represent u32 values; current native import accepts at
most 65,536 instructions, using a 65,546-byte record view and 65,536 u32 pairing
and stack entries each. Maximum balanced nesting is therefore 32,768.
Larger counts reject before count-plus-header arithmetic or payload access.
This implementation budget does not select another format.

| Producer | Raw-source budget | Instruction budget | Depth budget |
|---|---:|---:|---:|
| Bounded `compiler.bf` | 65,533 | 3,840 | 255 |
| Streaming coordinator with `stream_chunks.bf` | 1,048,576 | 65,536 before packing | 32,768 balanced |

Both emit identical framing. The compiled program still has a 65,536-byte tape.
Fixed compiler workspaces are distinct from dynamic allocation; runtime workspace
growth remains unimplemented. See [scalability](16_SCALABILITY.md).

## Bounded source request and private passes

`source_length:u16le || raw_source:byte[source_length] || 01` is the bounded
frontend's input transport, separate from BFX. Length counts every byte,
including NUL, whitespace and ignored text. Filter exactly `><+-.,[]` in order;
all other source bytes are ignored. A hash is not a comment delimiter.
The accepted raw-source maximum 65,533 leaves room for the length and terminator
in a 65,536-byte native input view. Lengths 65,534 and 65,535 are rejected;
complete oversized frames cannot enter that native view. A missing terminator
fails even at physical EOF. The terminator detects truncation, not arbitrary
corruption when later bytes remain. Isolate frames in the transport.

The bounded optimization passes consume a complete, previously validated,
successful BFX record with at most 3,840 instructions, followed by byte `01`.
They trust the header/count precondition; they are private transformations,
not additional untrusted-record decoders. They preserve the format and emit
six-byte failure status 1 for an invalid terminator. Their count staging uses
u16 internally and emits the upper two u32 count bytes as zero. Validate their
complete result before publication or import. Streaming coordinators have
separate typed buffer APIs; private BBCS/BBCR packets are not BFX records.

## Exact examples

| Input/result | Complete BFX hex |
|---|---|
| Empty program | `42 46 58 00 01 00 00 00 00 00` |
| One ASCII plus | `42 46 58 00 01 00 01 00 00 00 2B` |
| One CLEAR | `42 46 58 00 01 00 01 00 00 00 00` |
| Unmatched bracket response | `42 46 58 00 01 02` |
| Missing terminator response | `42 46 58 00 01 01` |

[Fixture pairs](../tests/bfx/README.md) contain current exact binary records.

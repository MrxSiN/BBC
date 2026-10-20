# BFX v3 arithmetic packing

The optional [`pack_arithmetic.bf`](../compiler/pack_arithmetic.bf) pass is
EXECUTED on Android ARM64 and Windows x86-64. It packs consecutive identical
arithmetic commands into explicitly declared powers of two. The authoritative
frontend still validates raw source and emits transparent v1; the existing
[clear/full-wrap pass](10_BFX_V2_CLEAR.md) emits v2. This pass consumes validated
v2 and emits v3. Source limits and the execution profile remain unchanged.

## Encoding and validation

Success is `42 46 58 || 03 || 00 || operation_count:u16le || operations`, exactly
`7 + count` bytes. Count is at most 3,840, nesting at most 255, and record length
at most 3,847. Every operation occupies one byte. Bracket pairing counts each
encoded arithmetic operation once. Failure is `BFX || 03 || status:u8`.

| Byte | Effect on current byte |
|---|---|
| `00` | CLEAR, as in v2 |
| `01`..`07` | Add `2^opcode`, modulo 256 |
| `08`..`0E` | Subtract `2^(opcode - 7)`, modulo 256 |
| Original eight ASCII bytes | Unchanged |
| Any other byte | Reject |

Each new arithmetic operation accesses the current cell only. It changes
neither pointer nor input/output. The importer rejects truncation, trailing
bytes, unsupported versions, non-success responses, illegal operations,
resource excess and unmatched brackets before publishing a decision store.
V1 stays strict ASCII; v2 still rejects bytes one through fourteen. The
standalone `bfx.xax` validator stays strict v1; the importer's embedded
validator accepts all three declared versions. No implicit extension exists.

## Internal producer contract

The caller supplies a **complete validated v2 success record**, followed by
required byte `01`. Establish magic, version two, success, exact length/count,
legal payload, bracket pairing and resource limits before invoking the pass.
The extended canonical validator or complete importer boundary can establish
these facts; no foreign-language source recognizer may substitute for BBC.
Failed raw-source compilations bypass both optional passes and retain v1 errors.

The helper is not an untrusted-record validator. It discards the five fixed
header bytes, reads the bounded count and operations, then requires its own
terminator. Missing/incorrect terminators emit only `42 46 58 03 01`. Bytes
after the terminator belong to the caller. Maximum complete input is 3,848
bytes. Require native success and a complete validated result; discard every
failed-call output prefix, including one resembling a success header.

Seven bounded scans use group sizes 128, 64, 32, 16, 8, 4 and 2. Each scan
recognizes live consecutive identical `+` or `-` commands, replaces each full
group with one declared operation and marks the other slots deleted. Deleted
slots and all other operations reset run state. Earlier larger encodings
remain untouched. The final live sequence contains descending powers followed
by at most one unit command for each remaining run. The v2 pass already removes
complete 256-command identities; valid v2 from another producer need not have
done so, and still packs correctly. No record grows or previously accepted
source becomes unsupported. Original source validation occurs before packing.

## Equivalence and bounds

For every byte `x`, executing `K` consecutive increments gives `(x + K) mod 256`,
and decrements give `(x - K) mod 256`. No intermediate value is inspected within
such a run, and there is no movement, I/O or failure opportunity to remove.
Surrounding loops and error ordering retain their positions. Even-step loops
remain ordinary loops, including nonterminating nonzero-entry cases. Opposite
movements are never cancelled. Full logical tape reset remains mandatory.

A group proves `K` live, distinct, adjacent same-direction operations. Deleting
`K - 1` cannot underflow the output count. Each later pass ignores deleted
slots, so groups cannot overlap. The phase code decreases seven through zero;
the threshold halves from 128 through two, then one. Every halving input is
even and every backward walk has positive bounded length. Slot markers and
opcodes are independent, so zero-valued CLEAR never terminates scanning.

The [tape notes](../compiler/pack_arithmetic.bf.notes.md) give the layout. The
helper has 3,639 instructions and 5,259 raw bytes, within the unchanged compiler
and text-framer limits. Its SHA-256 is
`c117e100ebb4c91dce1f872517f1070af00aa175711ff74a9fd648b464fb5c35`.
The independent interpreter observes peak cell 61,469 at maximum count.

## Canonical lowering and executed evidence

The [XAX consumer and exact-root transactions](https://github.com/MrxSiN/XAX/blob/0232858c7ad9be0e66b6feb300b4d0880bc276a5/compiler/integration/bfx/POWERS.md)
emit checked load, supported 32-bit rotate of the existing constant one,
truncation to eight bits, wrapping add/subtract and checked store. The exponent
is one through seven; rotating right by `32 - exponent` gives exactly 2..128.
No generated-decision constant-pool entry is added. V1/v2 accepted stores
stay byte-identical. The initial byte-width rotate was explicitly declined
by Windows lowering; a verified canonical graph repair uses the supported
32-bit sequence. Generic compiler implementation files are unchanged.

[Correctness evidence](../evidence/bfx_v3_arithmetic.json) records 432 native
packing properties, 72 independent binary-output C-interpreter cases, every
payload byte in all three versions and 908 Android/Windows record comparisons.
The 42 decision modules have 5,530 vectors per arm/target: 22,120 complete
input/output/tape/guard comparisons. Every byte value, EOF, five alignments,
dirty tape, both bounds, output failure ordering and invalid 32-bit logical
arguments agree with the original eight-command interpreter.

Frontend, clear helper and power helper each pass three identical native
generations on both targets. Each frontend generation passes twelve exact
fixtures. Android-native import stores match Windows exactly. Verification,
reference transactions and native lowering still use unchanged generic Python
bootstrap tools on Windows. Component fixed points establish no whole-toolchain
native compiler host, real-application result or overall competitor victory.

[Matched measurements](13_V3_BENCHMARKS.md) cover complete builds, process
execution, native calls, resident high-water counters and complete artifacts.
They retain all regressions and keep earlier evidence immutable.

# BFX v2 clear operation

This extension adds one declared operation. BFX v1 and source-request v1
retain their exact meanings and remain the transparent baseline. The
optional Brainfuck optimizer consumes validated v1 modules and emits v2;
the importer validates and lowers declared operations, without recognizing
source idioms. The standalone `bfx.xax` validator remains v1-only; the
importer's embedded validator accepts both versions. Implementation and target evidence are tracked separately from this
specification. Immediate arithmetic, transfer and scan operations are not
defined by this version. Removing full arithmetic wraps needs no new opcode.

## Record and operation encoding

All integers are unsigned little endian. Success is
`42 46 58 || 02 || 00 || operation_count:u16le || operations`.
Failure is `42 46 58 || 02 || status:u8`, with no count or payload. Compiler
statuses retain the v1 meanings. The fixed semantic profile is unchanged:
65,536 checked byte cells, wrapping arithmetic, EOF zero and checked output.

Each operation occupies one byte:

| Byte | Meaning |
|---|---|
| `00` | CLEAR: set the current cell to zero; no pointer, input or output change |
| `3E 3C 2B 2D 2E 2C 5B 5D` | The original eight operations, one byte each |
| Any other byte | Invalid operation; reject before publication |

The count is at most 3,840. A success record is exactly `7 + count` bytes,
at most 3,847. Bracket pairing indexes operations, including CLEAR entries.
Nested depth remains at most 255. Reject truncation, trailing bytes, unknown
versions, failed compiler records, unknown operations and unmatched brackets
before publishing executable graph operations. Existing v1 consumers reject
version two; new consumers accept v1 with its original strict opcode rules
and v2 with the extra zero byte. Unknown versions still reject explicitly.
There are no optional flags, implicit extensions or safety annotations.

CLEAR only accesses the current in-bounds tape cell. Previous pointer moves
retain their checks, and output failures retain their original ordering.
No movement is cancelled and no access to another cell is introduced.
Every decision invocation still logically resets the entire tape. Native
failure statuses and the rule to discard failed-call output are unchanged.

## Optimizer boundary and bounded algorithm

`compiler/compiler.bf` owns raw source filtering, validation and v1 emission.
The optional `compiler/optimize.bf` is a separate standard Brainfuck pass.
Its internal input contract requires a complete, successfully produced and
validated **v1 success record**, followed by a required byte `01`. The caller
establishes the v1 record's magic, version, success, exact count/length, legal
instructions, bracket structure and resource limits. The authoritative
frontend invocation must have completed successfully. Failed source
compilations bypass this pass and retain their original error record.
The optimizer is not an independent untrusted-record validator. Existing
canonical v1 validation may establish its precondition; an external host
must not supply source filtering or idiom recognition in its place.

The pass reads exactly five fixed header bytes, count-low, count-high and
the declared operations. It stages them in sixteen-cell slots before
emission. It checks the required final terminator itself; missing/incorrect
terminators produce only a five-byte v2 framing error. Bytes after the
terminator belong to the caller. Its complete maximum input is 3,848 bytes,
well within the native 65,536-byte input view. Private preconditions must be
established before calling; do not treat behavior outside them as acceptance.

A bounded forward pass replaces exact three-operation sequences
`[-]` and `[+]` with CLEAR. It marks the following two slots deleted and
subtracts two from the output count. Stored-slot markers remain intact so
zero-valued CLEAR operations and deleted slots cannot terminate scanning.
Only unmarked slots emit. The entire count and transformation are known
before any success prefix is written. Transport is not atomic: callers must
still require successful completion and exact validated output.

The same pass removes complete groups of 256 consecutive identical `+` or
`-` instructions. A byte counter records the current same-direction run
modulo 256; changing operation resets it. On wrap, mark the current and
preceding 255 slots deleted and subtract 256 from the output count. A bounded
backward walk marks those slots; temporary continuation markers return the
scan to its original position and are cleared. Runs shorter than 256 retain
their original instructions. No opposite pointer movements, I/O, brackets
or different arithmetic operations are merged. Deleted clear-loop operands
cannot form such a group: each is separated by its closing bracket, while
the emitted CLEAR is itself a run boundary.

The output never exceeds the input v1 record: each rewrite shrinks three
bytes to one, and full wrapping groups disappear. No optional expansion can make a previously accepted source
unsupported. The original v1 record remains available independently for
differential testing and fallback. The optimizer adds no source-language
command and does not reinterpret annotations or arbitrary raw source.

## Equivalence obligations

With wrapping 8-bit arithmetic, incrementing or decrementing by one reaches
zero from every starting byte, then leaves the pointer unchanged. These
loops contain no I/O, nested loop or pointer movement. A zero-entry loop
already leaves zero; storing zero has the same public result. CLEAR executes
at exactly the original loop's position, so surrounding I/O and failures
retain order. Optimized outer control flow still uses normal bracket tests.

Adding or subtracting 256 restores every byte's original value. A removed
group has no I/O, pointer change or failure opportunity. Removing an entire
loop body this way leaves an ordinary empty loop; it must not become CLEAR.
Its nontermination for a nonzero controlling cell is preserved. Counts never
underflow: a wrap proves 256 distinct, not-yet-deleted same-direction slots.
The private run state does not change the 65,536-cell execution profile.

Require all 256 entry values, nested/adjacent/skipped cases, EOF, output
capacity, dirty-tape reset and both tape boundaries to agree with an
independent interpreter. `+[++]`, `+[--]`, `+[<>-]`, multi-operation bodies
and I/O loops are negative rewrite cases. Nontermination comparisons use
mathematical invariants and bounded diagnostics, not timing races. Test both
record versions, every payload byte, unknown versions and malformed records.
Test both arithmetic signs, lengths around 255/256/257 and later multiples,
run boundaries, clear-loop adjacency, output/count byte carries and the
3,840-instruction limit. The optimizer itself must fit the unchanged limits.

XAX may lower CLEAR using a checked current-cell load, subtracting that value
from itself, and a checked store. This uses existing graph constants and
operations; it is equivalent to a zero store and retains memory safety.
Generic later graph optimization may simplify it. New XAX implementation
must be canonical semantic graphs, applied through verified expected-root
transactions; unchanged bootstrap verification/lowering is disclosed.

The implementation is EXECUTED on Android ARM64 and Windows x86-64.
[Correctness and raw measurements](../evidence/bfx_v2_optimization.json) and
the [benchmark report](11_V2_BENCHMARKS.md) retain separate component, build
and process boundaries. No overall competitor victory follows from v2 support.

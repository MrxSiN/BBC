# Compiler scalability and current limits

**Current bounded pipeline: EXECUTED. Private chunk frontend: PROTOTYPE,
EXECUTED on Android and Windows. Separate BFX v5 wide-profile native compilation:
EXECUTED. Runtime workspace growth: UNIMPLEMENTED.** This document separates
implementation limits from Brainfuck semantics. No existing source request,
BFX v1-v4 record or program tape changes.

## Where the current limits come from

| Current limit | Reason | Required scalable replacement |
|---|---|---|
| 65,533 raw source bytes | Two request-length bytes and one terminator share a 65,536-byte native input view; the length field is u16 | Streaming source input through bounded chunks and a wider public framing/count contract |
| 3,840 instructions | The frontend retains sixteen cells per instruction on its fixed 65,536-cell workspace; the guard closes at fifteen 256-instruction groups | Stream provisional instructions and grow/spool importer/graph workspace under explicit budgets |
| 255 nested loops | Frontend depth uses one byte, and the importer separately enforces the same bound | Wide depth arithmetic and a growable checked pairing stack in the importer |

The compiler working slot reaches cells 61,456..61,471 at 3,840 instructions.
That number is a conservative implementation choice, not the mathematical
maximum of every possible tape layout. Increasing it alone does not create
a scalable compiler. BFX v1-v4 counts are u16 and their native record view is
3,847 bytes; decoder scratch, optimization staging and graph serialization
also have fixed extents. All affected layers must agree on wider capacities.

The [capacity audit](../evidence/scalability_capacity_audit.json) reproduces a
coverage gap in the original bounded pipeline: pinned Brainfry Mandelbrot has 11,669 raw bytes, 11,451
instructions and nesting nine. The current ordinary BBC frontend returns BFX
resource status 3. The separate [v5 profile](17_BFX_V5_WIDE.md) now compiles
that program end to end. The earlier failure is preserved as a capacity
measurement, not a timing result.

These are compiler-resource limits. The compiled program's defined 65,536-cell
tape is a separate execution contract. A scalable compiler can preserve it.

## Executed first step: bounded-space streaming

[`stream_chunks.bf`](../compiler/stream_chunks.bf) filters source and validates
brackets in chunks without staging the complete instruction stream. It uses
cells 0..58, a u64 depth counter represented in byte cells and a u16 count for
each chunk. State travels explicitly between invocations. The source has
3,671 instructions / 3,794 bytes, so the existing bounded compiler can build it.
The ordinary decision core still resets its full tape before each call.

On both targets the prototype processes Mandelbrot, a 1 MiB binary source,
140,000 instructions with maximum nesting 70,000, and valid/unclosed loops
crossing chunk boundaries. It handles depth carries through 2^32 and overflow
at 2^64 without wraparound acceptance. [Evidence](../evidence/streaming_frontend_prototype.json)
records 588 scalar properties and 44 stream chunks per target, Android guard/
alignment checks, and ten independent-interpreter cases with exact consumption
and peak cell 58. [Static fixtures](../tests/stream_chunks/README.md) retain
small byte-exact cases. These are validation/filtering tests, not compiled
large-program execution or performance scores.

All emitted tokens remain provisional. A trusted caller starts with zero
state, preserves returned state exactly, isolates each packet, accepts only
successful continuation and finishes exactly once. Any native failure,
framing error, resource error or bracket error discards every earlier token
from the compilation. Complete success is published only after final validation.
The [v5 native coordinator](17_BFX_V5_WIDE.md) now implements this transaction
within separately declared fixed budgets. File-backed spooling and runtime
growth remain future work.

## Private BBCS version01 interface

This prototype interface is distinct from BFX and has no supported end-user CLI.
Use chunks of at most 32,768 bytes and initialized, distinct decision buffers.
The private caller establishes the chunk bound, Boolean flags and valid state
provenance; this component is not an untrusted continuation-state validator.

Input: `depth:u64le || bracket_error:u8 || overflow_error:u8 || chunk_length:u16le || final:u8 || source[chunk_length] || 01`.
Depth/error fields form the ten-byte continuation state; initial state is zero.
Final is zero or one. Source is binary; NUL and noncommand bytes are preserved
as consumed source positions and ignored by instruction filtering.

Output: `BBCS || 01 || tokens || 00 || depth:u64le || bracket_error:u8 || overflow_error:u8 || chunk_instruction_count:u16le || status:u8`.
Tokens contain only the eight original ASCII instructions, so the NUL delimiter
is unambiguous. A complete packet has exactly `19 + chunk_instruction_count`
bytes. Returned depth/error fields supply the next continuation state.
Status zero permits continuation or final acceptance; one is framing error,
two bracket error, three depth overflow. Framing wins over size, then brackets.
Unclosed depth is checked only on final input; unmatched closing brackets are
sticky. The caller must check native termination as well as this private status.
These packets must never be saved or imported as `.bfx` modules.

## Remaining work for dynamic compilation

The [v5 implementation](17_BFX_V5_WIDE.md) supplies a u32-count record,
native chunk coordination, streaming identical-run packing, wider decoder
pairing and enlarged import arenas. It accepts 1 MiB of source, 65,536
instructions and balanced nesting up to 32,768, and compiles Mandelbrot on
both targets. Those are fixed verified extents. The steps below describe
runtime growth beyond that specialization, not missing v5 record import.

1. Implement the canonical XAX compiler host's checked source-chunk loop and
   provisional spool/commit path. It must count total bytes/instructions with
   checked wide arithmetic and enforce configurable source, work, memory and
   depth budgets, with clean allocation/I/O exhaustion outcomes.
2. Preserve the v5 wide-count container and strict v1-v4 acceptance and bytes.
   Final counts must be known before publishing success; never expose a
   partial stream as a valid module.
3. Extend the streaming BF optimization beyond identical runs to clear and
   affine patterns, preserving chunk-boundary and failure/termination proofs.
4. Replace fixed importer record/scratch/output assumptions with verified
   growth or paging, and a checked loop-pair stack. Complete graph verification,
   target lowering and packaging must also accept the enlarged stores.
5. Measure full builds, runtime, memory and artifact size on the larger
   compiled corpus. Keep executed Mandelbrot and smaller regressions; add
   held-out sources and counterbalanced competitor trials.

The existing XAX HEAP_VIEW verifier requires a proven constant allocation size
before constructing a checked view. General runtime-sized views therefore need
further XAX work; calling malloc or removing bounds checks is insufficient.
The v5 capacity specialization is implemented; verified paging and runtime
growth remain open. All new XAX implementation remains canonical
semantic graphs/verified transactions; no Python production compiler fallback.

Dynamic scaling means consuming resources as work grows, subject to explicit
budgets and available memory/storage. It does not mean unlimited resources or
silently changing the compiled program's tape behavior.

[Bootstrap parity](../evidence/streaming_frontend_bootstrap.json) records three
byte-identical native rebuilds, own-source tokens on both targets and exact
independent consumption. Ordinary BFX import rejects the private packet.
[Verification/provenance](../evidence/streaming_frontend_verification.json)
pins the unchanged build components, source/fixture checks and external test
transport/compiler identities. These replays use the existing bounded frontend;
they are not self-hosting through a new wide-count importer.
The separate [v5 bootstrap evidence](../evidence/wide_bootstrap.json) records
the later native wide-profile run-packer cycle.

# BBC bootstrap and native rebuilds

All BBC implementation is standard Brainfuck. The bounded authoritative frontend
is [`compiler.bf`](../compiler/compiler.bf); the streaming frontend uses
[`stream_chunks.bf`](../compiler/stream_chunks.bf) plus canonical XAX coordination.
Every path uses the one [BFX specification](02_BFX_CONTRACT.md).

1. Run the exact BF frontend under an independent interpreter implementing the
   [execution profile](01_BRAINFUCK_PROFILE.md), using a framed own-source request.
2. Require complete successful BFX and exact filtered own-source payload bytes.
3. Run the emitted payload under the independent interpreter and require identical
   own-source output. This is seed agreement, separate from native execution.
4. Import through the canonical XAX importer, fully verify the emitted store and
   lower/package with unchanged generic XAX SDK utilities.
5. Execute the native frontend on the target, require the exact seed record, and
   repeat native import/verification/lowering. Compare record, store and native
   artifact bytes within each target across generations.

Optional bounded passes run as separate programs: clear optimization, arithmetic
packing and movement packing. Each consumes a previously validated successful
BFX record of at most 3,840 instructions plus byte `01`; each emits BFX again.
Do not pass a compiler failure to a transform. Validate each complete result.
Streaming packing handles larger instruction streams and opaque encoded opcodes.
Its private packet core is bootstrapped through native BF filtering/packing and
native XAX import, then specialized by exact-root canonical graph transactions.

## Text framer

[`frame_source.bf`](../bootstrap/frame_source.bf) reads NUL-terminated text or
physical EOF, at most 7,680 bytes, and emits `length:u16le || text || 01`.
Embedded NUL ends this optional transport. Oversized input is consumed and emits
nothing. Binary source uses the explicit known-length source request. The framer
uses eight-cell slots; last working cell is 61,455. The bounded compiler uses
sixteen-cell slots, with last working cell 61,471. Annotations must contain none
of the eight instruction characters; no preprocessing removes them.

## Authority and evidence

Windows-hosted generic SDK tools perform verification/lowering/packaging;
ctypes and NDK transports allocate buffers, copy bytes and call native exports.
They provide no production BF parser, BFX decoder or native backend. Android
component execution is distinct from Android compiler-host execution. Generic
Windows native-helper fallback remains disclosed.

The current migration evidence is linked in [status](05_STATUS.md). Earlier
[capacity-flag cycles](../evidence/frontend_capacity_gate.json),
[wide bootstrap](../evidence/wide_bootstrap.json) and semantic optimizer reports
remain byte-identical historical snapshots, with their original source and wire
identities. They must not be cited as execution of the migrated sources.
Standalone packaging uses the existing canonical hosts in XAX; its historical
build and resource reports retain their pinned compiler configurations.

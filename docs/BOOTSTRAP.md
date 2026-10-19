# BBC bootstrap and native rebuilds

Authoritative source is [compiler/compiler.bf](../compiler/compiler.bf).
[bootstrap/frame_source.bf](../bootstrap/frame_source.bf) prepares text input.
Both algorithms are ordinary Brainfuck. BFX is serialized data; filesystem,
process and platform operations belong to the external host or XAX.

## Seed procedure

1. Execute the framer under an independent interpreter with the exact compiler
   source bytes as input. Capture its complete output as a compiler request.
2. Execute the compiler with that request. Require a successful, complete
   [BFX v1 response](BFX_CONTRACT.md).
3. Execute the response's instruction payload under the same interpreter,
   supplying the same request. Require byte-identical BFX output.
4. Import the BFX through canonical XAX, verify the resulting store and lower
   it to a native frontend component. Continue with the native cycle below.

The independent interpreter must implement the
[65,536-cell profile](BRAINFUCK_PROFILE.md). It is external development tooling,
not a production frontend, optimizer or native backend. An external interpreter
step limit is a test safeguard, not a Brainfuck language guarantee.

The seed passed 21 fixture/bootstrap/boundary checks, including interpreted
own-source agreement. Its own-source BFX is 2,462 bytes, containing the
compiler's 2,455-instruction stream. Exact results and hashes are in
[frontend and decoder evidence](../evidence/bfx_migration.json).

## Text framer contract

The framer reads until NUL or physical EOF and emits:

`text_length:u16le || original_text_bytes || 01`

It accepts at most **7,680 text bytes**, including annotations and whitespace.
Oversized input is consumed to termination and emits no output. Empty text
emits `00 00 01`. Embedded NUL ends this text transport; arbitrary binary
source must use the known-length compiler request directly. The frontend's
65,535-byte raw-source limit is separate from the framer's capacity.

Eight-cell slots follow a zero sentinel. The last working slot spans cells
61,448..61,455. Rejected input does not advance that slot. The compiler uses
sixteen-cell slots; its last working cell is 61,471.

| Source | Bytes | Instructions | Raw SHA-256 |
|---|---|---|---|
| Framer | 1,207 | 302 | `1b1f7d90c17414417c8622303244d424ccf6e30704ee6165c77f3161e0bd454f` |
| Frontend | 4,531 | 2,455 | `45a5ae43b6cebfe854453827e321c11be2b7ab50db4d78f6a2360b241ed2014b` |

The [frontend tape notes](../compiler/compiler.bf.notes.md) describe its layout
and filtered instruction hash. Source annotations must contain none of the
eight instruction characters; no preprocessing hides annotations from execution.

## Native frontend cycle

For each target and each generation:

1. Run the native canonical XAX importer on the current frontend BFX.
2. Verify the emitted store and lower it using the Windows XAX build host.
3. Load the resulting native library on the target and call the frontend
   with the exact authoritative compiler-source request.
4. Require output identical to the seed BFX. Feed that output into the next
   generation and compare BFX, canonical-store and native-library hashes.

Three generations passed separately on Android ARM64 and Windows x86-64.
Android also passed all eight exact frontend fixtures in every generation.
BFX/store/ELF bytes match between Android generations; BFX/store/DLL bytes
match between Windows generations. ELF and DLL files are different target
artifacts and are not compared to each other.

The native decision ABI's call status and the frontend's BFX compilation status
are distinct. A frontend can execute successfully and emit a five-byte BFX
error record for rejected source. Verification checks the complete record,
not merely the native call's success result.

This establishes BBC frontend self-compilation through XAX. Native lowering
and canonical verification remain Windows-hosted bootstrap operations; the
XAX compiler host does not run on Android in this cycle. External ctypes and
NDK C transports only provide buffers, move bytes and call native exports.
They implement no Brainfuck parser, interpreter or BFX translation.

[Current cycle evidence](../evidence/bfx_android_importer.json) records source,
transaction, artifact and external-tool hashes. See
[XAX integration](XAX_INTEGRATION.md) for the pinned source and call contracts.
No Linux execution or runtime speed advantage is established by these cycles.

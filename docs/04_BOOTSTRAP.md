# BBC bootstrap and native rebuilds

Authoritative source is [compiler/compiler.bf](../compiler/compiler.bf).
[bootstrap/frame_source.bf](../bootstrap/frame_source.bf) prepares text input.
Both algorithms are ordinary Brainfuck. BFX is serialized data; filesystem,
process and platform operations belong to the external host or XAX.

## Seed procedure

1. Execute the framer under an independent interpreter with the exact compiler
   source bytes as input. Capture its complete output as a compiler request.
2. Execute the compiler with that request. Require a successful, complete
   [BFX v1 response](02_BFX_CONTRACT.md).
3. Execute the response's instruction payload under the same interpreter,
   supplying the same request. Require byte-identical BFX output.
4. Import the BFX through canonical XAX, verify the resulting store and lower
   it to a native frontend component. Continue with the native cycle below.

The independent interpreter must implement the
[65,536-cell profile](01_BRAINFUCK_PROFILE.md). It is external development tooling,
not a production frontend, optimizer or native backend. An external interpreter
step limit is a test safeguard, not a Brainfuck language guarantee.

The original seed passed 21 fixture/bootstrap/boundary checks, including
interpreted own-source agreement; its 2,455-instruction identity is recorded in
[frontend and decoder evidence](../evidence/bfx_migration.json).
The current source emits 2,117 BFX bytes containing 2,110 instructions.
[Windows filter evidence](../evidence/frontend_filter_windows.json) records
its independent seed and Windows rebuild checks;
[Android filter evidence](../evidence/frontend_filter_android.json) records
three native generations, twelve fixtures per generation and boundary checks.

## Text framer contract

The framer reads until NUL or physical EOF and emits:

`text_length:u16le || original_text_bytes || 01`

It accepts at most **7,680 text bytes**, including annotations and whitespace.
Oversized input is consumed to termination and emits no output. Empty text
emits `00 00 01`. Embedded NUL ends this text transport; arbitrary binary
source must use the known-length compiler request directly. The frontend's
65,533-byte raw-source limit is separate from the framer's capacity.

Eight-cell slots follow a zero sentinel. The last working slot spans cells
61,448..61,455. Rejected input does not advance that slot. The compiler uses
sixteen-cell slots; its last working cell is 61,471.

| Source | Bytes | Instructions | Raw SHA-256 |
|---|---|---|---|
| Framer | 1,207 | 302 | `1b1f7d90c17414417c8622303244d424ccf6e30704ee6165c77f3161e0bd454f` |
| Frontend | 4,355 | 2,110 | `6829614ef2d7778e8e1513ecdb94726ce00ad2989f12618987a569386a7dce88` |

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

The current frontend with the eight-byte-reset importer passes three
generations on each required target, with twelve exact fixtures, own source
and seven boundary checks per generation: twenty checks on each target.
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

[Current reset-cycle evidence](../evidence/wide_tape_reset.json) records the
new importer and all twenty checks per generation. The earlier
[Windows](../evidence/frontend_filter_windows.json) and
[Android](../evidence/frontend_filter_android.json) cycle evidence record
their source, artifact and external-tool hashes. The
[importer evidence](../evidence/bfx_android_importer.json) retains its canonical
transaction and importer hashes. See
[XAX integration](03_XAX_INTEGRATION.md) for the pinned source and call contracts.
The separate [Windows native driver prototype](03_XAX_INTEGRATION.md#windows-native-driver-prototype)
now verifies tested BBC/XAX stores and builds a PE fixture. It was not used for
these recorded cycles; native BBC DLL packaging remains incomplete.
These cycles establish correctness and fixed points. Separate
[frontend measurements](07_OPTIMIZATION_PROOFS.md) do not establish Linux
execution, application speed or competitive superiority.

## Standalone Android packaging

The [canonical process host](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/standalone_arm64.xax) calls an imported
decision directly. Apply [the hello example binding](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/standalone_hello.edit)
through the expected-root transaction interface, then verify and lower the
result with the existing static AArch64 executable package. The
[reproduction guide](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/STANDALONE.md#reproduce-the-hello-binding) uses
unchanged generic bootstrap APIs; no BBC parser, optimizer or native backend
is implemented in an external language.

[New evidence](../evidence/standalone_android.json) reproduces the empty and
hello executables byte for byte in a second bootstrap build. This is a
deterministic packaging check, separate from the three-generation frontend
cycle and from any XAX compiler self-build. The resulting static syscall ELF
executes on Android ARM64; it needs no desktop Linux host. Binary output
checks use device files/pull or native pipes, avoiding observed ADB display
newline translation.

## Standalone Windows packaging

The [canonical Windows host](https://github.com/MrxSiN/XAX/blob/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78/compiler/integration/bfx/standalone_windows.xax)
uses kernel32 I/O, owned buffers and the same checked decision contract.
Apply its [hello binding](https://github.com/MrxSiN/XAX/blob/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78/compiler/integration/bfx/standalone_windows_hello.edit)
through the expected-root transaction interface and verify the complete store.
The [build guide](https://github.com/MrxSiN/XAX/blob/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78/compiler/integration/bfx/WINDOWS_STANDALONE.md#build-configuration)
uses unchanged generic graph-splicing and PE lowering APIs. An explicit
inlined lowering view is required for larger programs because the default
Win64 call path declines the decision's five machine arguments and returned
borrowed views. This is a bootstrap configuration, not a new native compiler
driver or BBC backend.

[Windows evidence](../evidence/standalone_windows.json) records 23 native
programs and 28 host checks. The native driver replays the public binding,
verifies it and rejects its stale root. Empty and hello PE files rebuild
byte for byte. Their process interface accepts binary input up to 65,536 bytes
and discards decision-error output; no separate decision DLL or test host is
required. BBC's existing three-generation frontend cycle remains separate.

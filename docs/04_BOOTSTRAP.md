# BBC bootstrap and native rebuilds

Authoritative source is [compiler/compiler.bf](../compiler/compiler.bf).
[bootstrap/frame_source.bf](../bootstrap/frame_source.bf) prepares text input.
Both algorithms are ordinary Brainfuck. BFX is serialized data; filesystem,
process and platform operations belong to the external host or XAX.

The separate [v5 wide bootstrap](17_BFX_V5_WIDE.md) compiles the
10,907-instruction streaming run packer, which exceeds the original frontend's
budget. Native BF filtering and packing plus native XAX import produce its
canonical decision store. Generic expected-root view/interface edits bind the
private packet core; unchanged generic SDK utilities verify and lower it.
[Its replay evidence](../evidence/wide_bootstrap.json) keeps this component
cycle separate from native XAX compiler-host self-compilation.

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
The current source emits 2,199 BFX bytes containing 2,192 instructions.
[Capacity-gate evidence](../evidence/frontend_capacity_gate.json) records
42 independent checks, 785 Windows byte/property checks and three identical
Windows native generations. The device became available later in the follow-up;
Android then passed three native generations, twelve exact fixtures each,
twelve boundary checks and all 393 importer cases with Windows store parity.
[Windows filter evidence](../evidence/frontend_filter_windows.json) records
the preceding source's independent seed and Windows rebuild checks;
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
| Frontend | 4,537 | 2,192 | `d8170d895449cf00e971a052b6d5415d2c5f86585d982f826fa70c5127850d6e` |

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

The preceding 2,110-instruction frontend with the eight-byte-reset importer passes three
generations on each required target, with twelve exact fixtures, own source
and seven boundary checks per generation: twenty checks on each target.
BFX/store/ELF bytes match between Android generations; BFX/store/DLL bytes
match between Windows generations. ELF and DLL files are different target
artifacts and are not compared to each other.

The current capacity-flag frontend separately passes three identical Windows
BFX/store/DLL and Android BFX/store/ELF generations, twelve exact fixtures per
generation on both targets and twelve Android boundary checks. Android stores
match their Windows counterparts. Its new evidence does not relabel the
preceding Android source identity.

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

## Optional optimized rebuilds

Compile [`optimize.bf`](../compiler/optimize.bf) through the transparent v1
route first. Validate each successful v1 module with the unchanged canonical
v1 decoder, append byte `01`, and run the native Brainfuck optimizer. Validate
the resulting v2 module with the extended importer before full canonical
verification and generic native lowering. Source failures bypass optimization.
The [contract](10_BFX_V2_CLEAR.md) specifies the private preconditions; external
drivers supply buffers and files, not production recognition or translation.

[New evidence](../evidence/bfx_v2_optimization.json) records three identical
native generations for both the optimizer and the frontend on Android ARM64
and Windows x86-64. The frontend source and its v1 output stay identical;
its optimized v2 module, imported store and target native artifact also
reproduce. Each frontend generation passes twelve exact fixtures. The helper
source has 2,931 instructions; optimizing its own v1 stream leaves 2,851
operations. These are component fixed points, not a complete compiler-host
self-build. Windows-hosted unchanged generic XAX tools still verify and lower.

## Arithmetic-packed rebuilds

For arithmetic-packed builds, continue the optional route with
[`pack_arithmetic.bf`](../compiler/pack_arithmetic.bf). Validate the complete v2
success, append byte `01`, run the native helper, then validate/import v3 and
perform full canonical verification before native lowering. The
[v3 contract](12_BFX_V3_ARITHMETIC.md) specifies that internal boundary.
[Separate correctness evidence](../evidence/bfx_v3_arithmetic.json) records
three identical frontend, clear-helper and arithmetic-helper generations on
each target, twelve exact frontend fixtures each and native Android imports
matching Windows stores. The unchanged frontend source still emits v1.
These component fixed points use the disclosed Windows bootstrap host.

## Movement-packed rebuilds

Continue the optional route with [`pack_moves.bf`](../compiler/pack_moves.bf).
Validate complete v3 success, append byte `01`, execute the native BF helper,
then validate/import v4 and verify the complete canonical store before lowering.
The [v4 contract](14_BFX_V4_MOVEMENT.md) keeps failure ordering and all source
limits. [Correctness evidence](../evidence/bfx_v4_movement.json) records three
identical generations of all four components on each target, twelve frontend
fixtures per generation and exact Android/Windows stores. Frontend source and
its transparent v1 bytes remain unchanged. The four components are separate
bounded programs, never concatenated; native compiler-host gates remain separate.

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

The [compile-local cache configuration](18_BACKEND_BUILD_CACHE.md) reuses
successful verification facts through existing XAX APIs. Start each build
with an empty cache, verify the imported store, retain that cache on the
reader for the exact binding-result bytes, then verify the bound store before
lowering. No proof sidecar, producer assertion or first-check bypass is used.
This configuration retains the existing native BF sources and generic
bootstrap compiler; it does not complete the native Windows driver.

The [native-driver follow-up](19_NATIVE_DRIVER_FOLLOWUP.md) preserves an exact
independent rebuild of the original driver and separately verifies the
canonical diagnostic correction. Its corrected build uses existing same-process
SDK function fragments after full verification. That diagnostic bootstrap is
separate from cold-build measurements and native compiler self-compilation.

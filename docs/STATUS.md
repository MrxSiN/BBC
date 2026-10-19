# BFX status

2026-10-19. **BFX — Ballsdeep Brainfuck XAX** is the portable format emitted
by BBC's Brainfuck frontend. BFX v1 uses magic `42 46 58`, binary version `01`
and the framing, limits and execution profile defined in the contract.

| Work | Current status | Evidence |
|---|---|---|
| Brainfuck frontend and fixtures | EXECUTED | Eight exact fixtures; framing, instruction/nesting limits, maximum raw source and interpreted own-source agreement |
| XAX-native BFX decoding | EXECUTED | Canonical `compiler/integration/bfx/bfx.xax` in XAX; 393 native Windows cases and the same 393 on Pixel 8 Pro ARM64 |
| BFX-to-decision-graph emission | EXECUTED | Canonical XAX importer emits and hashes complete stores; 393 record checks on Android and Windows, plus 89 native Windows decision calls passed |
| BFX Android application | EXECUTED | Canonical XAX app/ABI source; eight Activity cases passed on Pixel 8 Pro |
| BFX native frontend rebuild cycle through a graph-only importer | EXECUTED | Three generations on each of Android and Windows have identical BFX/store/native artifacts; lowering uses Windows bootstrap tools |
| BBC optimization | UNIMPLEMENTED | Transparent instruction stream; no speed advantage claimed |
| Linux execution | UNIMPLEMENTED | No Linux execution performed in this iteration |

Current results, exact hashes and dependency disclosures are recorded in
[Frontend and decoder evidence](../evidence/bfx_migration.json). The frontend remains
ordinary Brainfuck. All newly added executable XAX implementation is a
canonical semantic graph. The build host uses generic XAX bootstrap utilities.

`compiler/integration/bfx/import_bfx.xax` executes on Android and Windows.
It uses a small mixing-result interface and checked hash scratch outputs;
the four-buffer import ABI is unchanged. Android imported 393 record cases
and three real frontend outputs with byte-identical stores and intact input/
buffer guards. Three Android frontend generations passed eight exact fixtures
each, with identical BFX, stores and ELF libraries. The Windows cycle and
89 emitted decision calls also pass.

Native lowering and canonical verification run on the Windows build host.
A general ARM64 large-composite return-copy defect remains tracked in XAX
OI-49; the importer uses a verified interface that avoids that operation.

Android UI/JNI/lifecycle behavior is now canonical source in
`compiler/integration/bfx/android_bfx.xax`. The XAX package ships canonical
BFX stores, data and documentation.
`backend_tests.xax` passes 36 arithmetic cases and a fresh-process 128 KiB
stack probe. Eight Activity cases pass after a generic rebuild from the saved
source.

[Application and regression evidence](../evidence/bfx_retirement.json) records
source hashes, device results and build dependencies.
[Importer evidence](../evidence/bfx_android_importer.json) records the current
canonical source, transaction, native imports and frontend cycles. Generic Python backend, verifier, APK and signing
tools remain bootstrap dependencies.

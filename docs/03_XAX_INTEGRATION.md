# BBC integration with XAX

The single [BFX specification](02_BFX_CONTRACT.md) governs every producer and
consumer. Canonical XAX source at `d320babab5bb9fe61a9d29f1f14942a847bf83a7` contains one decoder,
shared by `bfx.xax` and `import_bfx.xax`. The latter emits, hashes, sorts and
serializes a complete decision store only after validation. Old decoder and
wide-format entrypoints are retired; there is no format fallback.

[Canonical integration sources](https://github.com/MrxSiN/XAX/tree/d320babab5bb9fe61a9d29f1f14942a847bf83a7/compiler/integration/bfx)
are authoritative semantic graphs, with expected-root verified transactions and
workspace saves. `bfx.xax` is now the decoder FUNCTION dependency closure rather
than the retired target-specific build/package request. Select that function
and package it with the existing generic SDK. The importer and source/packing
coordinators are MODULE/PROGRAM stores with explicit entry functions.

| Component | Typed borrowed views in machine argument order |
|---|---|
| Public compile_bfx | Source/work 1,114,112; record 65,546; output/work 1,114,112; tape/work 1,114,112 |
| Decoder | Record read-only 65,546; scratch writable 524,288; logical length u32 |
| Importer | Record read-only 65,546; scratch writable 524,288; arena writable 536,870,912; hash scratch writable 2,048 |
| Source coordinator | Source/work 1,114,112; record 65,546; output work 1,114,112; tape work 1,114,112 |
| Packing coordinator | Record 65,546; input work 1,114,112; output work 1,114,112; tape work 1,114,112 |

Views must be distinct, initialized, live and satisfy the canonical ownership
contract. Raw native pointers cannot establish those proofs. Importer logical
record length is written to the first scratch u32 before calling. The public [compile_bfx interface](21_UNIFIED_COMPILATION.md) supplies a u32
frame and optimization level. The following is private source-coordinator ABI:
source bytes begin at source/work offset 65,536; write raw-source length to
record offset zero. Public callers use compile_bfx, not this private ABI.
Source length above 1 MiB rejects before tape reset.

Decoder returns `(count << 32) | validation_status`; importer returns
`(store_bytes << 32) | status`; source/packer return `(record_bytes << 32) | status`.
On any failure discard provisional buffers. Decoder status meanings are specified
once in the wire contract. Decision-call status and buffer semantics remain in
the [execution profile](01_BRAINFUCK_PROFILE.md).

The earlier format migration changed no generic SDK files. Its initial builds used the SDK snapshot
at `3dcb358e48b0f9a45b8cb72767c1aa600e55cd78`; unrelated upstream additions from
`943884a` are retained and all eight migration-snapshot component images rebuilt identically.
The unified phase adds compile.xax/compile_windows.xax and updates the private
source coordinator; its own evidence records the new identities.
Builds use Windows-hosted Python
verification, lowering and packaging. Source-coordinator Windows lowering uses
existing generic inlining APIs for its private BF callee. Native component calls
run with `XAX_REQUIRE_NATIVE=1` and record authority. Generic verification still
uses the Windows helper-loader fallback; this is not a native XAX compiler host.

The standalone Android/Windows hosts and bounded Android demo embed decisions,
not BFX decoders. Their earlier packaging/application evidence remains historical;
new format migration tests do not establish new application, performance or native
compiler-host claims. See [status](05_STATUS.md) and [bootstrap](04_BOOTSTRAP.md).

The native compile_windows.xax process host exposes emit-bfx/check/info through
the unified interface and exact shared decoder. These commands require no Python
at runtime. Full native bbc compile, library packaging and common-helper loader
migration remain open. See the [public guide](21_UNIFIED_COMPILATION.md).

# BBC integration with XAX

The single [BFX specification](02_BFX_CONTRACT.md) governs every producer and
consumer. Canonical XAX source at `42de0fc3ce31d4447f697e35a565cb4fdc489eda` contains one decoder,
shared by `bfx.xax` and `import_bfx.xax`. The latter emits, hashes, sorts and
serializes a complete decision store only after validation. Old decoder and
wide-format entrypoints are retired; there is no format fallback.

[Canonical integration sources](https://github.com/MrxSiN/XAX/tree/42de0fc3ce31d4447f697e35a565cb4fdc489eda/compiler/integration/bfx)
are authoritative semantic graphs, with expected-root verified transactions and
workspace saves. `bfx.xax` is now the decoder FUNCTION dependency closure rather
than the retired target-specific build/package request. Select that function
and package it with the existing generic SDK. The importer and source/packing
coordinators are MODULE/PROGRAM stores with explicit entry functions.

| Component | Typed borrowed views in machine argument order |
|---|---|
| Decoder | Record read-only 65,546; scratch writable 524,288; logical length u32 |
| Importer | Record read-only 65,546; scratch writable 524,288; arena writable 536,870,912; hash scratch writable 2,048 |
| Source coordinator | Source/work 1,114,112; record 65,546; output work 1,114,112; tape work 1,114,112 |
| Packing coordinator | Record 65,546; input work 1,114,112; output work 1,114,112; tape work 1,114,112 |

Views must be distinct, initialized, live and satisfy the canonical ownership
contract. Raw native pointers cannot establish those proofs. Importer logical
record length is written to the first scratch u32 before calling. Source bytes
begin at source/work offset 65,536; write the raw-source length to record offset
zero before calling. Source length above 1 MiB rejects before tape reset.

Decoder returns `(count << 32) | validation_status`; importer returns
`(store_bytes << 32) | status`; source/packer return `(record_bytes << 32) | status`.
On any failure discard provisional buffers. Decoder status meanings are specified
once in the wire contract. Decision-call status and buffer semantics remain in
the [execution profile](01_BRAINFUCK_PROFILE.md).

The migration changes no generic SDK files. Initial builds used the SDK snapshot
at `3dcb358e48b0f9a45b8cb72767c1aa600e55cd78`; unrelated upstream additions from
`943884a` are retained and all eight component images rebuild identically.
Builds use Windows-hosted Python
verification, lowering and packaging. Source-coordinator Windows lowering uses
existing generic inlining APIs for its private BF callee. Native component calls
run with `XAX_REQUIRE_NATIVE=1` and record authority. Generic verification still
uses the Windows helper-loader fallback; this is not a native XAX compiler host.

The standalone Android/Windows hosts and bounded Android demo embed decisions,
not BFX decoders. Their earlier packaging/application evidence remains historical;
new format migration tests do not establish new application, performance or native
compiler-host claims. See [status](05_STATUS.md) and [bootstrap](04_BOOTSTRAP.md).

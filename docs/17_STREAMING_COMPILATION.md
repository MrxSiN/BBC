# Streaming compilation

The single public [compile_bfx interface](21_UNIFIED_COMPILATION.md) invokes
the canonical XAX source coordinator, which runs [`stream_chunks.bf`](../compiler/stream_chunks.bf)
through private BBCS packets. O1 packing runs
[`stream_runs.bf`](../compiler/stream_runs.bf) through BBCR packets. A single
canonical decoder/importer accepts their output and the bounded frontend's
output. Every route uses [BFX](02_BFX_CONTRACT.md), with no alternate format,
source-size tag or decoder fallback.

The source budget is 1 MiB, chunk size 32,768 bytes and pre-pack instruction
budget 65,536. Depth uses wide private continuation state; a balanced program
within this instruction budget nests at most 32,768 loops. Tokens remain
provisional until complete source validation succeeds. On any coordinator
failure discard the entire buffer; its scalar status is not a BFX failure record.
The source coordinator publishes the BFX header only after validation.

The packing coordinator requires a validated successful BFX record. It checks
the single magic/identifier, successful status and supported count; it is not
a substitute for the canonical exact-length/opcode/bracket validator. It preserves
all valid opcodes, including CLEAR and already packed instructions, while packing
identical ASCII arithmetic and monotone movement runs. Final pending state must
be empty. In-place copying never overtakes consumed input.

The canonical XAX sources are `compiler/integration/bfx/source.xax`, `pack.xax`,
`import_bfx.xax` and the shared decoder closure `bfx.xax` in the separate XAX
repository. [Integration](03_XAX_INTEGRATION.md) specifies the typed buffers.
These are fixed views and budgets; runtime arena growth remains unimplemented.
Windows-hosted unchanged generic XAX bootstrap tools verify and lower the graphs.
Native component execution on Android does not mean the compiler host runs there.

The earlier [wide bootstrap](../evidence/wide_bootstrap.json),
[wide full checks](../evidence/wide_final_audit.json) and
[Mandelbrot report](../evidence/wide_profile.json) retain their old-format
identities. Current migration results are recorded separately in the status index.

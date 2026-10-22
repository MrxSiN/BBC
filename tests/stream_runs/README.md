# 🧪 stream_runs fixtures

> Exact packets for the streaming run packer.

[cases.json](cases.json) holds exact binary input/output pairs for
[`stream_runs.bf`](../../compiler/stream_runs.bf). They are data, not test code. Run each one
under the [BBC profile](../../docs/01_BRAINFUCK_PROFILE.md) or through the compiled pass, and
compare every output byte plus clean termination. Each input ends with the `01` terminator.

The private **BBCR** packets are never BFX ([format notes](../../compiler/stream_runs.bf.notes.md)).
Full-module publication belongs to the [streaming coordinator](../../docs/17_STREAMING_COMPILATION.md).

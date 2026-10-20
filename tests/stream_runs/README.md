# Private run-packer fixtures

`cases.json` contains exact binary input/output pairs for
[`stream_runs.bf`](../../compiler/stream_runs.bf). They are data, not executable
test logic. Execute them under the [BBC profile](../../docs/01_BRAINFUCK_PROFILE.md)
or the compiled pass and compare complete output bytes and successful native
termination. Input is isolated and includes the final byte-one terminator.

The [pass notes](../../compiler/stream_runs.bf.notes.md) define trusted tokens,
two-byte continuation state, finalization and provisional output. Never import
these private `BBCR` packets as BFX modules. The separate
[wide profile](../../docs/17_BFX_V5_WIDE.md) owns full-module publication.

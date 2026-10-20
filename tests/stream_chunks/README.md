# Private streaming frontend fixtures

[cases.json](cases.json) contains exact input/output bytes for
[stream_chunks.bf](../../compiler/stream_chunks.bf). The internal BBCS version01
format is described in [scalability](../../docs/16_SCALABILITY.md). These are
provisional token packets, not publishable BFX modules. They cover continuation,
final validation, byte carries/borrows, depth overflow, binary source and framing.

[Execution evidence](../../evidence/streaming_frontend_prototype.json) retains
588 Windows scalar properties, 44 stream chunks on both targets, 632 Android
calls with five alignments/guards and ten independent-interpreter checks.
The ordinary frontend, BFX v1-v4 limits and native importer stay unchanged.

# Private streaming frontend fixtures

[cases.json](cases.json) contains exact input/output bytes for
[stream_chunks.bf](../../compiler/stream_chunks.bf). The internal BBCS version01
format is described in [the pass notes](../../compiler/stream_chunks.bf.notes.md). These are
provisional token packets, not publishable BFX modules. They cover continuation,
final validation, byte carries/borrows, depth overflow, binary source and framing.

[Execution evidence](../../evidence/streaming_frontend_prototype.json) retains
588 Windows scalar properties, 44 stream chunks on both targets, 632 Android
calls with five alignments/guards and ten independent-interpreter checks.
The private packet format remains unchanged. The canonical streaming coordinator
publishes the same BFX format as the bounded frontend. These older execution
counts describe the pinned prototype source; current integration evidence is
separate in [status](../../docs/05_STATUS.md).

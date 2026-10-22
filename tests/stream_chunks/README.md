# 🧪 stream_chunks fixtures

> Exact packets for the chunked source filter.

[cases.json](cases.json) holds exact input/output bytes for
[stream_chunks.bf](../../compiler/stream_chunks.bf). Its private **BBCS** packets are
provisional tokens, never publishable BFX ([format notes](../../compiler/stream_chunks.bf.notes.md)).

They cover chunk continuation, final validation, byte carries and borrows, depth
overflow, binary source and framing.

📎 [streaming_frontend_prototype.json](../../evidence/streaming_frontend_prototype.json): 588 Windows
properties, 44 chunks on both targets, 632 Android calls across five alignments, and
10 independent checks, for the pinned prototype source. Current results are in [status](../../docs/05_STATUS.md).

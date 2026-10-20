# Private chunk frontend tape notes

[stream_chunks.bf](stream_chunks.bf) is a **PROTOTYPE** private source-filter/
bracket-validation stage. It emits version01 BBCS provisional token packets;
see [the interface and remaining pipeline work](../docs/16_SCALABILITY.md).
The authoritative public frontend remains [compiler.bf](compiler.bf).

The u64 depth occupies cells 0, 4, 8, 12, 16, 20, 24 and 28, low byte first.
Each adjacent three-cell group holds destructive-copy scratch, carry/nonzero
state and restoration. Carries/borrows propagate through fixed positions;
nonzero tests move a bounded sum of nonzero-byte flags through these groups.
All internal copy scratch returns to zero before reuse.

Chunk length occupies 32/36; its adjacent scratch includes loop gate 38.
Per-chunk instruction count occupies 40/44. Cell 48 is raw input/output scratch;
49 recognized-command flag; 50/51 opening/closing flags; 52 final-input flag;
53 sticky bracket error; 54 sticky depth-overflow error; 55 status; 56/57 opcode
comparison/restoration scratch; 58 unmatched-close temporary flag.

The counted source loop copies each raw byte once, compares the eight command
values, emits recognized tokens and updates count/depth. Opening increments
with full-width carry. Closing first tests complete depth, then borrows or marks
an unmatched close. Final input marks unclosed depth; framing priority is retained.
Overflow is sticky. No input-controlled pointer walk or instruction staging grows.
All loop bodies return to their controlling cell and the maximum cell is 58.

The source is 3,794 bytes / 3,671 instructions. Raw SHA-256 is
`7a243960bcbde41b4b84f45e78075971b5ee29b60e9ca44e267ffbf3b554649b`.
[Native/independent evidence](../evidence/streaming_frontend_prototype.json)
and [static fixtures](../tests/stream_chunks/README.md) cover both targets,
wide carries/borrows, framing, provisional output and cross-chunk brackets.
This filter does not expand BFX v1-v4. The separate
[v5 coordinator](../docs/17_BFX_V5_WIDE.md) now consumes its private packets
and supplies bounded wide-count module production and native compilation.

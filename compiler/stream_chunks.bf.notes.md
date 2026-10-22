# 🌊 stream_chunks.bf — public source filter

> Filters and bracket-checks one 32 KiB chunk at a time, carrying a 64-bit depth between chunks.

| | |
|---|---|
| Role | The public compiler's filter/bracket stage. Emits private **BBCS** v01 token packets, not BFX |
| Size | 3,794 bytes, 3,671 instructions |
| Raw SHA-256 | `7a243960bcbde41b4b84f45e78075971b5ee29b60e9ca44e267ffbf3b554649b` |
| Driven by | [`compile_bfx`](../docs/21_UNIFIED_COMPILATION.md) via the [streaming coordinator](../docs/17_STREAMING_COMPILATION.md) |

---

## 🗺️ Tape layout

| Cells | Meaning |
|---|---|
| 0, 4, 8, … 28 | u64 bracket depth, low byte first; each byte has a 3-cell scratch group next to it |
| 32 / 36 | Chunk length (38 is the loop gate) |
| 40 / 44 | Instructions in this chunk |
| 48 | Raw byte in/out |
| 49 | Recognized-command flag |
| 50 / 51 | Open / close flags |
| 52 | Final-chunk flag |
| 53 | Sticky bracket error |
| 54 | Sticky depth-overflow error |
| 55 | Status |
| 56 / 57 | Opcode compare / restore scratch |
| 58 | Unmatched-close temp |

The highest cell used is 58. Nothing grows with input size.

---

## 🔁 Per byte

1. Copy the raw byte once and compare it against the eight commands.
2. Emit recognized tokens and bump the count.
3. Open: increment depth with full-width carry.
4. Close: test the whole depth, then borrow, or mark an unmatched close.
5. On the final chunk, leftover depth marks unclosed brackets.

Framing priority is kept, overflow is sticky, and every loop returns to its
controlling cell.

📎 [streaming_frontend_prototype.json](../evidence/streaming_frontend_prototype.json) ·
fixtures: [tests/stream_chunks](../tests/stream_chunks/README.md)

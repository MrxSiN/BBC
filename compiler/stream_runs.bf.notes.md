# 🌊 stream_runs.bf — streaming run packer

> O1 packing for big programs: packs runs across 32 KiB chunks, carrying two bytes of state.

| | |
|---|---|
| Size | 11,124 bytes, 10,976 instructions (bootstrapped through the wide profile) |
| Raw SHA-256 | `aae50166e21d0647806cf7edac3ce5d5ea8fbd84cdf0a37ad785ed026016dcb3` |
| Filtered SHA-256 | `4c6697cecb6c5b6a3e1dcdb7baee6409a7ebf58f37877c2f57c9f49a43c6a1ef` |
| Coordinator | [streaming compilation](../docs/17_STREAMING_COMPILATION.md) |

It trusts its input: validated BFX instruction chunks. It does not check brackets
or untrusted records. XAX owns framing and publication.

---

## 📨 Packets

**In:** `pending_opcode:u8 | pending_count:u8 | chunk_count:u16 | final:u8 | instructions | 01`

- At most 32,768 instructions per chunk.
- Initial state is `00 00`. `final` is Boolean.
- The pending opcode is none, `+`, `-`, `<` or `>`. "None" means count 0.
  Arithmetic counts are 0–255; movement counts stay below 128.
- Only state returned by a successful earlier call is valid.

**Out:** `BBCR | 01 | packed | pending_opcode:u8 | pending_count:u8 | output_count:u16 | status:u8`

- Exactly `10 + output_count` bytes. Status 1 means a bad or missing terminator.
- Everything stays provisional until this pass *and* full source validation succeed.

---

## 🧮 Packing rules

- **Arithmetic.** Count identical ops mod 256. At a run end, emit bit 0 as the ASCII
  op and bits 1–7 as power opcodes. The sum is exact mod 256, so full 256 groups vanish.
- **Movement.** Emit a 128-step move every time the count hits 128; decompose the
  rest at the run end. Every group is one-directional, so the importer still
  catches the first step off the tape.
- **Flushing.** Loops, I/O and already-encoded opcodes (including CLEAR) flush the
  pending run and pass through in order.
- **Never.** Opposite moves never cancel. Clear-loop folding is not done here.
- **Invariant.** The pending count is the arithmetic run length mod 256, or the
  movement leftover. Chunk boundaries can't change it. The final flush leaves zero
  state. Output never exceeds consumed input, and XAX checks this before its
  in-place copy.

---

## 🗺️ Tape

| Cells | Meaning |
|---|---|
| 0, 1 | Pending opcode and count |
| 4–11 | Remaining chunk length (4 cells per byte) |
| 12, 13 | Final flag, current input byte |
| 16–23 | Output count (4 cells per byte) |
| 24, 25 | Equality scratch and restore |
| 26–30 | Predicate, parity, quotient, toggle, encoded opcode |
| 31–36 | Recognition and branch scratch |
| 37 | Framing status |

Cells 2–3, 14–15 and 38+ stay zero. Division splits the count into quotient and
parity, keeps the quotient as the next count and emits one power per parity bit.
Each flush ends with count and opcode at zero.

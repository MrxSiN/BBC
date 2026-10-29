# 🪗 fold.bf — offset and loop folding pass

> O1 in one pass: folds every straight segment into offset instructions and every
> simple counted loop into a guarded multiply form.

| | |
|---|---|
| Role | The public compiler's O1 pass, run by [`compile_bfx`](../docs/21_UNIFIED_COMPILATION.md) on the whole validated body in one call |
| Size | 8,469 bytes, 4,093 instructions |
| Raw SHA-256 | `80aabb5643974cf90ce75a3040d403e1d58707a560a62e9aa746e6e6584f052d` |
| Filtered SHA-256 | `25ca95335e32d6e028ee9f316826b295603d3de84907c98e5fd0212b9f2baab8` |
| Output | A [BFX `02`](../docs/02_BFX_CONTRACT.md) body; XAX adds the header and `FF` |
| Fixtures | [tests/bfx/fold-cases.json](../tests/bfx/fold-cases.json) |

**Input:** validated primitive instructions (only the eight commands), then a zero
byte or end of input. It trusts its input; run it only after `stream_chunks.bf`
accepted the source.

---

## 🗺️ Tape

A window of 256 slots mirrors the program tape around the start of the current
segment (slot 128 is offset 0), plus a guard slot on each side. Each slot has 16 cells:

| Cell | Meaning |
|---|---|
| 0 A | 1 for window slots, 0 for guards |
| 1 V | Visited in this segment |
| 2 D | Net change of that cell, mod 256 |
| 3 I | The slot's offset as a signed byte |
| 4 E | 1 on the edge slots 0 and 255 |
| 5 CK | A turning point was left here |
| 6 NC | 1 on every window slot except the cursor |
| 7–10 | RUN, pending `[`, last move left, last move right (travel with the cursor) |
| 11–15 | Move/bracket flag, kind, three temps |

Moving the program pointer moves the cursor one slot, so `<`, `>`, `+` and `-` cost a
few steps each and nothing is copied. The highest cell used is 4,127.

---

## 🔁 What it emits

A **segment** is a run of `+ - < >` between loops and input/output. At its end the
pass walks the visited slots left to right:

- a nonzero net change → `01 d k` (ADD);
- an unchanged turning point → `03 d` (CHECK);
- a nonzero final offset → `04 n` (MOVE).

`[`, `]`, `.` and `,` end a segment and pass through. Reaching an edge slot ends the
segment early, so every offset fits a signed byte.

A loop whose body is one segment, returns to offset 0 and changes the counter by
exactly +1 or −1 becomes `[ MUL/CHECK … 00 ]`: each other cell gets `02 d k` with
`k` = its change (counter −1) or minus its change (counter +1), then CLEAR. A body
that only touches the counter becomes a bare `00`. Anything else (`[--]`, `[>]`,
nested loops, I/O, a moving counter) stays a real loop.

---

## 🛡️ Why it is exact

- **Arithmetic.** Each cell's changes in a segment commute; their sum mod 256 is
  its net change. The pointer is never read inside a segment.
- **Bounds.** A segment path first leaves the tape, if at all, at an extreme. Every
  extreme is a turning point or the end, and each is checked by an ADD, CHECK or MOVE
  at that offset; every check lies on the original path. A segment has no I/O, so
  failing at a check instead of at the first crossing returns the same status and
  output, and tape contents after a failure are not observable.
- **Loops.** With counter `x ≠ 0` and step ∓1 the body runs exactly `x` (or `256 − x`)
  times and leaves the counter 0, adding `x·Δ` (or `−x·Δ`) to every other cell. The
  guard `[ … ]` keeps the checks conditional on entering. Steps of ±2 or more are
  never folded: they may not terminate.

## 🧪 Checks

- 19 exact fixtures, each matching an independent interpreter on 3 tape sizes and 2 inputs.
- 3,300 random programs (up to 400 instructions, tapes of 8 to 4,096 cells, long moves
  near both edges): all 2,921 that terminate within the step budget match the reference.
- All 17 benchmark programs match their expected output after folding.

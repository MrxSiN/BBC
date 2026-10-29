# 🧮 Optimization proofs

> Every speedup here is proven first and measured second. Nothing ships on vibes.

Two kinds of changes:

- **P0** makes the *compiler itself* faster. The BFX it emits is unchanged.
- **P1** makes *your program* smaller and faster. It changes BFX, under proof.

All measurements below are pinned snapshots from before the format migration.
Their old version names identify evidence, not current formats. Raw data and
confidence intervals live in the linked evidence files.

---

## ⚡ P0: counted source-byte groups

**Problem.** The frontend copied the source-length bytes on *every* input byte.
That was 76% of the work on long runs of ignored NULs.

**Fix.** Count bytes in groups of 256 and test the high counter only at group edges.

**Why it's safe.** The remaining-byte count drops by exactly one per byte, never
wraps, and scratch cells return to zero. Framing, limits and output are untouched.
131,072 exhaustive fragment states were checked.

**Effect.** Interpreter work fell from 137M to 111M instructions (own source)
and from 1.20G to 564M (max ignored NUL). Native frontend calls got 1.17× faster
on Android and 1.29× on Windows (geometric mean of 9 cases).


---

## 🔤 P0: single-copy opcode decoding

**Problem.** Decoding copied each raw byte eight times. That was 88% of the work
on ignored `FF` bytes.

**Fix.** Copy once, then walk a chain of subtractions (43, 44, 45, 46, 60, 62,
91, 93). A zero means exactly one opcode matched.

**Why it's safe.** The eight targets are distinct mod 256 and every path unwinds
once, restoring the byte and clearing scratch. 512 exhaustive states were checked
against the full tape. Worst case is 4,381 instructions per byte.

**Effect.** Own-source work fell from 111M to 65M instructions, and `FF` input
from 160M to 38M. Native calls got 2.23× faster on Android and 1.95× on Windows.
The compiler library shrank from 66,504 to 50,120 bytes (Android) and from
692,736 to 549,888 bytes (Windows).


---

## 🚩 P0: carry-triggered capacity flag

**Problem.** Every raw byte re-compared the instruction count against the limit.

**Fix.** Only when the count carries into a new 256-group does the frontend
check the limit, and it sets a full flag in an unused marker cell. Each byte
then just tests that flag.

**Why it's safe.** The flag is exactly "count == 3,840". Rejected commands never
advance it, and the flag is cleared before output. 7,682 exhaustive states were checked.

**Effect.** 1.169× faster on Android and 1.086× on Windows, over 10 frozen
requests. The Windows nested case is about 4% slower. It costs 82 instructions
and 20,992 bytes in the Windows DLL. An earlier gated variant regressed and was
rejected; its samples are kept.


---

## 🪗 P1: offset and loop folding

**Fix.** [`fold.bf`](../compiler/fold.bf) turns each segment of `+ - < >` into one
ADD per touched cell, CHECKs for unaccessed turning points and one MOVE, and each loop
whose single-segment body returns to its counter and steps it by ±1 into
`[ MUL… CLEAR ]` ([contract](10_FOLD_OPTIMIZATION.md), [BFX `02`](02_BFX_CONTRACT.md)).

**Why it's safe.**
- *Arithmetic.* Changes to one cell inside a segment commute; their sum mod 256 is
  the net change, and nothing in a segment reads the pointer or I/O.
- *Bounds.* A path first leaves the tape at an extreme, and every extreme is a turning
  point or the end. Each gets an ADD, MUL, CHECK or MOVE at that offset, and every
  checked offset lies on the original path, so the folded segment fails exactly when the
  original does. With no I/O in the segment, failing at a check instead of at the first
  crossing gives the same status and output; the tape after a failure is not observable.
- *Loops.* Counter `x ≠ 0`, step −1: the body runs `x` times, adding `x·Δ` to each other
  cell; step +1: `256 − x` times, adding `−x·Δ`. Both leave the counter 0. The guard keeps
  every check conditional on entering the loop. Steps of ±2 or more and anything with a
  nested loop, I/O or a moving counter are left alone: they may not terminate or may not
  be affine.

**Checks.** 19 exact fixtures checked against an independent interpreter on three tape
sizes; 3,300 random programs (2,921 terminating within budget all match, including long
moves past both window edges and tapes of 8 cells); all 17 benchmark programs, run
natively through the new XAX importer.

📎 [fold.bf notes](../compiler/fold.bf.notes.md)

---

## 🗄️ Retired: clear pass, arithmetic and movement powers

Until 2026-10-29, O1 ran `stream_runs.bf` (power-of-two arithmetic and move opcodes
`01`–`1C`) and the bounded `optimize.bf` clear pass (at most 3,840 instructions).
Their proofs and measurements remain in git history and the evidence reports that name
them. BFX `02` has no power opcodes; `fold.bf` subsumes both passes.

---

## 🧼 XAX: eight-byte tape reset

**Fix.** The importer clears the 65,536-byte tape with 8,192 checked eight-byte
stores instead of single bytes.

**Why it's safe.** Iteration k clears bytes 8k…8k+7. Every byte is cleared exactly
once, and length checks still run first.

**Effect.** A call saves 0.544 ms on Windows (6.168 → 5.624) and 0.058 ms on
Android (1.360 → 1.302).


---

## 🎛️ O0 / O1

- **O0** emits primitives.
- **O1** runs `fold.bf` on the whole validated body in one call. If it fails or its body
  does not fit the record, the O0 record is returned instead.

Bracket errors stick across chunks while counting continues, so "too big" wins
over "unmatched". Offset and multiply loops are folded; scan loops are not yet.

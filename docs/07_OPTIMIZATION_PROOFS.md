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

## 🧹 P1: clear loops and full wraps

**Fix.** `[-]` and `[+]` become CLEAR. A run of 256 identical `+` or `-` disappears.

**Why it's safe.** A unit step reaches zero within 255 iterations with no other
effects. 256 identical steps are the identity on a byte. Only complete,
consecutive, same-direction groups are removed; nothing involving movement is dropped.
Even-step loops like `[--]` are **not** touched, because they can loop forever.

**Checks.** 359 native and 71 independent cases. 6,048 full-buffer decision calls
across all 256 entry bytes, five alignments, EOF and failure order.

📎 contract: [clear optimization](10_CLEAR_OPTIMIZATION.md)

---

## ➕ P1: arithmetic powers

**Fix.** A run of K identical `+` or `-` (K = 2…128, a power of two) becomes one
opcode. Seven passes run from largest to smallest.

**Why it's safe.** Modular arithmetic. Groups never overlap, and every non-arithmetic
instruction keeps its order.

**Checks.** 432 native properties, 72 independent cases and all 14 powers over
every entry byte. 22,120 full-buffer calls.

**Effect.** Native calls 1.43× faster on Android and 1.24× on Windows vs v2.
Builds 1.09× / 1.14× faster.

📎 implemented by [stream_runs.bf](../compiler/stream_runs.bf) · [streaming compilation](17_STREAMING_COMPILATION.md)

---

## ➡️ P1: movement powers

**Fix.** A run of identical moves (2…128) becomes one packed move.

**Why it's safe.** A one-way run stays on the tape exactly when its endpoint does.
On failure the original status and last valid cell are kept. Opposite moves are
never merged: `<>` and `+[<>-]` stay as negative tests.

**Checks.** 432 native properties, 72 independent cases, 1,164 cross-target
records and 9,592 full-buffer calls.

**Effect.** Smaller files and builds about 1.02× faster. No clear runtime win;
the Android native-call aggregate was 0.93×.

📎 implemented by [stream_runs.bf](../compiler/stream_runs.bf) · [streaming compilation](17_STREAMING_COMPILATION.md)

---

## 🧼 XAX: eight-byte tape reset

**Fix.** The importer clears the 65,536-byte tape with 8,192 checked eight-byte
stores instead of single bytes.

**Why it's safe.** Iteration k clears bytes 8k…8k+7. Every byte is cleared exactly
once, and length checks still run first.

**Effect.** A call saves 0.544 ms on Windows (6.168 → 5.624) and 0.058 ms on
Android (1.360 → 1.302).


---

## 🌊 Streaming identical runs

The streaming run packer carries one opcode and a count across chunk boundaries,
so a run split between chunks is never lost. Loops and I/O flush first. Movement
keeps its first-crossing failure. Opposite moves and even-step loops are left
alone. See the [stream_runs notes](../compiler/stream_runs.bf.notes.md).

---

## 🎛️ O0 / O1

The [public entry](21_UNIFIED_COMPILATION.md) adds no new rewrite.

- **O0** emits primitives.
- **O1** packs arithmetic and movement runs, then runs the clear pass if the
  result has 3,840 instructions or fewer.

Bracket errors stick across chunks while counting continues, so "too big" wins
over "unmatched". No affine, scan or offset optimization is claimed.

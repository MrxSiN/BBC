# ➕ pack_arithmetic.bf — arithmetic packer

> Squashes runs of identical `+`/`-` into power-of-two opcodes, largest first.

| | |
|---|---|
| Size | 5,258 bytes, 3,653 instructions |
| Raw SHA-256 | `7d8a403d8a5c79caa9d1b3c7fc499cd8dd8545198d9037d6486d4cf67e15b95d` |
| Filtered SHA-256 | `4f2dc8d352f91e8904e6904d64532b7cb7b573e25a33a901fd20f3dc68a86138` |
| Contract | [arithmetic packing](../docs/12_ARITHMETIC_PACKING.md) |

---

## 🗺️ Tape (16-cell slots)

| Offset | Meaning |
|---|---|
| 0 | Persistent marker |
| 1 | Opcode |
| 5 | Phase code (counts down) |
| 7, 8 | Output count |
| 9 | Current run length |
| 10 | Previous unit opcode |
| 11 | Group threshold |
| 12 | Deleted flag |
| 13 | Backward-walk continuation |
| 14 | Gate, or the new encoded opcode |
| 15 | Walk counter |
| 2–4, 6 | Copies, compares and count borrowing |

The end slot keeps the framing status separately.

---

## 🔁 How it runs

1. Stage the counted input and check the terminator.
2. Phase 7, threshold 128: scan forward, skip deleted slots, reset on other
   instructions, and count identical unit arithmetic.
3. On a full group: carry the encoded opcode back, delete the group, keep its
   first slot and subtract `K − 1` from the count (with explicit borrow).
   Continuation markers restore the scan.
4. Next phase: halve the threshold and rewind. Seven phases total (128 → 2).
5. Carry the final count to the end, then emit live opcodes only.

The count never grows, walks stay inside the staged region, and the peak cell
is 61,469. Bootstrapped as its own bounded program; sources are never concatenated.

📎 [bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json) (pre-migration)

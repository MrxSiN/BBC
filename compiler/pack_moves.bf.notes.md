# ➡️ pack_moves.bf — movement packer

> Squashes runs of identical `>`/`<` into power-of-two moves, without hiding a fall off the tape.

| | |
|---|---|
| Size | 5,342 bytes, 3,732 instructions |
| Raw SHA-256 | `254910fea21d82ddf31c3ce89569b691ca68f468ba26695561cf6a0f23a792c9` |
| Filtered SHA-256 | `608e867e4e3b9c7d326dd1b9250705e382e5a960d257b04b86a9a5a514da2b0b` |
| Contract | [movement packing](../docs/14_MOVEMENT_PACKING.md) |

---

## 🗺️ Tape (16-cell slots)

| Offset | Meaning |
|---|---|
| 0 | Persistent marker |
| 1 | Opcode |
| 5 | Phase (counts down) |
| 7, 8 | Output count |
| 9 | Run length |
| 10 | Previous raw move |
| 11 | Threshold |
| 12 | Deleted flag |
| 13 | Backward-walk continuation |
| 14 | Gate, or the new encoded opcode |
| 15 | Walk count |
| 2–4, 6 | Copies, compares and count borrowing |

---

## 🔁 How it runs

1. Stage the input and check the terminator.
2. Seven scans with thresholds 128, 64, 32, 16, 8, 4 and 2.
3. Only live, identical raw moves join a run. Deleted slots, arithmetic encodings
   and other commands end it.
4. A full group is deleted, its first slot keeps the packed move, and the count
   drops by `K − 1`.
5. Emit live opcodes only, including zero-valued CLEAR.

Already-packed groups are never merged, and opposite moves are never cancelled.
Peak cell 61,469; output never grows.

📎 [bfx_v4_movement.json](../evidence/bfx_v4_movement.json) (pre-migration)

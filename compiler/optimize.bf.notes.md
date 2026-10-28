# 🧹 optimize.bf — clear-loop pass

> Turns `[-]` / `[+]` into CLEAR and deletes full 256-step arithmetic wraps.

| | |
|---|---|
| Size | 4,395 bytes, 2,946 instructions |
| Raw SHA-256 | `971fc93a10bc2ce9840f7bc675c57b6a994bd5c45757a24191a93c72852b1259` |
| Filtered SHA-256 | `33255827d324a2fa9b797366e7f6fa8561fef3ea7088a2ea11ea37f96e613174` |
| Contract | [clear-loop pass](../docs/10_CLEAR_OPTIMIZATION.md) |

**Input:** a complete, validated BFX success record, then byte `01`. Run it only
after the frontend succeeds; failed compiles skip it. It trusts the header.

---

## 🗺️ Tape

16-cell slots, after a sentinel. Within each slot:

| Offset | Meaning |
|---|---|
| 0 | Marker (separate from the opcode, so CLEAR = `00` never stops a scan) |
| 1 | Opcode |
| 7, 8 | Output count |
| 9, 10 | Arithmetic run state |
| 12 | Deleted flag |
| 13 | Temp continuation/gate |
| others | Local compare/copy scratch and input counting |

State moves slot to slot; there's no second array.

---

## 🔁 Phases

1. Drop the 6 fixed header bytes, keep the count and stage that many opcodes in marked slots.
2. Require the terminator and carry the output count to the first slot. Bytes after
   the terminator are not read.
3. Scan forward. An exact `[-]` or `[+]` becomes CLEAR in its opening slot; the
   other two slots are deleted and the count drops by 2.
4. Count identical arithmetic mod 256. On a wrap, delete that group (walk back over
   its 255 predecessors) and subtract 256 from the count.
5. Emit version, status and the final count, then rewind and emit only live
   opcodes, keeping zero-valued CLEAR.

Fits the 3,840-instruction limit; peak cell 61,469. Output never grows.

---

## 🛡️ Safety

- Never folds `[++]`, `[--]`, moves, I/O or nested bodies.
- A full-wrap body removed from a loop leaves an empty loop, which still loops
  forever on nonzero entry.
- Opposite moves are never cancelled.
- Validate the whole returned record before importing. A native output-capacity
  failure can leave a success-looking prefix: discard it.

📎 [canonical_bfx.json](../evidence/canonical_bfx.json)

# 🧠 compiler.bf — bounded seed frontend

> Reads one framed request, keeps the eight instructions, checks brackets and size,
> and writes BFX. No optimization, no backend.

| | |
|---|---|
| Role | Private bounded seed/reference. The public entry uses [`stream_chunks.bf`](stream_chunks.bf) |
| Size | 4,545 bytes, 2,200 instructions |
| Raw SHA-256 | `89e87c42d870e879c4dbbf2ec578da2823351566d3e7d25801f29b5804446b2a` |
| Filtered SHA-256 | `a9323e9daa898c76693df7b66647f58ddb16dd67d91db72ee76b710250b6c358` |
| Specs | [BFX](../docs/02_BFX_CONTRACT.md) · [profile](../docs/01_BRAINFUCK_PROFILE.md) |

Older counts and hashes quoted elsewhere are historical snapshots.

---

## 🗺️ Tape layout

Cells 0–15 stay zero (left sentinel). Work starts at cell 16. With `n` stored
instructions, the working slot starts at `16 × (n + 1)`.

| Slot offset | Meaning |
|---|---|
| 0 | Stored marker. In the working slot: the Boolean "full" flag. Sentinel stays 0 |
| 1 | Raw source byte; becomes the stored opcode |
| 2, 3 | Compare and restore scratch |
| 4 | Recognized-command flag (setup briefly parks the nonempty gate here) |
| 5 | Bracket depth (unsigned) |
| 6 | Zero-test temp, then the final error code |
| 7, 8 | Instruction count, low then high |
| 9 | Bytes left in this group (0 means 256 at group entry) |
| 10 | Full 256-byte groups still to come |
| 11 | Sticky bracket error |
| 12 | Sticky size error |
| 13 | Main-loop flag; later the success-output gate |
| 14, 15 | Open/close bracket flags; reused as counter scratch afterwards |

---

## 🔁 Filtering and validation

1. **Length check (once).** If the high length byte is 255 and the low byte is 254
   or 255, set size error 12. This rejects sources over 65,533 bytes without
   skipping any byte or the terminator. Cost: 269 instructions, no extra cells.
2. **Group setup.** A nonzero low byte is the first group size. A zero low byte
   means a full 256-group, and high is decremented once. Empty source skips this.
3. **Per byte** (each pass starts and ends at offset 13):
   - read the byte;
   - decode it with one copy and a subtraction chain (43, 44, 45, 46, 60, 62,
     91, 93), so a match skips the rest;
   - update depth, then the group counter.
   The high byte is tested only at group ends. All scratch returns to zero.
   Worst case 4,381 instructions per byte.
4. **Brackets.** A wrapping open sets the size error. A close at depth 0 sets the
   bracket error. Nonzero final depth sets the bracket error. Size beats brackets.
5. **Capacity.** The working marker is 1 exactly when 3,840 instructions are
   stored, and each byte just copies that flag. The count-high compare runs only
   on a low-byte carry (at most 15 times). A full buffer rejects commands but
   still accepts ignored bytes. The working marker is cleared before output, so
   no phantom instruction is emitted.
6. **Store.** A recognized command below the limit marks the slot, bumps the count
   and moves live state 16 cells right.
7. **Always consume the whole source**, even after an error, so the terminator
   can be checked.

At most 3,840 instructions fit. The last working slot spans cells 61,456–61,471.
Nothing scans left of the sentinel.

Proofs: [P0 proofs](../docs/07_OPTIMIZATION_PROOFS.md) (131,072-state counter,
512-state decoder, 7,682-state capacity flag).

---

## 📤 Output

`42 46 58 00 01 status`, then on success the u32 count and each stored
instruction in order (scanning marked slots back to the sentinel). Failures are
exactly 6 bytes. There is never partial success output, but OS writes aren't
atomic, so callers must reject truncated output.

---

## 🧰 When you edit it

- Keep byte consumption, error priority and instruction order.
- Comments must not contain any of the eight instruction characters.
- Re-check raw and filtered hashes, slot bounds, all fixtures, limits and agreement
  with an independent interpreter.

📎 [canonical_bfx.json](../evidence/canonical_bfx.json) (current) ·
[frontend_capacity_gate.json](../evidence/frontend_capacity_gate.json) (pre-migration) ·
[bootstrap](../docs/04_BOOTSTRAP.md)

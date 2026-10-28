# 📦 BFX format

> BFX (Ballsdeep Brainfuck XAX), extension `.bfx`: the one record BBC hands to XAX.

One format for every optimization level, source size and target. Numbers are
unsigned little endian. What the program *does* is defined by the
[Brainfuck profile](01_BRAINFUCK_PROFILE.md).

---

## 🧱 Record

```text
Success: 42 46 58 00 | 01 | 00     | count:u32 | count instruction bytes
Failure: 42 46 58 00 | 01 | status
```

| Bytes | Field | Value |
|---|---|---|
| 0–3 | Magic | `42 46 58 00` (`BFX` + NUL) |
| 4 | Format id | Exactly `01` (the byte, not ASCII `1`) |
| 5 | Producer status | 0 = success, anything else = failure |
| 6–9 | Instruction count | Success only |
| 10+ | Instructions | Exactly `count` bytes |

- ✅ A success is exactly `10 + count` bytes. A failure is exactly 6 bytes.
- 🚫 No padding, no extra fields, no trailing bytes, no other count widths.
- 🧮 Check `10 + count` for overflow before comparing lengths.
- 🗑️ A failure is a valid answer but never an importable program. Discard
  partial or failed output; file writes are not atomic.

Producer failure codes: **1** missing or bad terminator, **2** unmatched
brackets, **3** too big. Framing is checked first, then size, then brackets.

Old layouts (3-byte magic, ids 01–05) are rejected outright. There is no
fallback and no legacy decoder: recompile old sources, don't patch headers.

---

## 🔤 Instructions

| Byte | Meaning |
|---|---|
| ASCII `+ - > < . , [ ]` | The usual Brainfuck instruction |
| `00` | CLEAR: set the current cell to 0 |
| `01`–`07` | Add `2^n` (wraps) |
| `08`–`0E` | Subtract `2^(n−7)` (wraps) |
| `0F`–`15` | Move right `2^(n−14)` cells |
| `16`–`1C` | Move left `2^(n−21)` cells |

Every other byte is invalid. The count includes every instruction, brackets and
CLEAR too, and brackets must balance.

- CLEAR is a real instruction, so a zero byte is never a terminator.
- A packed move fails at the same first step its unit moves would, and the
  pointer stays on the last valid cell.
- Opposite moves never cancel. A loop that starts on zero runs nothing.
- A record carries no optimization level, size class, target or unsafe flags.

---

## ✔️ Validation

The one XAX decoder checks length, magic, id, status, count, every opcode and
bracket pairing **before** anything is imported. Until then the data is untrusted.

| Decoder status | Meaning |
|---|---|
| 1 | Bad framing or magic |
| 2 | Unsupported id |
| 3 | Producer reported failure |
| 4 | Too big |
| 5 | Invalid opcode |
| 6 | Unmatched brackets |

These are separate from producer status codes.

---

## 📏 Budgets

The count field could hold any u32. Today's importer accepts up to **65,536
instructions**, so balanced nesting tops out at **32,768**. Bigger counts are
rejected before any payload is read.

| Component | Raw source | Instructions | Nesting |
|---|---:|---:|---:|
| Public entry (`stream_chunks.bf` + XAX) | 1,048,576 bytes | 65,536 before packing | 32,768 |
| Private bounded seed (`compiler.bf`) | 65,533 bytes | 3,840 | 255 |

Both emit identical BFX. The compiled program's tape is 2,147,246,080 bytes, committed as
touched ([XAX dynamic tape](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/DYNAMIC_TAPE.md)).
These are fixed budgets; growing them at runtime is not built yet
([scalability](16_SCALABILITY.md)).

---

## 🔒 Private formats

Users never see these; they exist for bootstrapping.

**Bounded seed request.** `source_length:u16 | source | 01`.

- The length counts every byte, including NUL and whitespace.
- Lengths up to 65,533 are accepted, which leaves room for the length and the
  terminator in a 64 KiB buffer. 65,534 and 65,535 are rejected.
- A missing terminator fails even at end of file.
- The terminator catches truncation, not corruption.

**Bounded passes.** They take a complete, already validated success record of
up to 3,840 instructions, followed by `01`, and emit BFX again.

- They trust the header and count; they are not decoders for untrusted input.
- A bad terminator gives failure 1.
- Their count goes through a 16-bit stage, so the top two count bytes are always 0.
- Validate their output before publishing or importing it.

The streaming coordinators use private BBCS/BBCR packets. Those are not BFX.

---

## 🧪 Exact examples

| Input | BFX bytes |
|---|---|
| Empty program | `42 46 58 00 01 00 00 00 00 00` |
| `+` | `42 46 58 00 01 00 01 00 00 00 2B` |
| One CLEAR | `42 46 58 00 01 00 01 00 00 00 00` |
| Unmatched bracket | `42 46 58 00 01 02` |
| Missing terminator | `42 46 58 00 01 01` |

Binary fixture pairs: [tests/bfx](../tests/bfx/README.md).

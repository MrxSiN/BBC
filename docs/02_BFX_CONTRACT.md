# 📦 BFX format

> BFX (Ballsdeep Brainfuck XAX), extension `.bfx`: the one record BBC hands to XAX.

One format for every optimization level, source size and target. What the
program *does* is defined by the [Brainfuck profile](01_BRAINFUCK_PROFILE.md).
The current format id is **`02`** (2026-10-29). Id `01` records are rejected
outright: recompile old sources, don't patch headers.

---

## 🧱 Record

```text
Success: 42 46 58 00 | 02 | 00     | body | FF
Failure: 42 46 58 00 | 02 | status
```

| Bytes | Field | Value |
|---|---|---|
| 0–3 | Magic | `42 46 58 00` (`BFX` + NUL) |
| 4 | Format id | Exactly `02` (the byte, not ASCII `2`) |
| 5 | Producer status | 0 = success, anything else = failure |
| 6 … n−2 | Body | Instructions, each an opcode byte and its operands |
| n−1 | END | `FF`, the last byte of every success |

- ✅ A success is the 6-byte header, the body and `FF`; its body length is the
  record length minus 7. A failure is exactly 6 bytes.
- 📏 **No count field.** The record carries no width that could cap a program;
  its length is whatever the transport delivered. The id `01` u32 count is gone.
- 🚫 No padding, no extra fields, no trailing bytes after END.
- 🗑️ A failure is a valid answer but never an importable program. Discard
  partial or failed output; file writes are not atomic.

Producer failure codes: **1** missing or bad terminator, **2** unmatched
brackets, **3** too big. Framing is checked first, then size, then brackets.

---

## 🔤 Instructions

| Bytes | Meaning |
|---|---|
| ASCII `+ - > < . , [ ]` | The usual Brainfuck instruction |
| `00` | CLEAR: set the current cell to 0 |
| `01 d k` | ADD: cell at `p+d` += `k` (wraps) |
| `02 d k` | MUL: cell at `p+d` += cell at `p` × `k` (wraps) |
| `03 d` | CHECK: `p+d` must lie on the tape |
| `04 n` | MOVE: `p` += `n` |
| `FF` | END, only as the record's last byte |

`d` and `n` are signed bytes (−128…127), `k` an unsigned byte. Every other
opcode is invalid, and an operand may not run past the body.

- **Bounds.** ADD, MUL, CHECK and MOVE fail with status 1 (`POINTER_BOUNDS`)
  when `p+d` (or `p+n`) is off the tape, before any effect of that instruction.
  `<` and `>` keep their first-crossing rule; the pointer stays on the last valid cell.
- **Why that is exact.** BBC only emits offset instructions inside a *segment*:
  a stretch with no loop or input/output. Every point where the original path could
  first leave the tape is a turning point or the segment's end, and each one gets an
  ADD, MUL, CHECK or MOVE at that offset. A failure inside a segment is reported
  before the segment's next input/output, so callers see the same status and output.
- **MUL** reads the cell at `p`, which no instruction in its group changes.
  BBC emits it only inside a guarded loop (`[ … 00 ]`), so the checks and products
  happen exactly when the original loop would have run.
- A loop that starts on zero runs nothing. Opposite moves never silently cancel:
  their extremes stay checked.
- A record carries no optimization level, size class, target or unsafe flags.

---

## ✔️ Validation

The one XAX decoder checks length, magic, id, status, END, every opcode, every
operand length and bracket pairing **before** anything is imported. Until then the
data is untrusted. Operand bytes are never read as instructions.

| Decoder status | Meaning |
|---|---|
| 1 | Bad framing, magic or END |
| 2 | Unsupported id |
| 3 | Producer reported failure |
| 4 | Too big |
| 5 | Invalid opcode or truncated operand |
| 6 | Unmatched brackets |

These are separate from producer status codes. XAX keeps runtime checks for every
offset access; it never trusts a producer's claim that an access is in range.

---

## 📏 Budgets

The format has no size field. The remaining limits are buffers, not the wire
format, and are listed in [scalability](16_SCALABILITY.md): today the importer's
record view still accepts 65,536 body bytes and the public entry 1 MiB of source.

| Component | Raw source | Instructions | Nesting |
|---|---:|---:|---:|
| Public entry (`stream_chunks.bf` + `fold.bf` + XAX) | 1,048,576 bytes | 65,536 before folding | 32,768 |
| Private bounded seed (`compiler.bf`) | 65,533 bytes | 3,840 | 255 |

Both emit BFX `02`. The compiled program's tape is 2,147,246,080 bytes, committed as
touched ([XAX dynamic tape](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/DYNAMIC_TAPE.md)).

---

## 🔒 Private formats

Users never see these; they exist for bootstrapping.

**Bounded seed request.** `source_length:u16 | source | 01`.

- The length counts every byte, including NUL and whitespace.
- Lengths up to 65,533 are accepted, which leaves room for the length and the
  terminator in a 64 KiB buffer. 65,534 and 65,535 are rejected.
- A missing terminator fails even at end of file.
- The terminator catches truncation, not corruption.

**Fold pass.** [`fold.bf`](../compiler/fold.bf) reads validated primitive
instructions followed by a zero byte and writes a BFX body; XAX frames it.
It trusts its input and is never run on unvalidated source.

The streaming coordinator uses private BBCS packets. Those are not BFX.

---

## 🧪 Exact examples

| Input | BFX bytes |
|---|---|
| Empty program | `42 46 58 00 02 00 FF` |
| `+` (O0) | `42 46 58 00 02 00 2B FF` |
| `+` (O1) | `42 46 58 00 02 00 01 00 01 FF` |
| `[->+<]` (O1) | `42 46 58 00 02 00 5B 02 01 01 00 5D FF` |
| Unmatched bracket | `42 46 58 00 02 02` |
| Missing terminator | `42 46 58 00 02 01` |

Binary fixture pairs: [tests/bfx](../tests/bfx/README.md).

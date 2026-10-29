# 🧠 Brainfuck profile

> The rules every BBC program follows, on every target. One tape, one pointer, no surprises.

Applies to Android ARM64, Windows x86-64 and Linux x86-64 alike. Which targets
are actually *tested* lives in [status](05_STATUS.md).

---

## 📜 The language

| Thing | BBC does |
|---|---|
| Instructions | `><+-.,[]`. Every other byte is ignored |
| Tape | 2,147,246,080 cells (2 GiB − 232 KiB), each one byte, all start at zero. Pages are committed only when touched |
| Arithmetic | Wraps: 255 + 1 is 0 |
| Pointer | Starts at cell 0 |
| Moving off the tape | Fails immediately, at the first step past the edge |
| Input `,` | Reads the next byte. After end of input, reads 0 |
| Output `.` | Writes the cell's byte. Fails if output space runs out |
| Loops `[ ]` | Repeat while the current cell is not zero |
| Unmatched brackets | Rejected at compile time |

- 🔁 A loop that starts on zero never runs its body, so its moves never happen.
- ♾️ Programs may loop forever. A test driver's step limit is not part of the language.
- 💬 Comments are just ignored bytes. `#` means nothing special, so keep the eight
  instruction characters out of your comments.

Source size limits live in the [BFX spec](02_BFX_CONTRACT.md#-budgets).

---

## 🔌 How a compiled program is called

Inside, every program is one function:

```text
run_decision(input) -> status + output
```

- It borrows three separate 2,147,246,080-byte views: input (read-only), output and tape. Hosts
  reserve them and commit pages on first touch; input and output capacity stay 65,536.
- Two 32-bit numbers give the real input length and the output space. Either can
  be zero; neither can exceed its buffer.
- Every call starts at cell 0 on a zero tape: the decision clears cells 0–65,535 and the
  host provides a freshly reserved, zero tape. Bad lengths are rejected *before* the tape
  is touched.
- Output bytes past what was written stay untouched.

The result packs into one number: `(output_length << 32) | status`.

| Status | Meaning |
|---|---|
| 0 | ✅ Success |
| 1 | Moved off the tape |
| 2 | Output space ran out |
| 3 | Invalid input length or output space |

On any failure, throw the output away. These codes are separate from BFX and
importer errors. The raw-pointer function is internal; the typed XAX caller
proves the buffers are valid. See [XAX integration](03_XAX_INTEGRATION.md).

---

## 📱 The demo decision

[examples/decision.bf](../examples/decision.bf) reads one flag byte. Zero writes
`01` (permit); anything else writes `00` (block). End of input also reads zero,
so the app must always send exactly one byte.

The Android demo takes `flag` 0–255 and `capacity` 0–16 (defaults 0 and 1),
calls the decision, and shows:

| UI mode | Result | Sample row |
|---|---|---|
| 0 | PERMIT: returned `01` | Visible |
| 1 | BLOCK: returned `00` | Hidden |
| 2 | ERROR: bad input, native failure or odd output | Hidden |

- Capacity 0 deliberately hits the "output ran out" path.
- The demo decision is small and runs on the UI thread. Programs that might loop
  forever must run off the main thread; that worker path is not built yet.

---

## 🛡️ Rules for optimizations

Every rewrite must keep, exactly:

- output bytes and input consumption
- byte wrapping and the final pointer
- whether loops terminate
- the order of out-of-bounds failures

So opposite moves (`<>`) never cancel: the first move may already fail. Each new
rule needs positive, negative, nested-loop, wraparound and tape-edge tests against
an independent interpreter before it is switched on.

The passes that pass this bar: [offset and loop folding](10_FOLD_OPTIMIZATION.md). Proofs live in
[optimization proofs](07_OPTIMIZATION_PROOFS.md).

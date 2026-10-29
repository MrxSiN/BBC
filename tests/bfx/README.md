# 🧪 BFX fixtures

> Exact bytes in, exact bytes out. If a fixture changes, something broke or a spec changed on purpose.

These are private fixtures for the bounded seed. Public-interface regressions
live in [tests/compile](../compile/README.md). Read the [BFX spec](../../docs/02_BFX_CONTRACT.md)
before touching any fixture byte. `.gitattributes` protects them from line-ending
conversion, and the `.bfx` extension alone doesn't make a file valid.

---

## 🔤 Compiler fixtures

Each `.request` is exact bounded-compiler input; the matching `.bfx` is the
complete expected answer, including error records.

| Fixture | Status | Body bytes | Checks |
|---|---|---|---|
| [all-eight](all-eight.request) | 0 | 8 | All eight instructions survive |
| [bad-close](bad-close.request) | 2 | — | Unmatched `]` |
| [bad-open](bad-open.request) | 2 | — | Unmatched `[` |
| [empty](empty.request) | 0 | 0 | Valid 7-byte empty module |
| [nested](nested.request) | 0 | 18 | Nested loops |
| [raw-zero](raw-zero.request) | 0 | 2 | Literal NUL and FF are ignored |
| [safe-annotations](safe-annotations.request) | 0 | 2 | Comment text is ignored |
| [truncated](truncated.request) | 1 | — | Missing terminator |
| [truncated-zero](truncated-zero.request) | 1 | — | Ends in NUL, still no terminator |
| [invalid-terminator](invalid-terminator.request) | 1 | — | Terminator present but not `01` |
| [group-boundary](group-boundary.request) | 0 | 2 | 257 bytes crossing the first group edge |
| [opcode-bytes](opcode-bytes.request) | 0 | 8 | All 256 byte values → exactly the eight instructions in order |

Run [compiler.bf](../../compiler/compiler.bf) on each request under an independent
interpreter that follows the [profile](../../docs/01_BRAINFUCK_PROFILE.md), and compare
stdout byte for byte. For a native frontend, check both the native call status
and the BFX status; they are separate.

---

## ▶️ Program fixtures

| Program | Input → expected output | Checks |
|---|---|---|
| [basic.bf](../basic.bf) | [basic.input](basic.input) → [basic.output](basic.output) | Byte wrap, literal zero, EOF |
| [loops.bf](../loops.bf) | [loops.input](loops.input) → [loops.output](loops.output) | Nested loops, raw byte `04` |
| [decision.bf](../../examples/decision.bf) | [permit.input](permit.input) → [permit.output](permit.output) | Zero flag → `01` |
| [decision.bf](../../examples/decision.bf) | [block.input](block.input) → [block.output](block.output) | Nonzero flag → `00` |
| [bounds.bf](../bounds.bf) | empty → bounds failure | Move left from cell 0 |
| [bounds_right.bf](../bounds_right.bf) | empty → bounds failure | Run off the right edge |

[Bootstrap fixtures](../bootstrap/) pair `.input`/`.output` for
[frame_source.bf](../../bootstrap/frame_source.bf): empty, plain text and NUL-terminated text.
Oversized text produces nothing.

---

## 🔁 Pass fixtures

[fold-cases.json](fold-cases.json) (19) holds exact binary input/output pairs for
[`fold.bf`](../../compiler/fold.bf): segments, turning points, both edges, folded and
unfolded loops, and I/O. Each input is validated primitive instructions plus a zero byte;
each output is a BFX `02` body. Every pair was checked against an independent interpreter
on tapes of 8, 64 and 1,024 cells.

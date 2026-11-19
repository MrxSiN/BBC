# 📏 Scalability and limits

> How big a program BBC eats, and why the plate is fixed-size for now.

One public entry, [`compile_bfx`](21_UNIFIED_COMPILATION.md), handles every size.
Size never changes the [BFX format](02_BFX_CONTRACT.md) or the importer. BFX `02` has no
count field, so the wire format itself no longer caps a program; the limits below are buffers.

| Resource | Public streaming entry | Private bounded seed |
|---|---:|---:|
| Raw source | 1,048,576 bytes | 65,533 bytes |
| Instructions before optimization | 1,048,576 | 3,840 |
| Balanced nesting | 32,768 | 255 |

- **Bounded seed.** 16 tape cells per instruction, a one-byte depth, a u16
  length and a 64 KiB input view. Its last working cell is 61,471. These are
  implementation choices, not language limits.
- **Streaming entry.** Validates 32 KiB chunks with a u64 depth counter and
  wide pairing indices. Count limits are checked before any payload is read.
- The compiled program's tape is 2,147,246,080 cells, reserved up front and committed page by
  page as the program touches it (Windows: a commit-on-touch handler; Android: `mmap`).
  The edge comes from XAX's x86-64 bound encoding, not from BBC; see XAX OI-52.

---

## 🧱 The native backend is the real ceiling today

The frontend accepts 1,048,576 instructions, but the native XAX driver inside `bbc.exe`
declines (exit 5) much smaller decisions. Measured 2026-10-29 with the BFX `02` `bbc.exe`
on Windows, O0, by bisection on repeated patterns:

| Pattern | Builds up to | Declines from | Decision blocks / nodes at the edge |
|---|---:|---:|---|
| `+` | 4,941 | 4,942 | 4,951 / 15,109 |
| `>` | 4,213 | 4,214 | 4,223 / 8,711 |
| `[]` | 2,420 pairs | 2,421 | 4,851 / 9,967 |
| `+>` | 4,155 pairs | 4,156 | 8,321 / 21,063 |
| `.` | 4,162 | 4,163 | 8,335 / 16,935 |

No single count (blocks, nodes, values, edges, edge arguments, operands or fragment
bytes) or positive linear combination of them explains all five edges, so the limit
is inside the driver's verifier rather than a table size the frontend could respect.
It is XAX's open native-coverage issue
([OI-51](https://github.com/MrxSiN/XAX/blob/main/XAX_OPEN_ISSUES.md)). Folding moves
real programs under it: Mandelbrot's 11,451 instructions build at O1 (3,145 BFX
instructions) but still decline at O0. Since packed decision lengths (2026-10-31) factor O0 builds on
Windows, and the mandelbrot O0 decline is in the native verifier itself, before lowering.

---

## 🎚️ Raising the instruction budget

BBC#4 asks for at least 300,000 commands before folding, for the six ThreadsHideAds
policy programs (69,343 to 296,307 commands, all under 1 MiB). Measured 2026-11-15 on
Windows: 65,536 `+` pass and 65,537 exit 2, even at O1, where they would fold to 7 bytes
([evidence](../evidence/instruction_cap_2026-11-15.json)).

- `stream_chunks.bf` counts per chunk and `fold.bf` sees the whole body; neither has a
  total-count limit, so BBC's Brainfuck needs no change.
- The budget is `compile_bfx`'s capacity check and the record view it shares
  with the decoder and importer ([XAX integration](03_XAX_INTEGRATION.md)). Both are XAX
  code: raised in XAX release 0037 ([XAX#55](https://github.com/MrxSiN/XAX/issues/55)).
- Native builds of decisions that large also meet XAX OI-54 (2^18 values per function view).

**Raised (2026-11-19).** XAX release 0037 makes the budget 1,048,576, the 1 MiB source limit, so every
source that fits the frame fits the budget. The overflow fixtures in [tests/compile](../tests/compile/README.md)
moved to the new edge: 1,048,577 commands give status 3 even when a bracket error comes first, and
1,048,576 commands with an unmatched bracket give status 2
([evidence](../evidence/instruction_cap_2026-11-19.json)).

The six ThreadsHideAds programs now pass `check` and `emit-bfx` at O0 and O1. Their counts and record
hashes are the [regression set](../tests/compile/threadshideads.json)
([evidence](../evidence/xax_pin_0037_2026-11-19.json)).

---

## 🌱 Growing at runtime

Possible, but not built. It needs, at every layer, not just one constant:

- a canonical XAX allocation and growth interface;
- checked arithmetic and defined allocation failures;
- growable source, record, pairing and graph storage;
- matching validation and optimization budgets.

📎 [streaming compilation](17_STREAMING_COMPILATION.md)

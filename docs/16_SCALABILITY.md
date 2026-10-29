# 📏 Scalability and limits

> How big a program BBC eats, and why the plate is fixed-size for now.

One public entry, [`compile_bfx`](21_UNIFIED_COMPILATION.md), handles every size.
Size never changes the [BFX format](02_BFX_CONTRACT.md) or the importer. BFX `02` has no
count field, so the wire format itself no longer caps a program; the limits below are buffers.

| Resource | Public streaming entry | Private bounded seed |
|---|---:|---:|
| Raw source | 1,048,576 bytes | 65,533 bytes |
| Instructions before optimization | 65,536 | 3,840 |
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

## 🌱 Growing at runtime

Possible, but not built. It needs, at every layer, not just one constant:

- a canonical XAX allocation and growth interface;
- checked arithmetic and defined allocation failures;
- growable source, record, pairing and graph storage;
- matching validation and optimization budgets.

📎 [streaming compilation](17_STREAMING_COMPILATION.md)

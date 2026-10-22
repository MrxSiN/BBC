# 📏 Scalability and limits

> How big a program BBC eats, and why the plate is fixed-size for now.

One public entry, [`compile_bfx`](21_UNIFIED_COMPILATION.md), handles every size.
Size never changes the [BFX format](02_BFX_CONTRACT.md) or the importer.

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
- The compiled program's 65,536-cell tape is a separate, fixed language rule.

---

## 🌱 Growing at runtime

Possible, but not built. It needs, at every layer, not just one constant:

- a canonical XAX allocation and growth interface;
- checked arithmetic and defined allocation failures;
- growable source, record, pairing and graph storage;
- matching validation and optimization budgets.

📎 [capacity audit](../evidence/scalability_capacity_audit.json) · [chunk prototype](../evidence/streaming_frontend_prototype.json) · [streaming compilation](17_STREAMING_COMPILATION.md)

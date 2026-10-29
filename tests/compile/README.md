# 🧪 Public compilation regressions

> Edge cases for the one public entry point, plus two very deep programs.

Each `.request` is exact `length:u32 | source | 01` data for the
[unified interface](../../docs/21_UNIFIED_COMPILATION.md), placed at source/work offset
65,531. Put the actual frame length at offset 0 and the level at offset 4.
[cases.json](cases.json) has the expected status at O0 and O1. Failed calls return
length 0; never publish their buffers.

| Cases | Must return | Why |
|---|---|---|
| Two overflow cases | 3 (too big) | Even when a bracket error comes earlier |
| Two exact-capacity cases | 2 (brackets) | Capacity is fine, brackets aren't |
| Empty and binary cases | Exact valid BFX | Framing |

The first two rows lock in the coordinator's cross-chunk error precedence.

---

## 🕳️ Depth 512

`deep_nesting_512` has a `.bf` source and an expected O1 `.bfx` (BFX `02`, from `fold.bf`):

- **Zero-entry** prints `01`.
- **Active** enters all 512 loops, runs the innermost body three times and prints `03 02 01 00`.

Both pass the native frontend at O0 and O1, and their Android builds run on a Pixel 8 Pro
([native Android lowering](../../evidence/native_android_lowering.json)). O0 keeps primitives,
so its record differs from O1 while using the same BFX format.

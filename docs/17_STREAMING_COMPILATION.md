# 🌊 Streaming compilation

> Big programs, validated 32 KiB at a time, folded in one call.

The public [`compile_bfx`](21_UNIFIED_COMPILATION.md) drives two Brainfuck passes:

| Step | Brainfuck | How it runs |
|---|---|---|
| Filter and validate | [`stream_chunks.bf`](../compiler/stream_chunks.bf) | Once per 32 KiB chunk, private BBCS packets |
| O1 folding | [`fold.bf`](../compiler/fold.bf) | Once, on the whole validated body |

The output is ordinary [BFX `02`](02_BFX_CONTRACT.md), read by the same decoder as
everything else. No size tag, no second format.

---

## 🧭 Rules

- 📐 Budgets: 1 MiB source, 32 KiB chunks, 65,536 instructions before folding,
  balanced nesting up to 32,768 ([scalability](16_SCALABILITY.md)).
- ⏳ Tokens stay provisional until the whole source is valid. The BFX header and END
  are written only after that.
- 🗑️ On any coordinator failure, throw the whole buffer away. Its status is not
  a BFX failure record.
- 🪗 `fold.bf` needs no chunk state: it sees the whole body. If it fails or its body does
  not fit the record view, the O0 record is published instead.

The 2026-10-22 run packer (`stream_runs.bf`, BBCR packets) is retired with BFX `01`.

---

## 🏗️ Where it lives

XAX `compiler/integration/bfx/`: `compile.xax` (coordinator and `compile_bfx`),
`import_bfx.xax` and the shared decoder `bfx.xax`
([BFX 02 in XAX](https://github.com/MrxSiN/XAX/blob/bbc/bfx-v2-fold/compiler/integration/bfx/BFX_V2.md)).
Buffer sizes are in [XAX integration](03_XAX_INTEGRATION.md).

📎 [fold_v2.json](../evidence/fold_v2.json) · [unified_compilation.json](../evidence/unified_compilation.json)

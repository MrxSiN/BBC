# 🌊 Streaming compilation

> Big programs, eaten 32 KiB at a time.

The public [`compile_bfx`](21_UNIFIED_COMPILATION.md) drives two Brainfuck passes
through private packets:

| Step | Brainfuck | Packet |
|---|---|---|
| Filter and validate | [`stream_chunks.bf`](../compiler/stream_chunks.bf) | BBCS |
| O1 run packing | [`stream_runs.bf`](../compiler/stream_runs.bf) | BBCR |

The output is ordinary [BFX](02_BFX_CONTRACT.md), read by the same decoder as
everything else. No size tag, no second format.

---

## 🧭 Rules

- 📐 Budgets: 1 MiB source, 32 KiB chunks, 65,536 instructions before packing,
  balanced nesting up to 32,768.
- ⏳ Tokens stay provisional until the whole source is valid. The BFX header is
  written only after that.
- 🗑️ On any coordinator failure, throw the whole buffer away. Its status is not
  a BFX failure record.

The packer:

- requires a validated success record and checks magic, id, status and count;
- is not a replacement for the full decoder;
- keeps CLEAR and already-packed opcodes, and packs identical arithmetic and
  one-way move runs;
- must end with an empty pending state, and its in-place copying never overtakes unread input.

---

## 🏗️ Where it lives

XAX `compiler/integration/bfx/`: `source.xax`, `pack.xax`, `import_bfx.xax` and
the shared decoder `bfx.xax`. Buffer sizes are in [XAX integration](03_XAX_INTEGRATION.md).
These are fixed views; runtime growth is not built.

📎 [stream_runs.json](../evidence/stream_runs.json) · [unified_compilation.json](../evidence/unified_compilation.json)

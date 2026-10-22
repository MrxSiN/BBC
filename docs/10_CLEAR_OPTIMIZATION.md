# 🧹 Clear-loop pass

> `[-]` is a very long way of saying "zero". This pass says it in one byte.

[`optimize.bf`](../compiler/optimize.bf) takes a validated BFX success of up to
3,840 instructions plus terminator `01`, and emits the same [BFX format](02_BFX_CONTRACT.md).

| Input | Output |
|---|---|
| `[-]` or `[+]` | CLEAR (`00`) |
| 256 identical `+` or `-` in a row | Nothing (they wrap to the identity) |
| `[--]`, `[++]` and other even-step loops | Left alone: they may loop forever |
| Moves | Never cancelled |
| Packed opcodes | Passed through |

- Each 16-cell slot keeps its marker separate from the opcode, so CLEAR (`00`)
  can't end a scan early.
- A bad terminator gives BFX failure 1. The top two count bytes are always zero.
- Tape layout: [optimize.bf notes](../compiler/optimize.bf.notes.md).
- Proof: [optimization proofs](07_OPTIMIZATION_PROOFS.md#-p1-clear-loops-and-full-wraps).
- Old measurements: [v2 report](11_V2_BENCHMARKS.md).

You don't call this directly. [`bbc compile -O1`](25_NATIVE_COMPILE.md) runs it for you.

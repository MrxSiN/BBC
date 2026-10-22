# ➡️ Movement packing

> `>>>>>>>>` but in one byte, and it still falls off the tape at exactly the right step.

[`pack_moves.bf`](../compiler/pack_moves.bf) takes a validated BFX success of up
to 3,840 instructions plus `01`, and emits the same [BFX format](02_BFX_CONTRACT.md).

- Seven passes, from 128 down to 2, replace runs of identical moves with one
  packed move.
- A packed move fails at the same first step its unit moves would, and the
  pointer stays on the last valid cell.
- Opposite moves never cancel. A loop that starts on zero still skips its body.
- CLEAR passes through as a real zero-valued opcode. Output never grows.
- A bad terminator gives failure 1.

Tape layout: [pack_moves notes](../compiler/pack_moves.bf.notes.md) ·
proof: [optimization proofs](07_OPTIMIZATION_PROOFS.md#-p1-movement-powers) ·
old measurements: [v4 report](15_V4_BENCHMARKS.md).

You don't call this directly. [`bbc compile -O1`](25_NATIVE_COMPILE.md) runs it for you.

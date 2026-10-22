# ➕ Arithmetic packing

> 128 plus signs in a row is one instruction wearing a trench coat.

[`pack_arithmetic.bf`](../compiler/pack_arithmetic.bf) takes a validated BFX
success of up to 3,840 instructions plus `01`, and emits the same [BFX format](02_BFX_CONTRACT.md).

- Seven passes, from 128 down to 2, replace runs of identical `+` or `-` with
  one power-of-two opcode. A leftover single step stays ASCII.
- Addition and subtraction wrap mod 256.
- Packed opcodes and every other instruction end a run and pass through.
- Output never grows. A bad terminator gives failure 1.

Tape layout: [pack_arithmetic notes](../compiler/pack_arithmetic.bf.notes.md) ·
proof: [optimization proofs](07_OPTIMIZATION_PROOFS.md#-p1-arithmetic-powers) ·
old measurements: [v3 report](13_V3_BENCHMARKS.md).

You don't call this directly. [`bbc compile -O1`](25_NATIVE_COMPILE.md) runs it for you.

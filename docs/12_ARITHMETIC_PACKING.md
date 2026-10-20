# Arithmetic packing

[`pack_arithmetic.bf`](../compiler/pack_arithmetic.bf) consumes a validated,
successful BFX record of at most 3,840 instructions plus terminator `01`.
It emits the same [BFX format](02_BFX_CONTRACT.md). The header is a trusted
private precondition; publication requires complete record validation.

Seven descending scans group identical unit arithmetic commands in powers of
two, from 128 through 2. A group of K operations becomes one declared arithmetic
opcode; bit-zero units remain ASCII. Addition and subtraction wrap modulo 256.
Existing encoded operations and other commands stop a run and pass through.
The pass never expands the instruction stream. Bad terminator emits failure 1.

[Tape notes](../compiler/pack_arithmetic.bf.notes.md) explain staging and deletion
markers. Historical correctness and measurements remain immutable in
[bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json) and
[the benchmark report](13_V3_BENCHMARKS.md); they do not measure this migration.

The supported end-user route is [unified compilation](21_UNIFIED_COMPILATION.md).
These component contracts describe private BF implementation/bootstrap details;
users do not select a separate BFX format or manually negotiate passes.

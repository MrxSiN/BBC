# Movement packing

[`pack_moves.bf`](../compiler/pack_moves.bf) consumes a previously validated BFX
success of at most 3,840 instructions followed by `01`. It emits exactly the
same [BFX format](02_BFX_CONTRACT.md), including the identifier and u32 count.
It trusts the private header/count precondition. Bad terminator emits failure 1.

Seven descending scans replace identical monotone moves in groups of 128 through
2 with the declared movement powers. Encoded operations and opposite moves stop
a run. Every executed move retains its first-crossing trap and last valid cursor.
Opposite movement must never cancel, and zero-entry loops must still skip their
bodies. Output does not expand. CLEAR passes through as a real zero-valued opcode.

[Tape notes](../compiler/pack_moves.bf.notes.md) describe the separate markers.
Historical correctness and timing snapshots stay in
[bfx_v4_movement.json](../evidence/bfx_v4_movement.json) and
[the benchmark report](15_V4_BENCHMARKS.md), with their original source identities.

The supported end-user route is [unified compilation](21_UNIFIED_COMPILATION.md).
These component contracts describe private BF implementation/bootstrap details;
users do not select a separate BFX format or manually negotiate passes.

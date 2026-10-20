# Clear-loop optimization

[`optimize.bf`](../compiler/optimize.bf) transforms a validated bounded BFX
success plus terminator byte `01`. Input and output follow the single
[BFX specification](02_BFX_CONTRACT.md); optimization never changes its identifier.
The helper trusts the complete header, opcode and bracket validation precondition.

Exact `[-]` and `[+]` become CLEAR (`00`). Longer/even-step loops retain their
meaning and must not be rewritten as CLEAR. Complete groups of 256 consecutive
identical arithmetic commands disappear by modular arithmetic. No movement is
cancelled and source validation happens first. Existing packed opcodes pass through.

A sixteen-cell slot stores its marker independently from the opcode so CLEAR
cannot end a scan. At most 3,840 instructions fit this bounded helper; the upper
two serialized count bytes are zero. [Tape notes](../compiler/optimize.bf.notes.md)
describe staging and rewinds. Missing/invalid terminator emits BFX failure 1.
Historical optimization and timing snapshots remain in
[bfx_v2_optimization.json](../evidence/bfx_v2_optimization.json) and
[the benchmark report](11_V2_BENCHMARKS.md); their old wire identities are historical.

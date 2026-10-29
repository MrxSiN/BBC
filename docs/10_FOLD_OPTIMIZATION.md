# 🪗 Offset and loop folding

> `>>+++<<` is one instruction. `[->+++<]` is three, and they run once.

[`fold.bf`](../compiler/fold.bf) is BBC's O1 pass since 2026-10-29. It reads the
validated primitive instructions of a whole program and writes a
[BFX `02`](02_BFX_CONTRACT.md) body. It replaced the run packer (`stream_runs.bf`) and the
bounded clear pass (`optimize.bf`); both are retired and remain in git history.

| Input | Output |
|---|---|
| A segment of `+ - < >` (no loop or I/O inside) | One ADD per touched cell, a CHECK per unaccessed turning point, one MOVE |
| `[-]`, `[+]` | CLEAR (`00`) |
| `[->+++>++<<]` and every loop whose single-segment body returns to its counter and steps it by ±1 | `[` MUL per touched cell, CHECKs, `00` `]` |
| 256 identical `+` | Nothing: the net change is 0 |
| `[--]`, `[++]`, `[>]`, nested loops, loops with I/O, loops whose counter cell moves | Left as loops |
| Offsets beyond ±127 | The segment ends early at the window edge; a long move becomes several MOVEs |

- One call on the whole body: no 3,840-instruction gate and no chunk state.
- The pass trusts validated input; XAX's decoder still checks its output before import.
- If folding fails for any reason or its body does not fit the record view, `compile_bfx`
  returns the O0 record instead. O1 never rejects a program O0 accepts.
- Tape layout and fixtures: [fold.bf notes](../compiler/fold.bf.notes.md).
- Proof: [optimization proofs](07_OPTIMIZATION_PROOFS.md#-p1-offset-and-loop-folding).

You don't call this directly. [`bbc compile -O1`](25_NATIVE_COMPILE.md) runs it for you.

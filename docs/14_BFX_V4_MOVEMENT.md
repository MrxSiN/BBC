# BFX v4 monotone movement powers

The optional [`pack_moves.bf`](../compiler/pack_moves.bf) pass consumes a
complete **validated successful v3 record followed by required byte `01`**.
It emits v4. It is an internal transformer, not a validator of untrusted
records. Use the transparent frontend, validate v1, run the clear pass,
validate v2, run arithmetic packing, validate v3, then run movement packing.
Validate its complete result before import. Discard output from a failed
native call. A missing/wrong terminator emits the five-byte `BFX 04 01` error.

Successful framing remains `BFX || 04 || 00 || count:u16le || operations`,
exactly `7 + count` bytes. The limit remains 3,840 operations and nesting 255;
raw-source acceptance remains 65,533 bytes. No pass expands a record.

| Payload byte | Effect |
|---|---|
| `00` | CLEAR |
| `01`..`07` | Add `2^opcode` modulo 256 |
| `08`..`0E` | Subtract `2^(opcode - 7)` modulo 256 |
| `0F`..`15` | Move right by `2^(opcode - 14)` |
| `16`..`1C` | Move left by `2^(opcode - 21)` |
| Original eight ASCII commands | Unchanged |
| All other bytes | Reject |

V1, v2 and v3 retain their strict accepted byte sets. Unknown versions reject.
All accepted earlier decision stores retain their exact bytes. XAX's standalone
`bfx.xax` validator remains strict v1; the importer embeds the extended decoder.

## Equivalence and failures

Only adjacent, identical unit moves combine. For `K = 2..128`, a successful
right group visits `p+1` through `p+K`; left visits `p-1` through `p-K`.
Monotonicity makes all intermediate positions valid exactly when the endpoint
is valid. The group performs no I/O, cell mutation or conditional test.
On failure the original stops at the first attempted crossing, after reaching
0 or 65,535. The grouped lowering returns the same bounds status, preserves all
prior input/output/tape effects and passes that last valid cursor to the
failure block. It never exposes a wrapped endpoint to continuation or memory.

A checked conditional branch stays at its original control-flow position;
zero-entry loops bypass movement and its bounds check. Opposite moves never
cancel: `<>` at position zero must trap. `+[<>-]` remains a negative case.
No loop, I/O, arithmetic or CLEAR operation is crossed while forming a group.
The [tape notes](../compiler/pack_moves.bf.notes.md) describe the bounded producer.

XAX emits three pure graph nodes per packed move: derive `K` by a supported
32-bit rotate of existing constant one, compute a 32-bit endpoint, then compare.
Right failure is `endpoint > 65535`; left failure is `old_position < K`.
Right addition cannot overflow 32 bits under the existing cursor invariant.
Left subtraction may wrap only on a failure path that discards that endpoint.
No new constant-pool entry, unchecked access or generic backend code is added.
The complete 65,536-byte tape reset and invalid-length-before-reset guard stay.

## Executed checks

[Immutable correctness evidence](../evidence/bfx_v4_movement.json) retains the
frozen pre-execution design alongside executed results. There are 432 native
BF packing properties, 72 independent binary-output C-interpreter cases and
1,164 exact Android/Windows importer comparisons, including every payload byte
for each version. Peak observed BF tape cell is 61,469. The source has 5,347
bytes and 3,719 instructions, within the original frontend/framer limits.

Forty-two decision modules have 2,398 vectors per arm/target: **9,592 full-buffer
calls**. Both directions and every power pass nearby boundary positions,
five alignments, dirty tape, immutable input, guards, EOF, output-failure
ordering, skipped loops, trap-reaching loops and invalid 32-bit logical lengths.
The baseline is independently interpreted original eight-command source.

All four BF components pass three byte-identical native rebuild generations
on Android and Windows. Each frontend generation passes twelve exact fixtures.
Native Android import stores match Windows. The frontend's unchanged source
still emits transparent v1; its v4 native implementation contains 812 operations.
Clear, arithmetic and movement helpers contain 901, 1,057 and 1,063 operations.
Windows-hosted unchanged generic XAX bootstrap tools still verify and lower.
Component fixed points do not establish a complete native compiler host.
Performance and competitor completion require separate matched measurements.

The [published canonical consumer](https://github.com/MrxSiN/XAX/blob/ab25b75f7cc0f03d06aae3cab7d84327c59c5e37/compiler/integration/bfx/MOVEMENT.md)
contains both verified expected-root transactions. The [boundary supplement](../evidence/bfx_v4_native_boundaries.json)
adds ten current frontend source/framing checks per target, two oversized-view
guards and three exact maximum-count v4 stores, including depth-255 nesting.
[Matched measurements](15_V4_BENCHMARKS.md) keep execution, build, resource
and complete file-size results separate from earlier snapshots.

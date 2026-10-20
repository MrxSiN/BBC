# Compiler scalability and limits

Both frontend routes emit [BFX](02_BFX_CONTRACT.md). Source capacity and
optimization level never select a different wire layout or importer.

| Resource | Bounded BF frontend | Streaming route |
|---|---:|---:|
| Raw source | 65,533 bytes | 1,048,576 bytes |
| Instructions before optimization | 3,840 | 65,536 |
| Balanced nested loops | 255 | 32,768 |

The bounded frontend stores sixteen tape cells per instruction and keeps depth
in one byte. Its request length is u16 and the native input view is 65,536 bytes,
including two length bytes and one terminator. These are implementation choices,
not Brainfuck language restrictions. Its last working cell is 61,471.

The streaming route validates chunks with a u64 depth counter, coordinates larger
fixed source/work views and uses wide import pairing indices. It compiles sources
that exceed the bounded frontend's limits. BFX always carries a u32 count, including
empty and small modules. The decoder's present 65,536-instruction budget is checked
before payload access; balanced nesting cannot exceed half that count.

Dynamic growth is possible, but is not implemented. It requires a canonical XAX
allocation/growth interface, checked arithmetic, defined allocation failures,
growable source/record/pairing/graph storage and matching validation/optimization
budgets. Raising one constant does not address every layer. The compiled program's
65,536-byte execution tape is a separate language contract. Historical
[capacity audit](../evidence/scalability_capacity_audit.json) and
[chunk prototype](../evidence/streaming_frontend_prototype.json) retain their
original implementation limits. See [streaming compilation](17_STREAMING_COMPILATION.md).

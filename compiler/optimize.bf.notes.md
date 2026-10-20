# Optional BFX optimizer

[`optimize.bf`](optimize.bf) is an independent standard Brainfuck pass. It
recognizes exact unit-step clear loops and complete groups of 256 identical
arithmetic commands. The [v2 contract](../docs/10_BFX_V2_CLEAR.md) defines its
private input boundary, encoding, proofs and rejection requirements.

The authoritative frontend still accepts raw framed source and emits
transparent BFX v1. Invoke this pass only after successful frontend completion
and validation of that complete v1 success record. Append a byte `01`. Failed
compilations bypass it. The pass assumes the validated header and operation
stream; it does not independently establish those preconditions.

## Tape and phases

The tape is 65,536 wrapping bytes, initially zero. Slots have stride sixteen.
The sentinel precedes the first slot. Each slot holds a marker at offset zero
and an opcode at offset one; marker and opcode are distinct so CLEAR byte zero
does not stop scanning. Offsets seven/eight carry the output count, nine/ten
carry arithmetic run state, twelve marks a deleted slot and thirteen is a
temporary continuation/gate. Other cells hold local comparison/copy scratch
and counted-input state. State is transferred to the next slot, rather than
indexed through a second array.

1. Discard the five validated fixed header bytes, preserve the bounded count
   and stage exactly that many operation bytes in marked slots.
2. Require the terminator. Carry the output count to the sentinel and then
   into the first slot. Do not consume bytes following the terminator.
3. Scan forward. An exact `[-]` or `[+]` becomes CLEAR in the opening slot;
   mark its other two slots deleted and decrement the count by two.
4. Count consecutive identical arithmetic modulo 256. On wrap, mark that
   group deleted, walk back over its 255 predecessors and subtract 256 from
   the output count. Temporary continuation markers restore the forward scan.
5. Emit the known version, status and final count, rewind through marked
   slots and emit only undeleted operations. Preserve zero-valued CLEAR.

Every accepted input fits the existing 3,840-operation limit. The pass itself
has 2,931 instructions in 4,393 raw bytes; its SHA-256 is
`6f1b09b2f7719ea80b90fe0a4def3c172714de964a7a9587ae2e64806442d177`.
Its own optimized module has 2,851 operations. At the maximum input count,
the independent interpreter observes peak cell 61,469. Neither source nor
output limits are expanded. No rewrite can increase the record length.

## Correctness and use

Clear recognition never accepts `[++]`, `[--]`, movement, I/O or a nested
body. Removing a full wrapping run from a loop can leave an ordinary empty
loop; nonzero entry must still loop indefinitely. Opposite movements are
never cancelled. The full tape reset and each retained access check remain
part of the generated decision contract.

Require native success and validate the entire returned v2 record before
import. A native output-capacity failure can expose a prefix resembling
success; discard it. Missing/incorrect terminators emit a five-byte v2
framing error. Behavior outside the validated-v1 precondition is unspecified.

[Optimization evidence](../evidence/bfx_v2_optimization.json) contains native
and independent checks, exact consumption, all-byte and boundary tests,
three-generation fixed points, artifact hashes and separate performance
measurements. Unchanged generic XAX bootstrap verification and lowering
remain required; recognition executes this Brainfuck implementation.

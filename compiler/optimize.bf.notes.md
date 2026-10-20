# Optional BFX optimizer

Current source has 4395 bytes and 2946 BF instructions; raw SHA-256 `971fc93a10bc2ce9840f7bc675c57b6a994bd5c45757a24191a93c72852b1259`,
filtered SHA-256 `33255827d324a2fa9b797366e7f6fa8561fef3ea7088a2ea11ea37f96e613174`. All current framing follows the single
[BFX specification](../docs/02_BFX_CONTRACT.md). Older counts, hashes and
rebuild results quoted below are historical snapshots, not this source identity.

[`optimize.bf`](optimize.bf) is an independent standard Brainfuck pass. It
recognizes exact unit-step clear loops and complete groups of 256 identical
arithmetic commands. The [pass guide](../docs/10_CLEAR_OPTIMIZATION.md) defines its
private input boundary, encoding, proofs and rejection requirements.

The authoritative frontend still accepts raw framed source and emits
transparent BFX. Invoke this pass only after successful frontend completion
and validation of that complete BFX success record. Append a byte `01`. Failed
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

1. Discard the six validated fixed header bytes, preserve the bounded count
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

Every accepted input fits the existing 3,840-operation limit. Current source identity is listed above. At the maximum input count,
the independent interpreter observes peak cell 61,469. Neither source nor
output limits are expanded. No rewrite can increase the record length.

## Correctness and use

Clear recognition never accepts `[++]`, `[--]`, movement, I/O or a nested
body. Removing a full wrapping run from a loop can leave an ordinary empty
loop; nonzero entry must still loop indefinitely. Opposite movements are
never cancelled. The full tape reset and each retained access check remain
part of the generated decision contract.

Require native success and validate the entire returned BFX record before
import. A native output-capacity failure can expose a prefix resembling
success; discard it. Missing/incorrect terminators emit a six-byte BFX
framing error. Behavior outside the validated BFX precondition is unspecified.

[Historical optimization evidence](../evidence/bfx_v2_optimization.json) contains native
and independent checks, exact consumption, all-byte and boundary tests,
three-generation fixed points, artifact hashes and separate performance
measurements. Unchanged generic XAX bootstrap verification and lowering
remain required; recognition executes this Brainfuck implementation.

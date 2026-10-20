# Arithmetic packer tape notes

[`pack_arithmetic.bf`](pack_arithmetic.bf) implements the private validated-v2
to v3 pass in [the contract and proof](../docs/12_BFX_V3_ARITHMETIC.md).
It is standard Brainfuck; annotations contain no executable characters.

Slots have stride sixteen. Offset zero is a persistent marker, one the opcode,
five the descending phase code, seven/eight the output count, nine the current
run length, ten the previous unit opcode, eleven the group threshold and twelve
the deletion flag. Thirteen holds temporary backward-walk continuations;
fourteen is a gate or the new encoded operation, and fifteen the walk counter.
Offsets two through four and six provide local copies, comparisons and count
borrowing. The end slot's framing status is preserved independently.

After counted input staging and terminator checking, phase seven starts with
threshold 128. A forward scan excludes deleted slots, resets state at other
operations and counts identical unit arithmetic. At a full group, carry the
encoded operation backward, mark the group deleted, retain its first slot and
subtract `K - 1` from the output count with explicit borrowing. Continuation
markers restore the original scan position and are cleared.

Phase state and count move through the slots. At the end, decrement the phase,
halve its even threshold and rewind those fields to the first slot. Seven
iterations reach phase zero. A final bounded scan carries the result count to
the end; the existing marked-slot walk emits only live operations. Larger
encodings and zero-valued CLEAR remain distinct from markers and deletions.

The count never increases, all walks stay inside the staged region and the
maximum observed cell is 61,469. The source is 5,259 bytes / 3,639 instructions;
its own optimized module has 3,258 operations. Bootstrap needs the frontend,
clear helper and this helper as separate bounded programs. It does not
concatenate their source or relax the 3,840-instruction acceptance limit.

[Evidence](../evidence/bfx_v3_arithmetic.json) records independent interpretation,
exact consumption, native properties and three identical generations of all
three components on Android and Windows. The execution profile, full reset,
source validation, failure-output discard rule and transparent v1 route remain.

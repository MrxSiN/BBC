# Movement packer tape notes

[`pack_moves.bf`](pack_moves.bf) implements the private validated-v3 to v4 pass
in [the contract](../docs/14_BFX_V4_MOVEMENT.md). It is standard Brainfuck;
annotations contain none of the eight executable characters.

Slots have stride sixteen. Offset zero is the persistent marker; one holds
the payload opcode. Five holds the descending phase; seven/eight hold output
count; nine is run length, ten the previous raw move, eleven the threshold and
twelve the deletion flag. Thirteen carries backward-walk continuation;
fourteen is a temporary gate/new encoded opcode and fifteen the walk count.
Offsets two through four and six provide copies, comparisons and count borrowing.
The end slot keeps framing status independently.

After counted staging and terminator checking, seven scans descend through
thresholds 128, 64, 32, 16, 8, 4 and 2. Only undeleted identical raw movement
opcodes contribute to a run. Deleted slots, all arithmetic encodings and other
commands end a run. A complete group is marked deleted, its first slot retained
with the declared movement encoding, and output count reduced by `K - 1`.
The walk restores scan position and clears temporary continuations.

Phase/count state moves through the slots and rewinds between passes. Already
encoded groups are never combined. Final emission follows markers and copies
only live opcodes, including zero-valued CLEAR. Markers, opcodes and deletion
flags occupy distinct cells. No source pointer cancellation is performed.

All walks stay within the staged region and output count never increases.
The maximum observed cell is 61,469 for the unchanged 3,840-operation limit.
The source is 5,347 bytes / 3,719 instructions; its own v4 native module contains
1,063 operations. Bootstrap invokes four bounded BF components separately,
without concatenating sources or increasing frontend acceptance limits.

[Correctness evidence](../evidence/bfx_v4_movement.json) records exact counted
consumption, native properties, independent interpretation, both native targets
and three identical rebuild generations. Full tape reset and first-failure
semantics remain part of the decision contract.

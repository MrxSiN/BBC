# Movement packer tape notes

Current source has 5342 bytes and 3732 BF instructions; raw SHA-256 `254910fea21d82ddf31c3ce89569b691ca68f468ba26695561cf6a0f23a792c9`,
filtered SHA-256 `608e867e4e3b9c7d326dd1b9250705e382e5a960d257b04b86a9a5a514da2b0b`. All current framing follows the single
[BFX specification](../docs/02_BFX_CONTRACT.md). Older counts, hashes and
rebuild results quoted below are historical snapshots, not this source identity.

[`pack_moves.bf`](pack_moves.bf) implements the private validated BFX pass
in [the contract](../docs/14_MOVEMENT_PACKING.md). It is standard Brainfuck;
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
Current source identity is listed above. Bootstrap invokes four bounded BF components separately,
without concatenating sources or increasing frontend acceptance limits.

[Historical correctness evidence](../evidence/bfx_v4_movement.json) records exact counted
consumption, native properties, independent interpretation, both native targets
and three identical rebuild generations. Full tape reset and first-failure
semantics remain part of the decision contract.

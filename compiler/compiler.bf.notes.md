# BBC frontend algorithm and tape layout

Current source has 4545 bytes and 2200 BF instructions; raw SHA-256 `89e87c42d870e879c4dbbf2ec578da2823351566d3e7d25801f29b5804446b2a`,
filtered SHA-256 `a9323e9daa898c76693df7b66647f58ddb16dd67d91db72ee76b710250b6c358`. All current framing follows the single
[BFX specification](../docs/02_BFX_CONTRACT.md). Older counts, hashes and
rebuild results quoted below are historical snapshots, not this source identity.

Authoritative source: [compiler.bf](compiler.bf). Wire format:
[BFX](../docs/02_BFX_CONTRACT.md). Execution semantics:
[Brainfuck profile](../docs/01_BRAINFUCK_PROFILE.md).

The frontend reads one known-length request, filters and validates the eight
instructions, then emits either a complete instruction record or a six-byte
compiler-error record. It performs no semantic optimization and owns no
native-code or platform backend.

## Tape layout

The first sixteen cells stay zero as a left sentinel. Work begins at cell 16.
For `n` stored instructions the working slot begins at `16 * (n + 1)`.

| Slot offset | Meaning |
|---|---|
| 0 | Stored-instruction marker; working slot reuses it as a Boolean full flag; sentinel stays zero |
| 1 | Raw source byte; retained as opcode in a stored slot |
| 2, 3 | Destructive comparison and restoration scratch |
| 4 | Recognized-command flag; initialization temporarily saves the nonempty gate here |
| 5 | Unsigned bracket depth |
| 6 | Temporary zero-test flag, then final error code |
| 7, 8 | Filtered instruction count, low byte then high |
| 9 | Current group byte counter; zero encodes 256 at an active group entry |
| 10 | Number of later full 256-byte groups |
| 11 | Sticky bracket error |
| 12 | Sticky size error |
| 13 | Main-loop flag; later success-output gate |
| 14, 15 | Opening and closing bracket flags; reused as group-counter scratch after bracket processing |

## Filtering and validation

Before the main loop, copy length-high into scratch cells 2 and 3 and restore
it. Adding one and testing for zero recognizes high byte 255. Only in that
case, copy and restore length-low twice; adding one or two recognizes 255 or
254 respectively. Either case sets sticky size error 12. Scratch cells return
to zero and both length bytes are unchanged. This rejects source beyond
65,533 without skipping any declared byte or its terminator. The check uses
269 extra source instructions, no extra tape cells, and runs once per request;
it changes neither the per-byte loop nor the maximum instruction slot.

For nonempty source, initialization saves the loop gate in cell 4, prepares
the first byte group, then restores the gate and clears cell 4. A nonzero
length-low byte gives the first group size. Zero length-low starts a full
256-byte group and decrements length-high once. Empty source skips both.

Each main iteration begins and ends at offset 13. It sets continuation to one,
reads one raw byte, decodes the eight opcodes and updates bracket depth.
After bracket flags are consumed, the group counter decrements and tests its
low byte once using cells 14 and 15. Only at a completed group does it test
the high byte, selecting a later full group or stopping. Scratch cells return
to zero before slot transfer. Opcode decoding preserves the raw byte using a
single copy into comparison scratch. Nested mismatch branches subtract the
gaps between ASCII values 43, 44, 45, 46, 60, 62, 91 and 93. A match skips
all later comparisons. The final mismatch clears the command and bracket
flags. Scratch returns to zero; bracket flags are set only for their exact
bytes. The decoder passes all 256 bytes at both extreme working slots while
preserving every other tape cell, with at most 4,381 dispatched instructions.
The exact counter invariant, 131,072-state regression and decoder proof
are documented in [P0 proofs](../docs/07_OPTIMIZATION_PROOFS.md).

An opening bracket that wraps depth sets the sticky size error. A close at
depth zero sets the sticky bracket error without subtracting. A nonzero final
depth sets the bracket error. Size takes priority over bracket diagnostics.

The working slot's marker is one exactly when the stored count is 3,840.
The per-byte guard copies that Boolean flag, preserving it. A full buffer
rejects only a recognized command, clearing cell 4 and setting size error 12.
The expensive count-high comparison runs only when count-low carries, at
most fifteen times: high becoming fifteen marks the next working slot full.
Stored slots retain marker one. Before record emission, clear the current
working marker so output scanning cannot emit a phantom instruction.
No state is transferred on ignored or rejected bytes.
All 7,682 reachable count/command states pass whole-tape checks; see the
[capacity-gate proof](../docs/07_OPTIMIZATION_PROOFS.md#p0-carry-triggered-capacity-flag).

If an instruction is recognized and count-high is below fifteen, the frontend
marks the old slot, increments the count with carry, and transfers live state
sixteen cells right. The raw instruction stays in the old slot. A full buffer
rejects further instructions without advancing; ignored trailing bytes remain
valid. After any error the declared source is still consumed, so the required
terminator can be checked before choosing the final status.

At most 3,840 instructions are stored. The working slot then spans cells
61,456 through 61,471. Rejected input never creates another slot. No scan goes
left of the zero sentinel. These layout bounds are also exercised by the
external instrumented interpreter; they are not a claim about an XAX backend.

## Record emission

After validation, the frontend emits BFX magic `42 46 58`, NUL magic byte, identifier
`01` and the compiler status. Success additionally emits the little-endian u32
count, scans marked slots left to the sentinel, then outputs each
stored instruction in order. Failures emit exactly six bytes. This prevents
partial success output for rejected source; it does not promise atomic OS
writes. Callers must reject incomplete transport output.


## Maintenance checks

Preserve request consumption, diagnostic priority and exact instruction order
when editing the source. Annotations must contain none of the eight executable
instruction characters. Check raw and filtered hashes independently, slot
bounds, all exact fixtures, resource limits and independent-interpreter
agreement after executable changes.

Current own-source records, stores and native cycles are in
[canonical migration evidence](../evidence/canonical_bfx.json). Earlier
[capacity-gate evidence](../evidence/frontend_capacity_gate.json) retains its
pre-migration source identity. The [optional optimizer](optimize.bf.notes.md)
changes the payload representation, while both routes emit the same BFX format.
[Bootstrap](../docs/04_BOOTSTRAP.md) explains authority and replay.

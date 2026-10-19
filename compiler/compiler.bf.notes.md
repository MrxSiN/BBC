# BBC frontend algorithm and tape layout

Authoritative source: [compiler.bf](compiler.bf). Wire format:
[BFX v1](../docs/BFX_CONTRACT.md). Execution semantics:
[Brainfuck profile](../docs/BRAINFUCK_PROFILE.md).

The frontend reads one known-length request, filters and validates the eight
instructions, then emits either a complete instruction record or a five-byte
compiler-error record. It performs no semantic optimization and owns no
native-code or platform backend.

## Source identity

Raw SHA-256: `45a5ae43b6cebfe854453827e321c11be2b7ab50db4d78f6a2360b241ed2014b`.
Filtered SHA-256: `ecc84ea90ad9cb1b2d314686078177f8e8b9a430300f09a94a34d3777dd5c536`.
The source has 4,531 bytes and 2,455 instructions. Annotations contain none
of the eight instruction characters. Whitespace and annotations are ignored
by ordinary interpreters, without preprocessing.

## Tape layout

The first sixteen cells stay zero as a left sentinel. Work begins at cell 16.
For `n` stored instructions the working slot begins at `16 * (n + 1)`.

| Slot offset | Meaning |
|---|---|
| 0 | Stored-instruction marker; zero in sentinel and current working slot |
| 1 | Raw source byte; retained as opcode in a stored slot |
| 2, 3 | Destructive comparison and restoration scratch |
| 4 | Recognized-command flag |
| 5 | Unsigned bracket depth |
| 6 | Temporary zero-test flag, then final error code |
| 7, 8 | Filtered instruction count, low byte then high |
| 9, 10 | Remaining raw source length, low byte then high |
| 11 | Sticky bracket error |
| 12 | Sticky size error |
| 13 | Main-loop flag; later success-output gate |
| 14, 15 | Opening and closing bracket flags |

## Filtering and validation

Each main iteration begins and ends at offset 13. It clears that flag, reads
one raw byte, compares all eight opcode values, updates bracket depth, and
decrements the 16-bit remaining length with borrow. The next-loop flag is the
OR of the remaining length bytes. All comparisons preserve the raw byte.

An opening bracket that wraps depth sets the sticky size error. A close at
depth zero sets the sticky bracket error without subtracting. A nonzero final
depth sets the bracket error. Size takes priority over bracket diagnostics.

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

After validation, the frontend emits BFX magic `42 46 58`, binary version
`01` and the compiler status. Success additionally emits the little-endian
count, scans marked slots left to the sentinel, then outputs each
stored instruction in order. Failures emit exactly five bytes. This prevents
partial success output for rejected source; it does not promise atomic OS
writes. Callers must reject incomplete transport output.


## Maintenance checks

Preserve request consumption, diagnostic priority and exact instruction order
when editing the source. Annotations must contain none of the eight executable
instruction characters. Check raw and filtered hashes independently, slot
bounds, all exact fixtures, resource limits and independent-interpreter
agreement after executable changes.

The own-source BFX is 2,462 bytes: seven bytes of framing and 2,455 instructions.
Interpreted agreement alone is seed verification. Three native frontend
rebuild generations execute separately on Android and Windows through the
canonical XAX importer; [bootstrap](../docs/BOOTSTRAP.md) describes that cycle.
[Current evidence](../evidence/bfx_android_importer.json) binds native results
to this source hash, and [the fixture guide](../tests/bfx/README.md) describes
regression inputs. This tape map governs the Brainfuck frontend, not the XAX
importer's separate serialization workspace.

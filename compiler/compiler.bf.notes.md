# Portable frontend tape map

Authoritative source: [compiler.bf](compiler.bf).
Raw SHA-256: `56bc7b195c3ff06d5bb61c6363f10558c270dcaead89fa96e627ee767ccae91e`.
Filtered SHA-256: `2b4d63023917ec76545f7118c00fe9829736a8eeb06e65844f6902492684fd42`.
The source has 4,531 bytes and 2,455 instructions. Annotations contain none
of the eight instruction characters. Whitespace and annotations are ignored
by ordinary interpreters, without preprocessing.

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

After validation, the frontend emits BBX magic, binary version and status. Success additionally
emits the count, scans marked slots left to the sentinel, then outputs each
stored instruction in order. Failures emit exactly five bytes. This prevents
partial success output for rejected source; it does not promise atomic OS
writes. Callers must reject incomplete transport output.

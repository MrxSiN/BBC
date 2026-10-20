# Streaming identical-run packing

Current source has 11124 bytes and 10976 BF instructions; raw SHA-256 `aae50166e21d0647806cf7edac3ce5d5ea8fbd84cdf0a37ad785ed026016dcb3`,
filtered SHA-256 `4c6697cecb6c5b6a3e1dcdb7baee6409a7ebf58f37877c2f57c9f49a43c6a1ef`. All current framing follows the single
[BFX specification](../docs/02_BFX_CONTRACT.md). Older counts, hashes and
rebuild results quoted below are historical snapshots, not this source identity.

`stream_runs.bf` is a standard Brainfuck pass for the private wide compilation
profile. It consumes trusted provisional BFX instruction chunks, preserves
two continuation bytes, and emits BFX opcode bytes. The canonical
XAX coordinator owns whole-record framing and final publication. This pass
does not validate untrusted BFX records or bracket balance.

Input is `pending_opcode:u8 || pending_count:u8 || chunk_count:u16le || final:u8
|| instructions[chunk_count] || 01`. Chunks contain at most 32,768 validated BFX
instructions. Initial state is two zero bytes; final is Boolean. Pending opcode
is zero, plus, minus, left or right. Zero opcode requires zero count. Arithmetic
counts range from zero through 255; movement counts remain below 128. Only
state returned by a successful preceding call is valid continuation state.

Output is `BBCR || 01 || packed_instructions || pending_opcode:u8 ||
pending_count:u8 || output_count:u16le || status:u8`. It has exactly
`10 + output_count` bytes. Status one means bad/missing terminator; all bytes
are provisional until both this pass and complete source validation succeed.
No delimiter is needed: the fixed five-byte footer supplies the count.

The count of identical arithmetic instructions wraps modulo 256. On a change
of instruction or final input, binary decomposition emits the original ASCII
unit instruction for bit zero and the corresponding power opcode for bits
one through seven. The sum is exactly the original arithmetic modulo 256.
Complete 256-command groups disappear. Opposite directions remain separate.

Identical movement emits a 128-step opcode immediately at count 128. Remaining
movement decomposes in the same way at a run boundary. Every group moves in
one direction. The importer retains endpoint checking and last-valid-cursor
failure behavior, so a group cannot hide an intermediate bounds failure.
Opposite movements never cancel. Loops, input and output flush the pending run
and retain their original order. Non-unit encoded opcodes including zero-valued CLEAR flush any pending run and
pass through unchanged; only recognized ASCII unit operations may coalesce.
Clear-loop recognition is not part of this
pass; the bounded optimization pipeline retains its separate clear optimization.

For an unfinished arithmetic run the pending count represents its length
modulo 256. A movement run has emitted every complete 128-step group and holds
the remaining length. This invariant is independent of chunk boundaries.
Final flush leaves zero continuation state. Cumulative packed output never
exceeds cumulative consumed instructions, including the pending run; the XAX
coordinator checks this before copying output into the record in place.

## Tape

| Cells | Meaning |
|---|---|
| 0, 1 | Pending opcode and count |
| 4..11 | Remaining chunk length, four cells per byte |
| 12, 13 | Final flag and current input byte |
| 16..23 | Output count, four cells per byte |
| 24, 25 | Equality scratch and restoration |
| 26..30 | Predicate, parity, quotient, toggle and encoded opcode |
| 31..36 | Recognition and branch scratch |
| 37 | Framing status |

Cells 2..3, 14..15 and 38..65,535 remain zero. Copy destinations and restoration
scratch are zero at each helper entry. Division consumes the count into a
quotient and parity, restores the quotient as the next count, then consumes
the parity to emit one power. Each flush ends with a zero count and opcode.
Current source identity is listed above. It exceeds the original
frontend's instruction budget and is bootstrapped through the wide profile.

See [wide compilation](../docs/17_STREAMING_COMPILATION.md) for capacities, executed
evidence and the remaining work toward runtime workspace growth.

# BF-owned Android resource optimizer

Source SHA-256: `4874b23e0bc5d8356b4783368fe43df40f774b5f0f0e91198b0023671fefb014`

Filtered instruction SHA-256: `eb1a1f47d2cc065952b18190a74096bb3068ed1338d82704066b4049efb5b511`

This second raw BF stage contains 15,767 commands, within the production
compiler's 16,128-command capacity. Both independent BF seeds execute
`compiler/core.bf` to produce identical 504,759-byte Linux ELFs. Windows
executed the interpreters, not the generated Linux executables.

The internal byte protocol and sixteen-cell records are the same as
[the affine stage](android_native_optimize.bf.notes.md). Input must come from
that stage after upstream source validation. Cell 12 also carries the bounded
tape flag. It is not a general ELF optimizer or a parser for untrusted images.

If every opening bracket begins one of the six recognized clear/transfer
patterns, every loop returns to its entry pointer. At most ten source commands
can contain at most ten ordinary pointer moves. From the initial pointer zero,
all successful reachable addresses are within cells 0..10, with an adjacent
transfer using no more than cell 11. A zeroed sixteen-byte stack allocation
therefore replaces the 65,536-byte data mapping. `PT_RW` and `PT_DYNAMIC` become
`PT_NULL`. Every `<` retains its original underflow guard. Ordinary `>` moves
can skip the upper-bound guard under this proof; original trap instructions
remain available to the generic transfer code. The generated image exits
directly and does not need to restore the entry stack pointer.

Any unrecognized loop keeps the original full tape and pointer checks.
This includes nested loops and loops with nonzero net pointer travel.
The proof relies on the normal entry pointer zero. Artificial nonzero-entry
tests exercise retained generic transfer guards, not the bounded startup.

An initial comma followed immediately by either right-transfer pattern reads
at cell zero and transfers to an initially zero cell one. Its replacement can
store the source directly at cell one, clear cell zero, then skip the loop.
This preserves the final tape as well as output, including zero and EOF.
Unused trailing command slots branch directly to the existing exit sequence.
Read and write status handling remains in the original slots: unsuccessful
reads exit(4), unsuccessful writes exit(3); Android slots do not retry EINTR.

The fixed 4,192-byte file and source ceiling of ten commands remain. This is
a bounded prototype, not general affine analysis or Android compiler
self-hosting. The [test](../tests/verify_android_native_optimization.py)
compares complete bytes to an independent encoding oracle, stdout/status and
the entire tape to the BF reference, two load bases, read/write faults,
conditional bounds, two seed implementations and native phone executions.

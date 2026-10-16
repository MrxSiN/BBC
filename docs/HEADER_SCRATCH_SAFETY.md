# Header scratch safety — Iteration 20

The 39 Brainfuck arithmetic loops introduced in Iteration 19 shortened the compiler enough to self-host with in-core source filtering. They reuse tape cell 61 as a counter. The safety assumption matters, so this iteration verifies it explicitly instead of hoping a zeroed cell stays zero forever.

## Static contract

Run `python3 tests/verify_header_scratch.py`. The checker reads **the actual filtered Brainfuck instruction stream** and locates the ELF header block using the SHA-bound source notes: BF offsets `2848:4277`.

The proof assumes entry at **pointer 60** with **cell 61 equal to zero**, using the documented wrapping byte semantics. It establishes, independent of the values in other tape cells:

- Every instruction in the block keeps the pointer within cells **60 through 71**.
- All **45** loops return the pointer to the position at their corresponding opening bracket. Six are single-cell clearing loops; 39 are arithmetic loops.
- Each of the **39** scratch loops has a known positive 8-bit counter and a `-1` induction step. It therefore terminates after exactly that many iterations and leaves cell 61 at zero. Its loop body only accesses cells 60 and 61.
- No other instruction changes cell 61 in a way that invalidates the abstract counter value. The final pointer is 60 and cell 61 is zero.
- Writes are restricted to cells **60, 61, 69, 70 and 71**. Reads/loop conditions use only the bounded region.

The checker rejects four deliberate source mutations that break pointer movement, a loop counter update or bracket structure. Test code performs this inspection; machine-code generation is still exclusively inside `compiler/core.bf`.

## Runtime entry witnesses

`python3 tests/verify_compiler_tape.py` executes the authoritative BF compiler under an independently compiled, audit-only BF interpreter. Eight sources, including the full compiler and the maximum 16,128-command input, reach both header boundaries once with pointer 60 and zeroed cell 61. The instrumented seed rejects a mismatched entry/exit condition. This is **EXECUTED** evidence, stored in `evidence/compiler_tape_audit.json`.

## What this does not prove

The static argument is **conditional**. It does not yet prove every possible decoder path reaches the header with the stipulated pointer and zeroed scratch cell, nor that all compiler buffer records, counters and bracket-stack metadata remain disjoint. It also does not prove ELF output or the machine-code backend correct in isolation. Those are covered by other regression evidence, not by this argument.

The next safety task is to establish the decoder-to-header preconditions for arbitrary well-formed and malformed input. No compiler-wide S3 memory-safety claim follows from this local result. Machine-readable details live in [`../evidence/header_scratch_safety.json`](../evidence/header_scratch_safety.json).

# Tape-safety audit

The test is deliberately narrower than a compiler proof. We have a fixed native backend with small, identifiable instruction templates. Those templates can be checked against a state invariant before calling them safe.

## Invariant

On entry to every reachable Brainfuck instruction slot, the native compiler must maintain:

- `r13 = 0x600000`: first tape address.
- `r14 = 0x610000`: one-past-last tape address.
- `r12` is at least `r13` and strictly below `r14`.
- Every load, store, and one-byte `read`/`write` buffer is addressed through `r12`.

Startup initializes those registers. `+`, `-`, `[`, `]`, `,`, and `.` leave them alone. `>` increments `r12`, checks it against `r14`, and traps with `exit(2)` if the result is outside the tape. `<` decrements `r12`, checks against `r13`, and traps likewise. There is no cell access between the movement and the guard. Branch targets are verified to land on slot boundaries. For Linux x86-64, `syscall` does not overwrite the preserved `r12`–`r14` registers.

This gives a conditional inductive argument for **generated program tape accesses** when the actual executable matches the accepted templates and the documented hardware/OS semantics hold. It is not a proof that the BF compiler's own four-cell source buffer and scratch allocations can never overlap.

## Gate

```sh
python3 tests/verify_tape_safety.py
```

- Checks fixed pointer, arithmetic and I/O template bytes, plus native startup.
- Exhaustively evaluates the two abstract guarded pointer moves at every one of the **65,536** tape positions: **131,072** transitions, exactly two invalid boundary moves.
- Independently validates the compiler ELF and each generated witness ELF with `tests/verify_emission.py`'s strict slot/relocation checker.
- Executes **nine** native examples, including both boundary traps, loops, EOF, and maximum source size.
- Rejects **ten** modified artifacts that corrupt guards, memory operands, startup registers, or memory permissions. Mutants are inspected, not executed.

Evidence: [`../evidence/tape_safety_audit.json`](../evidence/tape_safety_audit.json).

## What is still missing

A checked machine template plus mathematical pointer-index reasoning is stronger than merely running Hello World. It is still not an independent formal x86 decoder, exhaustive machine-level proof, compiler-internal memory proof, or defense against a hostile kernel. Bounds-check elimination remains off limits until the proof obligations for the affected programs are discharged.

**Status: STRUCTURAL + EXECUTED evidence. Not S3 certification.**

## Compiler-internal execution evidence

[`COMPILER_TAPE_AUDIT.md`](COMPILER_TAPE_AUDIT.md) records eight executed BF compiler tape traces and source-cell checks, including the maximum supported input. This supplements, but does not close, the compiler-internal nonoverlap question. Source-byte cells are temporarily reused by codegen; the audit tests their values at phase boundaries, not on every intermediate instruction.

## Compiler header arithmetic proof

For a narrowly scoped compiler-internal conditional proof rather than generated tape guards, see [`HEADER_SCRATCH_SAFETY.md`](HEADER_SCRATCH_SAFETY.md). It checks the original BF instruction stream and eight executed header-entry witnesses. It does not establish full compiler tape nonoverlap.

# Compiler tape audit

The native tape guard prevents out-of-range Brainfuck pointer movement. It does **not** prove the compiler's own buffer, scratch cells and loop metadata never overlap. Those are different questions.

`tests/verify_compiler_tape.py` instruments an audit-only build of the independent C Brainfuck seed. The build executes `compiler/core.bf` directly. It does not implement a parser for the language being compiled, an ELF emitter, or a hidden compiler backend. The regular bootstrap seed is built without the instrumentation.

## What it checks

The current Linux compiler stores only filtered source commands at cell **68**, using **four tape cells per executable command**. At the end of the decoder (BF offset 2462), and again after the compiler finishes, the test compares each retained-command cell against the filtered command stream. It also traces the highest and lowest BF tape pointer by phase, counts accesses and writes, and compares every emitted byte with the production native compiler.

Escaped `00` and `FF` are both ignored source bytes and discarded. The checked compiler buffer is compacted command storage, not a raw byte-for-byte source image.

The emitter also temporarily writes retained-command cells and later restores them. A gate that simply banned all those writes would reject the working compiler. The audit deliberately checks phase boundaries, not a false immutability claim.

Run it directly:

```sh
python3 tests/verify_compiler_tape.py
```

Eight executed cases include empty source, nested programs, ignored binary bytes, the full compiler source, and full 16,128-command capacity inputs as well as comment-heavy input. A deliberately wrong expected byte is rejected, so the checker is not just printing PASS. Every resulting ELF is compared byte-for-byte with the native compiler's output. Evidence lives in [`../evidence/compiler_tape_audit.json`](../evidence/compiler_tape_audit.json).

## Results and limits

For the executed maximum-sized sources, the highest observed pointer was **cell 64,601**, leaving **934 cells** above it in the 65,536-cell tape. That is a measured high-water mark, not a license to increase the input ceiling.

This gate establishes useful *execution evidence* for the current Brainfuck compiler implementation. It does **not** prove every possible control path has the same footprint. We still need an ownership map and nonoverlap argument for all four source-buffer lanes, bracket metadata and compiler scratch space. New source transformations require a fresh audit. The source-revision hash and phase offsets are checked against the annotation map rather than silently trusting old offsets.

Iteration 19 scope: the audit now checks the compacted source buffer, not a raw byte-for-byte source image. It is still dynamic evidence only. The authoritative source is **15,559 bytes**.

## Header scratch entry and exit checks — Iteration 20

The audit-only interpreter now checks that BF offsets 2848 and 4277 both execute exactly once with pointer 60 and cell 61 equal to zero. All eight existing witnesses pass. This checks the preconditions used by the separate static header verification at [`HEADER_SCRATCH_SAFETY.md`](HEADER_SCRATCH_SAFETY.md). The observations do not prove those entry conditions for every possible input.

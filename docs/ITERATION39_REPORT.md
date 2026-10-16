# Iteration 39 — Windows source-dependent PE32+ emitter

## Implemented

Added `experiments/windows_linear_pe_64.bf` (**10,831** executable Brainfuck commands), native Linux-built stage, and transport adapter `bootstrap/run_windows_linear.py`. This program compiles up to **64** filtered `+ - > <` Brainfuck commands into a PE32+ Windows x64 console executable. It constructs the headers, executable instructions, import directory and tape section in Brainfuck. Development-only `tools/author_windows_linear.py` created the saved BF source; Python does **not** produce or patch PE/machine code during the tested compiler path. The preexisting BF scanner owns source filtering. Older fixed Windows seed stays intact.

## Source compliance and execution semantics

Only original eight Brainfuck operations execute in the compiler's `.bf` file, with safe ignored comments. The bounded target implements 65,536 zero-initialized 8-bit tape cells, wrapping arithmetic, initial cell zero, and checked pointer movement. The generated x64 target traps out-of-bounds with `UD2`; Windows exception process status is not verified. Loops and byte I/O are rejected instead of silently miscompiled. Three PE sections are `.text` RX, `.idata` RW, and `.tape` zero-initialized RW. The image is **2,048 bytes**.

## Correctness and safety

The focused verifier passed **87** instruction-stream program cases, **five** independent Brainfuck-interpreter comparisons for the compiler source, **60** expected pointer-boundary trap cases from the independent oracle, **seven** unsupported/oversized rejections and **three** existing-file preservation tests. Independent `objdump` recognizes PE32+, the Win32 import and expected x64 instruction encodings. No native Windows loader execution occurred, so these are **Linux-executed Brainfuck-emission tests with PE structural and x64-instruction verification**, not Windows target conformance proof.

## Self-hosting

The unchanged canonical Linux BF compiler successfully recompiled its full source twice (Stage 1 and Stage 2): both outputs were byte-identical to the installed **475,703-byte** ELF. Independent cold Stage 0 was not rerun. Android archived bounded S2 remains as in Iteration 38; no fresh Android device run was done. Windows has **no native compiler execution or self-hosting proof**.

## Dependencies and limits

The Linux BF compiler runs the standard-BF Windows emitter. Python transports BF-owned source and artifact bytes, checks status and writes output files atomically; tests use Python, GNU `objdump`, and an independent BF interpreter. No C/Rust/LLVM code generator is used in production. No Windows x64 runtime was present. The four-instruction subset, fixed image and 64-command cap are prototype boundaries, not universal Windows support. The Android 300,000-command target remains open.

## Pending device acceptance

Four BF-emitted Windows executable fixtures and a hash-checking PowerShell smoke runner are prepared in `build/windows39_acceptance/`. They have **not** run under Windows, and their runtime exit statuses are unverified. See the command in [`WINDOWS_LINEAR_PE.md`](WINDOWS_LINEAR_PE.md).

## Next priority

Acquire Windows target execution evidence and implement Win32 byte I/O entirely through BF-owned machine-code generation; then bracket relocation, scalable PE layout and Windows-native S2. If runtime remains unavailable, progress the next BF-owned component without reporting Windows execution.

Detailed contract: [`WINDOWS_LINEAR_PE.md`](WINDOWS_LINEAR_PE.md). Evidence: [`../evidence/iteration39_windows_linear_pe.json`](../evidence/iteration39_windows_linear_pe.json).

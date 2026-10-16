# windows_x64_loop_rel32.bf — Iteration 41 BF stage notes

**Authoritative standard-BF source:** [`windows_x64_loop_rel32.bf`](windows_x64_loop_rel32.bf).

- Brainfuck instruction count: **1,738**.
- Source SHA-256: `fb0ff203630242ea344e4c5c12c3899af4c471107b743b40776c8d4ce61f07d5`.
- Filtered instruction SHA-256: `7a454925d6927777b2274e637cfe9b6be601705a2230d8c876b3bcb5adf035e5`.
- Linux native ELF: [`../build/windows_x64_loop_rel32_x86_64_linux.elf`](../build/windows_x64_loop_rel32_x86_64_linux.elf).
- Native ELF SHA-256: `9ef80090a362c06628887f1ec4aa6862ab2206bd67180fe631fb61d77ec43c41`.

This module is written as raw Brainfuck with safe ignored comments. The development-only Python authoring script generated the saved Brainfuck instruction stream. In production the actual BF executable owns native code generation; the Python transport does not calculate x64 instruction displacements or patch machine code.

The complete input/output contract, byte positions, trust conditions, slot size and safety boundary are in the [Windows all-eight-command contract](../docs/WINDOWS_FULL64_PE.md). Windows loader and native compiler execution are **NOT RUN**.

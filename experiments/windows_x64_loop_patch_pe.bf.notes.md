# windows_x64_loop_patch_pe.bf — Iteration 41 BF stage notes

**Authoritative standard-BF source:** [`windows_x64_loop_patch_pe.bf`](windows_x64_loop_patch_pe.bf).

- Brainfuck instruction count: **5,364**.
- Source SHA-256: `a1de797099e810302effc790b17d0d05ae5fe6c11ffb62758d1c4564553a3842`.
- Filtered instruction SHA-256: `d189e42c376c20921147a18d2233e0dffdd07b6b7d66e6aaeffdf808feb132c2`.
- Linux native ELF: [`../build/windows_x64_loop_patch_pe_x86_64_linux.elf`](../build/windows_x64_loop_patch_pe_x86_64_linux.elf).
- Native ELF SHA-256: `1959d6d25fd4a7ed1e66916bfb71df323a116c3185582ec9d767cab379eee454`.

This module is written as raw Brainfuck with safe ignored comments. The development-only Python authoring script generated the saved Brainfuck instruction stream. In production the actual BF executable owns native code generation; the Python transport does not calculate x64 instruction displacements or patch machine code.

The complete input/output contract, byte positions, trust conditions, slot size and safety boundary are in the [Windows all-eight-command contract](../docs/WINDOWS_FULL64_PE.md). Windows loader and native compiler execution are **NOT RUN**.

# windows_loop_slots_pe_64.bf — Iteration 41 BF stage notes

**Authoritative standard-BF source:** [`windows_loop_slots_pe_64.bf`](windows_loop_slots_pe_64.bf).

- Brainfuck instruction count: **11,120**.
- Source SHA-256: `a74d5d31bfe3a44ea6d7efd984bc45148dd3a2cd32bd70f5adc756380cfa8bb4`.
- Filtered instruction SHA-256: `fa5677ff351495651d0831d5b89046da71850eee40243e99426a605a857515ee`.
- Linux native ELF: [`../build/windows_loop_slots_pe_64_seed_x86_64_linux.elf`](../build/windows_loop_slots_pe_64_seed_x86_64_linux.elf).
- Native ELF SHA-256: `2214805ff54c077149f823f5ed2750fc9317c8c75b9c684a017ae0226fbfee6d`.

This module is written as raw Brainfuck with safe ignored comments. The development-only Python authoring script generated the saved Brainfuck instruction stream. In production the actual BF executable owns native code generation; the Python transport does not calculate x64 instruction displacements or patch machine code.

The complete input/output contract, byte positions, trust conditions, slot size and safety boundary are in the [Windows all-eight-command contract](../docs/WINDOWS_FULL64_PE.md). Windows loader and native compiler execution are **NOT RUN**.

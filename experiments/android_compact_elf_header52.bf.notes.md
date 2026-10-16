# android_compact_elf_header52: Iteration 52 stage

Standard Brainfuck instructions: **3545**.

Source SHA-256: `64db9a0a6abcc82934cdcc9b594995693829e71f77d1e095c0d987cb477d4b76`.

Compiled Linux native stage SHA-256: `b8b7aaef230d15982a4205fbaf7e3af4c46a418277fdac1fee3233e51af962a9`.

This stage is executed on Linux as part of the dynamically sized compact AArch64 ELF pipeline. The source-authoring Python tool is development-only. Production branch and ELF decisions are BF-owned. Linux-hosted structural and instruction-simulator tests passed; the resulting image has not been Android loader-executed. See [the Iteration 52 pipeline contract](../docs/ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

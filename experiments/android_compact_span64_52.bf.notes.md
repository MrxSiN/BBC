# android_compact_span64_52: Iteration 52 stage

Standard Brainfuck instructions: **7538**.

Source SHA-256: `882cf6bf9122241d408f2fc3030e4ce34d10ddd2efc7dd13741eb1315aabc499`.

Compiled Linux native stage SHA-256: `8f6e09b4501404c90994a7035b75b893407c46f4af2dd6038cc6abddb17be575`.

This stage is executed on Linux as part of the dynamically sized compact AArch64 ELF pipeline. The source-authoring Python tool is development-only. Production branch and ELF decisions are BF-owned. Linux-hosted structural and instruction-simulator tests passed; the resulting image has not been Android loader-executed. See [the Iteration 52 pipeline contract](../docs/ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

# android_compact_elf_word_plus7_52: Iteration 52 stage

Standard Brainfuck instructions: **15526**.

Source SHA-256: `eed16c3429437b427c6c0de9dbb296f3620eccf9cce2eb33d23ce6aead5f3170`.

Compiled Linux native stage SHA-256: `cad37cf8a3d29d9f089585c5bb28daab15c3ddae8f26a6f8443d856adaf3539b`.

This stage is executed on Linux as part of the dynamically sized compact AArch64 ELF pipeline. The source-authoring Python tool is development-only. Production branch and ELF decisions are BF-owned. Linux-hosted structural and instruction-simulator tests passed; the resulting image has not been Android loader-executed. See [the Iteration 52 pipeline contract](../docs/ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

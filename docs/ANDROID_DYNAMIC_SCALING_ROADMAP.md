# Iteration 52: experimental dynamic AArch64 ELF code generation

Full all-eight-instruction AArch64 ELF generation now works in a resource-growing Linux-hosted standard-BF pipeline. **55 ELF programs passed 110 simulated runs**; one synthetic 296,307-command source produced an ELF accepted by `readelf`. None of the original eleven policy programs have been compiled with this route, and Android-native loading/JNI/DSO and long-branch veneers are unverified/unimplemented. The historical 2,719-command bound applies to the **legacy** image generator, not the new experimental path. [Contract](ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

---

# Android Brainfuck — resource scaled compiler roadmap

## Design decision

Do not set another arbitrary command-count tier. Allow source and generated artifacts to grow through chunked I/O and out-of-core storage, with explicit resource budgets, 64-bit file offsets, checked arithmetic and deterministic errors. Resource-bounded is not resource-unlimited.

## Verified now

1. Source analysis over 100 million commands, including a long bracket span, in Linux-executed standard Brainfuck stages (historical)
2. Dynamic streaming of raw AArch64 slots for six linear BF commands with a tested 300,001-command program (Iteration 49)
3. Historic Android-native bounded S2, distinct from universal backend acceptance

## Next evidence gated implementation work

1. **Loop storage** — replace the BF pairer's fixed 255-depth stack with BF-controlled external random-access storage, with typed generic host byte transport only; validate deep nesting without changing eight-instruction semantics
2. **Code offsets** — BF-owned 64-bit generated code offsets and source-to-code relocation records, including short and long AArch64 branches
3. **Compact native emission** — remove the 48-byte-per-command slot requirement; implement BF-safe run folding, semantic preservation and bounded optimizer resource use
4. **Dynamic ELF and DSO** — BF-owned output size/layout, ELF page alignment, relocations and PIE startup; support library entry ABI for JNI use, with no external machine-code compiler
5. **Real projects** — compile all eleven original BF policy programs (up to 296,307 commands), preserving per-program tape and protocol behavior; run original parity suites and Android APKs
6. **Large program qualification** — compile and execute a nontrivial 100-million-command BF source on actual Android; measure memory, time, output size, relocation coverage and selfhosting stability
7. **Portability** — protect Linux S2 and existing Windows experimental code; tackle broad ABI/platform coverage only with device evidence

None of these future gates are accepted merely because a source stream no longer has a counter cap.

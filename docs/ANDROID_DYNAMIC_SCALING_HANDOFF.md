# Iteration 52: experimental dynamic AArch64 ELF code generation

Full all-eight-instruction AArch64 ELF generation now works in a resource-growing Linux-hosted standard-BF pipeline. **55 ELF programs passed 110 simulated runs**; one synthetic 296,307-command source produced an ELF accepted by `readelf`. None of the original eleven policy programs have been compiled with this route, and Android-native loading/JNI/DSO and long-branch veneers are unverified/unimplemented. The historical 2,719-command bound applies to the **legacy** image generator, not the new experimental path. [Contract](ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

---

# Iteration 51 Android integration checkpoint

[The current integrated code/pair stream](ITERATION51_COMPACT_AARCH64_RELOCATION_LEDGER.md) has BF-owned all-eight compact raw machine code, 64-bit native-word offset tracking, and BF-owned bracket matches in disk-backed dynamic storage. The verified output is **unrelocated code plus matched pairs**; branch-word encoding, ELF/DSO layout, Android-native execution, original eleven policy compilation and JNI/APK parity are outstanding. The existing full ELF limit of 2,719 instructions is unchanged.

---

# Android dynamic compiler engineering handoff — Iteration 50

**Objective:** Compile the eleven original Brainfuck policies from GmailHideAds, TwitterHideAds and ThreadsHideAds into verified Android AArch64 native code, and support much larger translation units by available-resource scaling rather than fixed slot-count tiers. Native Android device tests, JNI integration and general compiler self-hosting are release gates, not assumptions.

**Verified in Iteration 50:** compact Brainfuck-owned linear AArch64 byte streaming (one million source commands tested, 12 MB raw output); a Brainfuck-controlled file-backed 8-byte-position bracket stack (4,096 nesting levels tested); a BF bridge from the existing 32-bit scanner; 100-million-range bracket source positions paired. They are still **separate stages** and **do not produce a scalable loop-capable Android ELF**. More detail in [the progress report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md).

The next engineering task is not another arbitrary count threshold. Implement a **single coherent 64-bit source-offset / native-byte-offset stream** with standard-BF ownership of loop metadata and branch displacement, and compose it with a BF-owned dynamic ELF header/segment writer. Preserve atomic error semantics on overflow and resource failure. Consider compact jump veneers rather than relying on the ±128 MiB native AArch64 direct-branch reach. The existing Android ELF/loader proof through 2,719 commands and the archived Android-native S2 proof cannot be relabeled as dynamic 100M compilation.

**Acceptance:** Reproduce the stage tests above, then require a real application fixture beyond 2,719 commands, readelf/PIE checks, instruction-level differential runs, device loader execution, the three repository ABI/JNI parity suites, original policy sources, and repeatable target-native self-hosting before claiming universal Android support.

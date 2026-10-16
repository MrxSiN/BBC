# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Iteration 52: experimental dynamic AArch64 ELF code generation

Full all-eight-instruction AArch64 ELF generation now works in a resource-growing Linux-hosted standard-BF pipeline. **55 ELF programs passed 110 simulated runs**; one synthetic 296,307-command source produced an ELF accepted by `readelf`. None of the original eleven policy programs have been compiled with this route, and Android-native loading/JNI/DSO and long-branch veneers are unverified/unimplemented. The historical 2,719-command bound applies to the **legacy** image generator, not the new experimental path. [Contract](ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

---

# Android application compiler acceptance contract — updated Iteration 59

**Status: PARTIAL POLICY COMPILATION; ORIGINAL APK/JNI ACCEPTANCE OPEN.** This is an audit of the original `.bf` policy sources in three real Android Xposed modules. Three individual callable policy images have been emitted by older bounded BF codegen; no full three-product application acceptance has occurred. The legacy bounded Android PIE path accepted **2,719 commands** (Iteration 45); the historically tested Android-native self-hosted compiler has a separate **16,128-command** input ceiling. The newer resource-scaled BF-owned callable path supports all eight instructions and now emits ELF shared-object metadata with a `bfc_call_v1` export (Iteration 59). Three locally available original policies have structural DSOs. **Actual Android dynamic loading, native JNI execution, full source collection and app parity remain open.**

## Required source workloads

| Product | BF programs | Total BF commands | Largest program | BrainfuckCC target result |
|---|---:|---:|---:|---|
| [GmailHideAds](https://github.com/MrxSiN/GmailHideAds) | 2 | 36,940 | 18,748 | Two dynamic BF-owned callable `.so` images structurally validated; device open |
| [TwitterHideAds](https://github.com/MrxSiN/TwitterHideAds) | 3 | 188,951 | 108,565 | One dynamic BF-owned `action.bf` `.so` compiled; two sources remain |
| [ThreadsHideAds](https://github.com/MrxSiN/ThreadsHideAds) | 6 | 1,087,021 | 296,307 | Uncompiled |
| **Combined** | **11** | **1,312,912** | **296,307** | **3 dynamic callable DSOs structurally verified; full Android/app acceptance open** |

The source counts refer to filtered **`><+-.,[]`** bytes, not raw file lengths. Source files are balanced and their pinned Git blob SHA-1 hashes are in [`../status/ANDROID_APPLICATION_GATES.json`](../status/ANDROID_APPLICATION_GATES.json). The repository revisions and historical source audits live in [`../status/TARGET_WORKLOADS.json`](../status/TARGET_WORKLOADS.json). Counts and ownership were cross-checked using the connected GitHub repositories on 2026-10-13.

The **296,307-command** `ThreadsHideAds/brainfuck/src/nested.bf` makes a 300,000-command compiler limit a very weak milestone. The combined policy set already exceeds **1.3 million commands**. **Current objective (Iteration 59):** the old 100-million-command target has been **retired**. Compilation must scale with available resources, without a fixed command-count ceiling. The 100M source-stage measurements are archived in [the old source-stage contract](ANDROID_100M_CAPACITY.md); they never demonstrated native callable code generation. The [current dynamic callable roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) replaces that historical stretch target.

## What compiling these apps actually means

All three are Android/Xposed projects using Java, JNI/C and Gradle, plus their Brainfuck decision-policy cores. [GmailHideAds](https://github.com/MrxSiN/GmailHideAds) currently uses two BF policies and a separate BF-implemented BF-to-C compiler; [TwitterHideAds](https://github.com/MrxSiN/TwitterHideAds) uses three BF policies; [ThreadsHideAds](https://github.com/MrxSiN/ThreadsHideAds) uses six policies with host capabilities and a stateful `core` program. Their current production flows emit C from BF and compile that with the Android NDK. Our stated requirement is *direct* BF-owned native generation instead of BF-to-C followed by Clang.

The compiler **cannot ingest their Java sources, hook Android methods, or package APKs as standalone BF with its current eight byte-oriented instructions**. The correct architectural division is:

```text
existing .bf policies --> BrainfuckCC native AArch64 backend --> Android shared-library-compatible native machine code
                                                                   |
existing Java/Xposed/DexKit/Gradle host --> declared JNI and framed host capabilities --> instrumented Android APK
```

A **standalone AArch64 shell ELF PIE is not an Android `.so`**. It does not satisfy JNI linking, exported function symbols, dynamic loader relocations, host callbacks, or the established module test suite. An Android linker/packager may assemble host libraries and APKs, but **must not perform the Brainfuck-to-machine-code translation** in the accepted production path. Build all three application packages and record toolchain dependencies separately from BF-native compiler acceptance.

## Nonnegotiable compatibility gates

| Gate | Executable evidence required | State |
|---|---|---|
| A. Source | Compile **all 11 original pinned BF sources**, preserve comments, parse nested loops, reject malformed input deterministically; document compile time, peak RAM, output size | OPEN |
| B. Semantics | Unsigned byte wrapping; per-program tape sizes **32–256**, configured from upstream `programs.json`; clear scratch on request; **Threads `core` persists 64 cells** across requests | OPEN |
| C. Host protocol | Byte-exact framed request/response, EOF behavior, output limits, callbacks and `CAP_CALL` recursion where used; fail open on host errors | OPEN |
| D. Android native library | AArch64 JNI-loadable ET_DYN `.so` or explicitly supported equivalent, real Android loader evidence, correct ABI and exported entry points | PARTIAL — symbol/export and independent linker tested, but Android JNI loader still OPEN |
| E. Product builds | Rebuild **GmailHideAds, TwitterHideAds, ThreadsHideAds** with BF-native policy code; signed/installable APK test builds (keys stay external) | OPEN |
| F. Parity and runtime | Original project's parity and robustness tests; host capability traces; on-device Xposed hooks; memory safety, thread behavior and benchmark evidence | OPEN |
| G. Resource-scaled callable compilation | No arbitrary source/IR/loop-nesting caps; BF-owned native callable code/relocation; meaningful growing program tests with measured resources | PARTIAL — all eight commands with dynamic loops and DSO structurally verified, Android runtime still OPEN |

The original projects have different host contracts. Gmail/Twitter use framed requests and short-lived zero-initialized tapes. Threads uses a richer capability protocol and nested `CAP_CALL` across the six compiled programs; the `core` policy has persistent cells. Never normalize these differences away merely to pass a compiler test. References: [`../status/ANDROID_APPLICATION_GATES.json`](../status/ANDROID_APPLICATION_GATES.json), the three upstream `brainfuck/programs.json` files and their architecture/ABI documents.

## Engineering sequence and stop conditions

1. Replace fixed 48-byte command slots with **streaming compact BF-owned IR and native emission**, using at least 32-bit command/byte offsets, checked arithmetic, file-size and resource boundaries. Build the actual eleven-file corpus as the first benchmark. Keep old 2,719-command path as regression reference.
2. Scale bracket stack/relocations and ELF layout beyond 300,000; meet each source's compile-and-execute acceptance before chasing a synthetic 10-million ceiling.
3. Build a **shared-library target**: PIC, ELF dynamic metadata, SONAME/imports/exports/relocations as required, Android loader and JNI entry contracts. Keep target API level explicit.
4. Integrate the existing Java/C host adapter strictly as a disclosed platform dependency; preserve `programs.json` tape policy, framed protocols, Threads state and capability recursion, and error/fail-open paths.
5. Run the upstream parity suites with **native BF output** substituted for generated C. Then build, install and test each APK on supported hardware (or explicitly identified compatible emulator).
6. Extend source ingestion, file-backed IR, loop nesting, relocation and callable output based on available resources and checked representable offsets; test real growing workloads without an arbitrary command-count benchmark. Profile runtime, compiler memory, storage and output size; no blanket C/Rust superiority claim.

**Acceptance definition:** A source parse or AArch64 shell binary alone does not count. The minimum user-requested milestone is all **three installed module APKs with native BF-compiled policy kernels passing target-device parity tests**. Complete elimination of Java/Android host code is *not* a capability of ordinary Brainfuck; it would require a separate explicit host protocol and is not claimed here.

## Reproduce source audit

```bash
python3 tests/verify_android_app_acceptance.py
python3 tests/verify_android_app_acceptance.py --checkouts /path/to/clones
```

The optional checkout root contains folders `GmailHideAds`, `TwitterHideAds`, `ThreadsHideAds` checked out at the pinned upstream commits. The script verifies raw bytes, filtered instruction counts, Git blob IDs, nesting, and `programs.json` tape sizes. It does **not** call the compiler or prove app compatibility. For real compiler acceptance, publish separate executable build and test evidence for every gate.

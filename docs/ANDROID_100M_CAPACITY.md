# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Iteration 49 — resource scaled native code streaming

A new [standard BF native slot stage](../experiments/android_streaming_linear_slots.bf.notes.md) reads arbitrary raw source bytes and emits AArch64 linear instruction slots as a stream with **no built in source command count ceiling**. A 300,001-command program generated 14,400,048 native bytes and matched existing BF-owned templates. The host only frames and copies bytes, with optional caller supplied output quotas; it does not parse BF or emit instructions. **Not a runnable ELF:** brackets, scalable relocation, dynamic executable layout, JNI and the eleven real application policies remain open. The complete Android ELF backend still supports only 2,719 commands. [Report](ITERATION49_DYNAMIC_ANDROID_STREAMING.md) and [evidence](../evidence/iteration49_android_dynamic_stream.json). The 100M benchmark remains a target, not an artificial maximum or a completed native executable. Earlier iteration notes remain historical.

# Android 100 million command target

**Status: 100M source scanning and 32-bit pairing executed on Linux; 100M native compiler NOT implemented.**

The goal is now **at least 100,000,000 executable Brainfuck instructions per single source file**, not merely 100 million across several project modules. Multiple units exceeding 100 million aggregate must also remain supported. This supersedes the earlier 10M-per-unit stretch goal without changing historical reports.

## Verified stage

The new [32-bit BF-owned source analyzer](../experiments/android_100m_rle_scan.bf.notes.md) processes real 100MB raw input using generic run-length transport and correctly emits 32-bit filtered-command counts and optional bracket positions. On Linux, it passed small-source differential tests and synthetic high-range cases. The compressed-input test **is not native compilation of 100 million commands**, and is not evidence of uniform throughput for diverse input.

The existing AArch64 native-code emitter remains bounded to 2,719 commands; the separately demonstrated Android-native compiler remains bounded to 16,128 input commands. Neither can compile the eleven pinned application policies. Current universal-compiler maturity is **UNIMPLEMENTED** beyond source-analysis primitives.

## Additional verified loop-pairing stage

The [new standard-BF 32-bit pairing stage](../experiments/android_100m_bracket_pairs.bf.notes.md) matches 100-million-range opening and closing offsets in a framed scanner byte stream. It was tested on a real 100,000,002-byte source, but its stack has a documented **255-loop nesting maximum**. A separate BF scanner fork writes the necessary zero event delimiter; the original source stage retains its old response format. Pairing a source offset is not relocating a native instruction; AArch64 branch encoding and source-to-native offset mapping remain open. [Iteration 48 evidence](../evidence/iteration48_android_100m_pairing.json).

## Required architecture for true 100M native compilation

1. **BF-only frontend:** Filter raw source, retain 32-bit source indexes, support nested bracket matching and recover invalid inputs, while bounding source, stack, and artifact resources.
2. **Streaming compact IR:** Eliminate the fixed 48-byte machine-code slot per BF instruction as an obligatory frontend representation. Process bounded chunks, store compact loop metadata on disk or in documented compiler-controlled memory through byte transport, and preserve source semantics.
3. **BF-only relocation and AArch64 emitter:** Use 64-bit artifact-size arithmetic where needed. AArch64 direct branch immediates have finite range; add bounded, verified branch veneers or layout planning for long spans.
4. **Android ELF output:** Generate correctly aligned and loadable PIE or shared-library ET_DYN artifacts with non-overlapping RX/RW segments, safe tape placement, and observable deterministic resource exhaustion. Do not assume a 4.8GB file (100M times 48 bytes) is a practical delivery format.
5. **Application integration:** Generate ABI-compatible native kernels for all 11 policies of GmailHideAds, TwitterHideAds and ThreadsHideAds, with their existing per-program tape and persistence contracts. Preserve external JNI/Xposed/Gradle dependencies; do not disguise them as a ninth BF instruction.
6. **S2 and release gates:** Compile and execute nontrivial 100M-unit programs, verify all output and bounds behavior on Android, then compile the full BF compiler source with a native Android compiler and compare repeated stages. Publish time, peak memory, generated code bytes, hashes and independent reference results.

## Acceptance ladder (all are distinct)

| Capability | Verification | Current status |
| --- | --- | --- |
| 100M raw-byte transport and BF source analysis | Full raw-file test with lossless compression | EXECUTED on Linux |
| 32-bit bracket occurrence offsets across 100M | BF-produced event positions | EXECUTED on Linux |
| 100M-range bracket pairing | BF-owned 32-bit matched opening and closing offsets | EXECUTED on Linux; maximum nesting 255 |
| 100M native branch relocation | BF-owned source-to-code mapping and native branch displacements | UNIMPLEMENTED |
| 100M native AArch64 executable generation | Compile a real 100M-command unit to runnable Android code | UNIMPLEMENTED |
| All 11 application policy kernels | Native code, parity, ABI and JNI acceptance | UNIMPLEMENTED |
| Working Android APKs | Real device install and complete module tests | UNIMPLEMENTED |
| 100M native compiler self-hosting | Full target-side compiler self-compilation with hashes | UNIMPLEMENTED |

Source-stage evidence: [`../evidence/iteration47_android_100m_source.json`](../evidence/iteration47_android_100m_source.json). Existing real-app acceptance: [Android application contract](ANDROID_APPLICATION_ACCEPTANCE.md).

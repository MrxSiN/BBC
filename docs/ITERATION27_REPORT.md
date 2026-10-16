# Iteration 27 engineering report — partial source capacity gate

**Date:** 2026-10-13  
**Milestone status:** **PARTIAL**, not closed.  
**Next priority:** Complete BF-owned multi-byte bracket tracking and scalable AArch64 emitter/relocation path. No Windows implementation work yet.

## Implemented

- Added [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf): **1,170 standard BF commands** plus comments containing no BF instruction characters. It emits the filtered command stream, a 24-bit little-endian emitted-command count and one final status byte. No host filters source or counts its Brainfuck commands.
- Added BF-only marker/carry/overflow state in tape cells 7–14. A separately instrumented BF variant exercises the top-byte overflow instead of sending 16 million commands.
- Added opt-in `--scanner` to [`../bootstrap/run_android_loops.py`](../bootstrap/run_android_loops.py). This only decodes the scanner's output frame and feeds the existing BF-owned downstream stages. The old default filter is preserved, and final output remains an atomically installed AArch64 ELF image.
- Added scanner regression tests, stage integration parity tests, source annotations, status matrix entry, roadmap progress and architecture/safety/target notes.

## Source compliance

The compiler remains entirely standard Brainfuck. Canonical Linux [`../compiler/core.bf`](../compiler/core.bf) remains **15,559 bytes / 14,859 executable commands** with unchanged SHA-256 `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`. Its 475,703-byte ELF SHA-256 remains `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8`. The new BF scanner SHA-256 is `c9a6b7c9d3e4f17f0802fa64b382cc5bfda37027aaf6ee277cc1432787b18bf2`; its Linux native executable SHA-256 is `3f3a5a216c386e5cf051c2f67ab261f6cadc6c5250ce75e35b0d758cd2d9f06f`.

## Self-hosting

The original Linux S2 bootstrap evidence from Iteration 26 remains in the archive, and the authoritative compiler source/binary hashes were checked unchanged. A **fresh two-stage native recompile was attempted but did not complete within the execution limit** in this development pass; it is **NOT VERIFIED for Iteration 27**. No cold Stage 0 or newly compiled Android/Windows-native compiler was tested.

## Correctness and source capacity

- **37 scanner fixtures:** output command bytes and reported counts agreed with the independent Python oracle, including 16,128; 16,129; 65,535; 65,536; 300,000 and **300,001** executable commands. The test program printed PASS and wrote [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json); its invoking command subsequently reached an outer execution timeout. The evidence data and generated ELF remain inspectable.
- **6** malformed wire cases rejected. **6** BF-seed comparisons (two independently implemented C interpreters) agreed on short scanner programs. Instrumented 24-bit overflow returned status **2**; an unmodified scanner was not exercised by a 16,777,216-command stream.
- **9** bounded programs produced byte-identical AArch64 images using old vs. opt-in scanner mode, and **4** invalid programs rejected in both modes. Atomic output preservation passed the opt-in CLI test. See [`../evidence/iteration27_scan_integration.json`](../evidence/iteration27_scan_integration.json).
- `tests/verify_android_contract_v1.py`, `tests/verify_source_comments.py`, `tests/verify_target_workloads.py`, and `tools/check_docs.py` passed. Other full release tests and device execution were not rerun.

## Memory safety and performance

Scanner state is within tape cells **0–14** on the 65,536-cell V0 tape, with dedicated counter carry and overflow sentinel. Source comment invariance, malformed framing and multiple carry thresholds are executed, not formal proofs. Whole-compiler scratch ownership, arbitrary large source indexing, dynamic ELF output bounds and Android-loader safety remain unverified. Individual local test wall times are recorded in source scan evidence; **no statistically controlled native C/Rust performance comparison** was made this iteration.

## Dependencies and platforms

Linux native BF compiler performs the actual Brainfuck-to-machine-code compilation of the scanner; Python runs test oracles, transport and file placement; two C Brainfuck seed interpreters provide independent interpretation only. None generate Android machine instructions. **Linux-hosted scanner: EXECUTED. Android generated program pipeline: old ten-command limit; nine locally identical image checks, no fresh Android-device execution. Android native compiler/self-hosting: UNIMPLEMENTED. Windows PE32+ and native self-hosting: UNIMPLEMENTED.**

## Remaining acceptance blocker

Iteration 27 is **not complete**: emitting **300,001 filtered source commands** is different from emitting and running the corresponding **AArch64 native executable**. Bracket relocation, branch distances, emitted image size and multi-pass output are still limited by the ten-command downstream stages. The next BF-owned implementation should begin general position/span metadata with multi-byte counters, and must not outsource source-specific indexing or relocation to Python.

The Android-first / Windows-second **22-iteration baseline** remains planning only. Failure to close a gate may require contingency iterations; it does not justify silently marking the milestone complete.

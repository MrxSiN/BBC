# Documentation reconciliation D0 — 2026-10-13

**Historical D0 report.** Iteration 26 subsequently adopted [`ANDROID_COMPILER_PROTOCOL_V1.md`](ANDROID_COMPILER_PROTOCOL_V1.md) and ran a new hosted regression suite. The next implementation step is Iteration 27; this D0 record describes the documentation-only state *before* that work.

## Scope

This pass updates the maintained project guidance **before any compiler implementation change**. The uploaded `Brainfuck Compiler.md` and tracked `docs/PROJECT_REQUIREMENTS.md` are byte-identical (SHA-256 `f06653e0225b95ffffe65ac55a97ef1e9f95f338bf2deb03856689156b75d59e`). Historical iteration and benchmark evidence is preserved rather than edited to fit a plan.

## Changes

- Rewrote `README.md`, `docs/STATE.md`, `docs/TARGETS.md`, `docs/HANDOFF.md` and `docs/OPEN_ISSUES.md` to state the *latest archive evidence*: Linux S2; Android native generated-program execution on Pixel 8 Pro; **no Android native compiler or native self-hosting**; Windows PE32+ unimplemented.
- Added [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) and planning-only [`../status/ROADMAP.json`](../status/ROADMAP.json): **22 baseline** post-D0 iterations, Android 26–39, Windows 40–45, shared 46–47, contingency 28–34. The next development step is **Iteration 26**, not a retroactively invented iteration.
- Added [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md), keeping "universal V0 Brainfuck on Android `arm64-v8a` shell" distinct from all Android ABIs, APK integration, host services, incompatible execution profiles and unlimited input.
- Updated `AGENT.md` and `CLAUDE.md` to make the plan, existing evidence boundaries, source-purity requirement and documentation style explicit.
- Added current-status disclaimers to `docs/ARCHITECTURE.md`, `docs/ANDROID_AARCH64_PROTOTYPE.md`, `docs/ANDROID_NATIVE_OPTIMIZATION.md`, `docs/ANDROID_DEVICE_BENCHMARK.md`, `docs/BENCHMARKS.md`, `docs/SELF_HOSTING.md` and `docs/TARGET_WORKLOADS.md`. Older chronological claims about lack of Android execution now remain *historical*, not contradictory current-state claims.
- Appended the Android-first planning decision to `docs/DECISIONS.md` without changing past decisions.
- Left normative V0 specifications, specialized historical notes, self-hosting evidence and existing machine-readable conformance results unchanged. Current feature claims are not inferred from this roadmap.

## Verification performed in this documentation environment

| Check | Result |
|---|---|
| `python3 tools/check_docs.py` | **PASS**: 40 maintained Markdown files after this report was added, local links, source count, annotations and installed native ELF size |
| `python3 tests/verify_source_comments.py` | **PASS**: safe annotations, negative cases and interpreter invariance |
| `python3 tests/verify_target_workloads.py` | **PASS**: four repos, 12 sources tracked, 11 documented capacity failures |
| `python3 tests/verify_native_benchmark_contract.py` | **PASS**: 20 cross-checked BF-native/C outputs from two workloads and five byte inputs |
| Roadmap data check | **PASS**: exactly 22 uniquely numbered planned iterations, 26 through 47 |
| Canonical `.bf` SHA-256 | **UNCHANGED**: `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9` |
| Linux native compiler ELF SHA-256 | **UNCHANGED**: `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8` |
| Original project requirements hash | **UNCHANGED** |
| Full `sh tools/verify_release.sh` | **NOT RERUN** as a full gate in this documentation-only pass |
| Android native device tests / Windows compiler tests | **NOT RERUN**; hardware/target test environments not part of this pass |

The original ZIP does not preserve Unix executable bits on extracted ELF files. To execute the existing Linux native compiler in this test environment, its extracted file mode was corrected (`chmod u+x build/compiler_x86_64_linux.elf`); **ELF bytes and hash were not changed**. The repackaged Linux compiler retains its executable permission.

## Success condition and next action

Documentation is now aligned on the true present limit: the next development work is source-capacity architecture and versioned native Android compilation contracts, **not** Windows implementation yet, and not claiming an Android compiler from an Android-executed demo. Continue Iteration 26 using [`HANDOFF.md`](HANDOFF.md). A feature becomes supported only after the evidence-gated work and target-side runs in [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md).

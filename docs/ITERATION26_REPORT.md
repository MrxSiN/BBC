# Iteration 26 — Android-first compiler contract and regression report

**Date:** 2026-10-13  
**Result:** **Contract and hosted test milestone ACCEPTED**; scalable Android implementation **NOT STARTED**. The general release/cold-bootstrap gate remains incomplete. The next BF implementation iteration is **27**.

## Implemented

- Adopted the [Android V1 compiler input/output, loader and capacity contract](ANDROID_COMPILER_PROTOCOL_V1.md). The chosen multi-pass BF-owned streaming strategy must be proven with real BF source in Iteration 27 onward; this iteration does not falsely count an architecture as a compiler.
- Added [`tests/verify_android_contract_v1.py`](../tests/verify_android_contract_v1.py) and [`tests/verify_iteration26_native_stages.py`](../tests/verify_iteration26_native_stages.py). Added both to `tools/verify_release.sh` for future regression runs.
- Added stage/source evidence [`iteration26_contract.json`](../evidence/iteration26_contract.json), native-stage evidence [`iteration26_native_stages.json`](../evidence/iteration26_native_stages.json), synchronized `status/ROADMAP.json` and `status/CONFORMANCE_MATRIX.json`, and updated README, handoff, targets, decisions and issue list.
- **No edits to `compiler/core.bf` or any existing Android `.bf` stage.** No code-generation capability or large-source support was added. This is an intentionally bounded contract-first iteration.

## Provenance

| Input | SHA-256 |
|---|---|
| `compiler/core.bf` | `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9` |
| `build/compiler_x86_64_linux.elf` | `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8` |
| `docs/PROJECT_REQUIREMENTS.md` | `f06653e0225b95ffffe65ac55a97ef1e9f95f338bf2deb03856689156b75d59e` |

All three match the documentation-D0 starting archive. The existing authoritative BF source is 15,559 raw bytes / 14,859 commands. The ELF remains 475,703 bytes.

## Tests run on this host

| Gate | Result | Evidence boundary |
|---|---|---|
| `python3 tests/verify_android_contract_v1.py` | **PASS** | Eight BF-stage source/binary hash pairs, 256 raw source bytes, six bad wire escapes, nine Android ELF outputs, 14 AArch64 load-bias simulator/reference differential cases, six malformed or 11-plus-command rejections, 1 MiB transport cap, atomic-output preservation |
| `python3 tests/verify_iteration26_native_stages.py` | **PASS** | Installed Linux BF compiler emits Stage 1; newly emitted Stage 1 runs and emits byte-identical Stage 2. Not independent Stage 0 |
| `python3 tests/verify_android_optimized_adapter.py` | **PASS** | Comment invariance and two atomic-failure checks |
| `python3 tests/verify_target_workloads.py` | **PASS** | Four repositories, twelve BF sources tracked, eleven oversized-for-current-compiler workload observations |
| `python3 tests/verify_source_comments.py` | **PASS** | Four valid annotations, seven rejected unsafe cases, ten source-comment equivalence checks |
| `python3 tests/verify.py` | **PASS** | 178 of 178 Linux compiler semantic cases |
| `python3 tools/annotate.py --check` | **PASS** | Source purity, annotations, hashes |
| `python3 tools/check_docs.py` | **PASS** | Maintained docs, links, source count and ELF size |
| `sh tools/verify_release.sh` | **INCOMPLETE** | Stopped during the expensive compiler-tape audit. Never label the complete gate as passed |
| Full filter-integration and native-emission suites | **INCOMPLETE** | Each exceeded the local test execution budget |
| Android/Windows target-side compiler and self-hosting | **NOT RUN** | No corresponding OS/device execution environment used; Android compiler still unimplemented |

Tests use Python only for transport and **independent oracles**. BF-specific parsing, native instruction generation, relocation and ELF emission in the exercised experimental pipeline remain the existing `.bf` stages. AArch64 simulator outcomes are **not** Android-native execution. Cold seed Stage 0 is historical evidence, not freshly verified here. No new benchmarks were taken.

## Capabilities and limitations

- Linux native compiler: authoritative BF-only S2 remains backed by original archived Stage 0→2 evidence and fresh native Stage 1→2 equivalence. Full release auditing not completed in this turn.
- Android: the generated executable pipeline is still **ten-command-limited**; earlier device execution remains historical. Android-native compiler and Android-native self-hosting are **UNIMPLEMENTED**. The new planned source limit of 300,000 is **not reached**.
- Windows: PE32+ BF compiler, generated program execution and native self-hosting are all **UNIMPLEMENTED**.
- Optimizations: no new transformations, safety claims or speed measurements. The current Android microbenchmark still does not establish being fastest.
- Memory safety: no compiler tape-overlap proof; existing checked-pointer/negative witnesses are not a formal proof. No new BF execution profile was introduced.

## Next highest-priority change

**Iteration 27:** Write and execute an ordinary Brainfuck streaming command counter with bounded multi-byte index arithmetic, deterministic resource exhaustion and validated tape ownership. Test the ten-command old ceiling and the 16,128/16,129 boundary first, then step toward the 300,000-command acceptance target. Keep the existing BF source, Linux S2 and Android prototype fully reproducible. Verify cold bootstrap and expensive gates before any release promotion.

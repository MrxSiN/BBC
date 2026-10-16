# Iteration 65 — Disk backed patch index acceptance

Removed the active 64 bit relocation adapter's growing Python set of patch addresses. Duplicate patch detection now uses a one bit per native word sparse temporary file, while BF continues to calculate and emit relocations. Five prior iteration DSOs reproduce byte for byte, 12,000 loop pairs compile, and fail closed duplicate rejection is tested. Real Android Bionic/ART/APK device acceptance and native dynamic compiler self hosting are still open. [Report](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md). No artificial command count goal returns.

---

# Iteration 64 — BF-native AArch64 code integrity postflight

The dynamic DSO transport now validates not just BF-generated ELF metadata but the entire BFP1 code stream, exact native operator templates, and forward/backward signed-64-bit nested-loop relocation targets before an atomic publish. No native code or BF syntax is implemented in Python. 52 new BF outputs, 104 simulator/reference comparisons, seven native mutations, two injected atomic rollbacks, and 13 previous shared libraries passed local validation; Android Bionic/ART/APK runtime execution is still open. Legacy paths remain fallbacks. [Iteration 64 report](ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md).

---

# Iteration 63 — Fail-closed BF DSO publication

`bootstrap.android_dynamic_callable59` now rejects invalid BF-produced ELF64 metadata before the output file is atomically installed. The independent structural check uses constant prefix memory and does not emit ELF fields or native code. Local executed evidence: 240 BF programs, 960 AArch64/reference comparisons, 40 corrupted headers, four length mismatches, injected BF-header corruption with preserved existing artifact and a sparse 64-bit length test. Bionic loading and real Android ART/JNI remain unverified. Continue with target-side tests and original application-policy parity; retain legacy fallbacks until native Android self-hosting. [Full details](ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md).

---

# Active Android callable compiler roadmap — resource scaled

## Scope

This replaces the old synthetic 100-million-command development target. Implement one production-oriented standard-Brainfuck compiler path that grows with required source, IR, branch metadata and executable size. No artificially selected command count or nesting threshold qualifies as universal support.

The Iteration 58 path compiles **all eight original Brainfuck instructions**, including nested loops and signed-64-bit BF-owned branch relocation, and retains BF-owned 64-bit ELF size calculations. Iteration 59 additionally emits BF-generated ELF DSO exports for `bfc_call_v1` with dynsym/dynstr/hash and ELF section metadata. Independent AArch64 linking and host-Linux JNI transport tests passed, **not Android loader/JNI execution**. Iteration 60 adds nine BF-generated DSO fixtures, a device-targeted native `dlopen` test, and zero-length-safe JNI buffer handling; fixture simulator and host Linux checks passed, but no arm64 Android device/NDK is available here. Iteration 61 adds a device-side ART `app_process` + Java/JNI acceptance driver covering the same nine policies, with Linux JVM/test-only-C-stub and mocked-ADB verification; actual Android ART/JNI execution remains unverified. The older callable IR backend (4,096 records, depth 255) and the old freestanding dynamic ELF backend remain **temporary verification fallbacks** until the new path can replace them without losing correctness or on-device compatibility. Historical 100M scan experiments are retained as archived test data, not goals.

Iteration 62 now adds an installable debuggable APK device gate (`tools/android_bfp1_bridge/apk_acceptance62.py --device`) which loads nine unchanged BF-produced DSOs in the app native-library namespace. The shared Java/JNI assertions pass Linux host C-stub tests and simulated device transport guards; **no Android device or Gradle build is available**, so the app namespace remains unverified. Keep the shell ART route separately testable.

## Integration gates

1. **Dynamic brackets and indexed IR — implemented, simulator verified:** BF-owned bracket pairing uses file-backed opaque records; BF emits native word positions and 64-bit relative literals. Check physical Android execution and out-of-core resource failure behavior.
2. **Callable eight-operator semantics — simulator verified:** nested loops, loop budget, checked pointer moves, modulo arithmetic, EOF-zero and output quota validated on 354 simulator cases. Verify full hardware ABI, actual Android pointer trap outcomes, and large-range branch execution.
3. **All actual application policies — three local sources compiled:** compile the other eight pinned Twitter/Threads sources, verify original source hashes, measure real resources and keep their host protocol/tape requirements distinct. No standalone shell ELF qualifies as a substitute for a callable policy binary.
4. **Android runtime integration — structural export and host bridge implemented:** BF-native DSO symbol metadata, linker acceptance, and a separate C/Java `dlopen` JNI host adapter exist. The bridge was executed with a test-only x86_64 native policy on Linux JVM. **Actual AArch64 Android Bionic loading, JNI execution of BF policy code, Android APK parity and Threads callbacks/state remain OPEN.**
5. **Compiler maturity:** demonstrate native target self-hosting, independent interpreters, transaction-safe failure tests, performance and safety regression. Then delete legacy bounded paths, redundant source-only throughput plumbing and associated active configuration; preserve historical evidence snapshots separately.

There is deliberately **no iteration-count promise or 100M benchmark gate**. Completion requires executed evidence for all five gates; source ingestion and machine-code byte comparisons alone are not enough.

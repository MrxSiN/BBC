# Iteration 57 Linux self-hosting and target status

The canonical Linux BF compiler was not modified; a fresh native Stage 1→2 compilation reproduced its installed ELF byte-for-byte. Both new dynamic-callable BF stages were independently compiled by that Linux BF compiler and rebuilt identically. The new dynamic callable pipeline has **not** been run as an Android-native compiler or self-hosted natively on Android. [Linux S2 regression](../evidence/iteration57_linux_s2_regression.json), [stage tests](../evidence/iteration57_dynamic_callable_linear.json).

---

# Iteration 55 — opt-in policy constant stores (Linux verified)

Two original Gmail BF policies now compile into smaller callable AArch64 images using a new standard-Brainfuck-only value propagation stage. The original archived Android baseline and default codegen stay byte-identical. Linux execution checked 109 compiler cases, 480 functional Gmail IR cases, full source-to-ELF parity and a fresh two-stage native compiler replay. **No new Android device execution, APK parity or speedup has been established.** Remaining gates: device validation of the opt-in images, original Twitter/Threads policies, and genuinely resource-scaled callable IR for the 100M target. See [the Iteration 55 contract](ITERATION55_GMAIL_VALUEFOLD.md) and [roadmap](ANDROID_APP_ROADMAP_ITERATION55.md).

---

# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Iteration 53 — BF-owned far-loop AArch64 ELF path

The experimental Android compiler now emits compact, dynamically sized, all-eight-instruction freestanding PIE ELFs with **64-bit PC-relative long loop jumps**. New 32-byte bracket templates and BF-owned 64-bit position/literal arithmetic replace direct AArch64 `B` branch reach limits. **57 small ELF programs / 114 AArch64 simulator runs passed**. A 296,307-command **synthetic** program produced a 3,686,824-byte ELF accepted by `readelf`; this was not an Android device run or an original application policy compilation. No JNI/DSO or 100M executable compilation acceptance is claimed. Read [the engineering report](ITERATION53_LONG_RANGE_ANDROID_ELF.md), [roadmap](ANDROID_DYNAMIC_ROADMAP_ITERATION53.md), and [evidence](../evidence/iteration53_android_far_elf_tests.json).

---

# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Current self-hosting evidence — Android target-side stages recorded

The uploaded October 13 archive includes [Android native S2 evidence](ANDROID_NATIVE_S2_AUDIT.md): the standard-BF Android compiler source generated a 933,008-byte AArch64 image through independent seed execution, then Stage 1–3 compilers compiled that same BF source natively on Pixel 8 Pro/API37. All four archived images match. We checked their hashes and execution-result files offline; no fresh Android or independent cold-seed device run occurred here. Android source limit is 16,128 commands, not the planned 300,000. The unchanged **15,559-byte** Linux BF compiler has fresh byte-identical native Stages 1–2; Windows still has no native self-hosting.

---

# Self-hosting

**Platform boundary (2026-10-13):** All Stage 0→1→2 evidence on this page is for **Linux x86-64**. The authoritative source remains **15,559 bytes** with **zero** fixed emitted padding. Experimental Android-generated programs have executed on a device, but **no Android native compiler has self-compiled there**. Windows PE32+ is unimplemented. Android-first and Windows-second self-hosting gates are in [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) and [PLATFORM_ACCEPTANCE.md](PLATFORM_ACCEPTANCE.md).

**Yes, the compiler compiles itself.** The source stays Brainfuck all the way through machine-code generation. C interpreters are only cold-boot execution engines.

## Bootstrap

```text
compiler/core.bf -> independent C BF seed -> Stage 0 native ELF
                                      Stage 0 -> Stage 1 ELF
                                      Stage 1 -> Stage 2 ELF
                         compare the exact ELF bytes of every stage
```

The second C seed resolves BF brackets differently and agrees with the first. It is an additional trust check, not a proof that both implementations or the C toolchains are incorruptible.

Run from the project root on Linux x86-64:

```sh
python3 tests/verify_selfhost.py
```

The script compiles both independent seed interpreters, executes the BF compiler source, compares the native outputs byte-for-byte, checks generated programs and rejected input, and **only then** replaces the installed native compiler.

| Measurement | Latest executed value |
|---|---:|
| BF source instructions | 14,859 |
| Annotated source bytes | 15,559 |
| Source input limit | 16,128 executable commands |
| Stage 0/1/2 artifact bytes | 475,703 each |
| Stage equivalence | Exact bytes |

Latest input and binary SHA-256 hashes are in [`../evidence/selfhost.json`](../evidence/selfhost.json). Don't copy old hashes into release notes and hope nobody notices. All native ELF headers, size arithmetic and machine-code templates are emitted by Brainfuck. The Python runner transports bytes; it does not link, patch or optimize generated output.

## What this does not prove

Matching binaries validate a repeatable self-compilation cycle for the tested revision. They do not prove the bootstrap interpreters are universally trustworthy, provide a formal compiler-correctness proof, or establish C/Rust performance superiority. Those are separate problems.

## Integrated source filtering

Iteration 19 integrates the previously experimental compactor. Raw ignored text no longer fills compiler source records or native slots, and comment variants now produce byte-identical ELF output. Source capacity remains 16,128 **commands**, so this compiler has 1,269 command slots of spare self-compilation capacity. The source can be bootstrapped and self-compiled without the external filter. See [`STATE.md`](STATE.md) and [`../evidence/integrated_filter.json`](../evidence/integrated_filter.json).

# Iteration 55 — current callable Android policy implementation

An opt-in standard-Brainfuck IR pass propagates known cell values into native AArch64 constant stores for the original Gmail `row.bf` and `scope.bf`. Both full source-to-ELF outputs and independent bytecode/IR oracles passed on Linux. The legacy BF stages and Android device images are unchanged, and the new images are **not yet device-tested or benchmarked**. This is a small verified code-size optimization, not general resource-scaled compilation. See [the Iteration 55 contract](ITERATION55_GMAIL_VALUEFOLD.md), [roadmap](ANDROID_APP_ROADMAP_ITERATION55.md) and [evidence](../evidence/iteration55_policy_valuefold.json).

---

# Iteration 52: experimental dynamic AArch64 ELF code generation

Full all-eight-instruction AArch64 ELF generation now works in a resource-growing Linux-hosted standard-BF pipeline. **55 ELF programs passed 110 simulated runs**; one synthetic 296,307-command source produced an ELF accepted by `readelf`. None of the original eleven policy programs have been compiled with this route, and Android-native loading/JNI/DSO and long-branch veneers are unverified/unimplemented. The historical 2,719-command bound applies to the **legacy** image generator, not the new experimental path. [Contract](ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

---

# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Iteration 41 platform acceptance checkpoint

Windows now has BF-owned native PE emission for `><+-.,[]` through **64 commands**, with nested loops structurally checked on Linux. This **does not satisfy Windows native execution or Windows-native compiler/self-hosting**. Run the [Windows41 acceptance suite](../build/windows41_acceptance/manifest.json) under an actual Windows loader before upgrading status. Linux S2 and archived Android bounded S2 remain distinct evidence categories. [Iteration 41 details](WINDOWS_FULL64_PE.md).

---

# Latest Android native self-hosting acceptance classification

The archived Pixel 8 Pro/API37 native compiler run has [S2 execution evidence](ANDROID_NATIVE_S2_AUDIT.md) within a 16,128-command input envelope; this supports the bounded Android S2 gate but **not** the proposed 300,000-command capacity qualification, app integration, or universal Android ABI coverage. Windows x64 has [structural PE output only](WINDOWS_PE32_SEED.md); its loader and native compiler/self-hosting gates are open.

---

# Android generated-program loader acceptance — 2026-10-13

**The real-device generated-program gate passed 13/13 fixtures** on Pixel 8 Pro, Android 17/API 37, through 2,000 commands with loops. This does not satisfy the Android-native compiler, native self-compilation, callable APK backend or multi-device/API requirements. The isolated existing GM APK also passed instrumentation; it uses BF-to-C/JNI, not the BrainfuckCC native backend. See [executed device report](ANDROID_DEVICE_FOLLOWUP_20261013.md) and [raw loader evidence](../evidence/android_device_20261013/device_verification.json). Historical acceptance notes follow; the acceptance contract remains normative.

---

# Iteration 37 Android loader verification procedure

A reproducible [Android shell acceptance suite](ANDROID_DEVICE_ACCEPTANCE.md) now exists, but **the real-device gate remains unexecuted**. Offline AArch64 simulation does not satisfy Android platform verification; a real `adb` run of BF-produced binaries followed by native compiler execution and full self-compilation is required. See [report](ITERATION37_REPORT.md). Earlier acceptance definitions remain below.

---

# Acceptance status — Iteration 33, partial

The optional Linux-hosted Brainfuck compiler stages now produce AArch64 ELF PIE images for up to **512 standard Brainfuck commands containing loops**, including size-class crossing at command 331. This was **simulated**, not Android-device executed. It is not an Android-native compiler and does not establish native self-compilation, 300,000-command compatibility, unrestricted Android execution, or Windows PE32+. See [Iteration 33](ITERATION33_REPORT.md) and the [native test evidence](../evidence/iteration33_wide_slot_patch_512.json). The acceptance contract below remains normative.

---

# Platform acceptance status — Iteration 32 partial

A bounded **255-command loop-capable** Android AArch64 ELF path is now implemented using only standard Brainfuck for machine instruction generation and relocation. An independent **512-command linear** path also exists. Both remain Linux-hosted cross-generation and AArch64 **simulation**, not Android-native compiler execution. This does **not** satisfy the Android generated-program loader test, Android native self-hosting, 300,000-command acceptance target, APK packaging, or Windows PE32+ acceptance. See [Iteration 32](ITERATION32_REPORT.md).

---

# Platform acceptance contract — 2026-10-13

The adjective "universal" needs a boundary. This contract states what an Android-first, Windows-next *standard Brainfuck native compiler* must prove before release. Plans are not proof; actual status remains in [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json).

See also the versioned [Android compiler input/diagnostic/loader contract](ANDROID_COMPILER_PROTOCOL_V1.md), agreed in Iteration 26 but not yet a scalable native compiler.

## Input semantics: V0

Only `><+-.,[]` execute. Ignore all other source bytes. `[`/`]` must balance; 8-bit cells wrap modulo 256; 65,536 initially zero cells; pointer starts at zero; moving outside the tape traps deterministically; EOF stores zero; I/O consumes and emits raw bytes in order. Both optimizing and unoptimized paths preserve the observable semantics, resource-failure behavior, and trap conditions. Build options may explicitly change *documented* resource limits, not silently change V0.

## Coverage by product surface

| Surface | Initial acceptance | Not implied |
|---|---|---|
| Android generated program | Native AArch64 (`arm64-v8a`) executable ELF PIE, supported shell location/loader, full BF semantics, source-length limit documented and exercised | Runs as an APK, all devices/ABIs, unrestricted app-sandbox execution, JNI service access |
| Android native compiler | Executable Android AArch64 native compiler that reads BF source and writes valid Android program artifacts, and recompiles *its own complete BF source* with repeatable stages | A Linux-hosted cross-compiler that happens to emit Android ELF |
| Windows generated program | x86-64 PE32+ console EXE honoring Windows ABI, Win32 byte I/O and safe tape | ARM64 Windows, GUI apps, drivers or network APIs in ordinary BF |
| Windows native compiler | Executable Windows compiler generating Windows-native BF programs and passing complete self-compilation stages | PE headers inspected only, execution under Linux, Linux-to-PE cross-build alone |
| Linux regression | Current S2 x86-64 compiler continues to self-host and pass source/semantic/safety tests | Full S3 formal proof, arbitrary-width tapes or universal compiler completeness |

## Mandatory evidence for each mature target

- Record OS/version or Android API level, ABI, loader and execution context; record tool versions, source revision and hashes.
- Execute compiler executable on that target, then run representative generated programs with redirected/empty/binary byte inputs.
- Run Stage 0 native compiler → Stage 1 → Stage 2 and compare artifacts or justified semantic equivalence. Compile the entire authoritative BF compiler, not a toy subset.
- Run independently defined bracket, pointer, EOF, wrapping, resource-limit and malformed-input tests including loops at long branch distances.
- Record bounds-check and tape-memory invariants with executed negative cases; a simulation is not native OS execution.
- Independently inspect ELF/PE metadata, relocations, segment/section permissions and actual loader behavior; reject partial output on errors.
- Run benchmark workloads against comparable native C/Rust baselines, report distributions/uncertainty and explicitly label unmet speed objectives.

## Current evidence boundary

The archive reports Linux S2 with byte-identical stages and Android ten-command ELF execution on Pixel 8 Pro, Android 17/API 37. The last Android optimizer run contains 1,032 native executions. **Neither Android native compiler execution nor Android native self-hosting has evidence.** Windows compiler/emitter is **UNIMPLEMENTED**. Device measurements are historical archive evidence. Iteration 27 newly executed a BF-only wide source scanner on Linux and nine matching ten-slot output images, but did not run an Android device or native Android compiler. Source scanner capacity is not general Android native compilation. See [`ANDROID_NATIVE_OPTIMIZATION.md`](ANDROID_NATIVE_OPTIMIZATION.md), [`SELF_HOSTING.md`](SELF_HOSTING.md), and [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md).

## External policy and application limitation

The eleven audited Android policy sources span 18,192–296,307 BF commands and exceed both the ten-command Android experimental ceiling and existing 16,128-command Linux production limit. The proposed 300,000-command acceptance *target* addresses source capacity, not platform host ABI parity. Android app integration requires explicit host bridges. G29 has a distinct 32-bit checked-cell profile. None can be called compatible solely from successful parsing. Consult [`TARGET_WORKLOADS.md`](TARGET_WORKLOADS.md).

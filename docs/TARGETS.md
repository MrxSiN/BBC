# Iteration 65 — Android dynamic callable verification status

AArch64 shared objects continue to be emitted by standard BF, with a newly file backed host relocation duplicate index. The resulting DSOs are structurally and simulator verified; the actual Android Bionic loader, ART/JNI, installed APK and dynamic native self host remain unverified. [Evidence](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 62 Android application-namespace test path

The existing BF-native dynamic callable AArch64 `.so` compiler is now paired with a test-only installable APK harness. It packages nine byte-identical BF-generated DSOs and a separate host JNI bridge into the app native library directory and checks a nonce-bound private report. **Only Linux/JVM C-stub, BF-emulator, APK-archive and mock-ADB validation executed here, not a Gradle build or Android APK run.** Do not promote Android callable loader or app parity status until actual device acceptance. [Acceptance guide](ITERATION62_ANDROID_APK_ACCEPTANCE.md).

---

# Iteration 61 target note — Android ART/JNI unexecuted

A device acceptance command now exists for the BF-generated AArch64 callable DSO through Android shell loader **and** ART/JNI (`tools/android_bfp1_bridge/device_acceptance61.py --device`). Linux JVM and fake-ADB checks passed. Target Android `app_process` and real Bionic loading have **not** been executed in this environment. Successful shell ART execution will not by itself prove APK linker namespace or native self-hosting. [Scope and command](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md).

---

# Iteration 60 target status — loader device gate prepared, not executed

Nine BF-produced AArch64 dynamic callable DSOs now have a repeatable Android loader and ABI probe. Linux checks passed BF reference/AArch64 simulator parity and ELF inspection; a test-only Linux native DSO passed host `dlopen` and JNI edge-case tests. **No real ARM64 Android `dlopen` or JNI invocation of BF-generated code has occurred in this iteration.** The shell loader test is ready for NDK/ADB/device, but it is not APK/app namespace parity. New Linux native self-compilation was byte-identical for two generations; the full cold-bootstrap regression timed out after its first two stages, so that gate is incomplete. [Device plan](ITERATION60_ANDROID_LOADER_ACCEPTANCE.md), [test evidence](../evidence/iteration60_loader_readiness.json).

---

# Iteration 59 active Android target status

AArch64 standard-BF codegen has a new ELF64 DSO output with exported `bfc_call_v1`, versioned ABI metadata and Android-oriented 16 KiB load alignment. Linux-native compilation and AArch64 simulator tests plus independent cross-linking passed. **Actual Bionic `dlopen`, native/JNI target execution and self-hosting remain unverified**, so this is not yet a fully supported Android shared-library target. The normal Linux compiler S2 record remains separate. The numeric command-count objective is retired. [Report](ITERATION59_DYNAMIC_CALLABLE_DSO.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Iteration 57 Android callable target checkpoint

The new optional Android AArch64 callable ELF path has BF-owned dynamic linear emission and BF-owned checked 64-bit segment sizes; **loops, JNI dynamic symbols and Android device loader execution are not yet implemented/verified**. The old AArch64 freestanding ELF compiler does not provide callable semantics. No 100M threshold is active. Linux and Windows proven/historical status is unchanged. [Evidence](../evidence/iteration57_dynamic_callable_linear.json).

---

# Iteration 56 Android application compatibility target

Original TwitterHideAds `action.bf` now compiles on Linux into a 15,300-byte callable AArch64 image, with independent code-byte and BF-versus-IR parity checks; **Android device/JNI execution remains pending**. The next target is dynamically stored callable IR for the other original Twitter and Threads policies, not another artificial fixed record tier. [Current roadmap](ANDROID_APP_ROADMAP_ITERATION56.md).

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

# Iteration 51 Android integration checkpoint

[The current integrated code/pair stream](ITERATION51_COMPACT_AARCH64_RELOCATION_LEDGER.md) has BF-owned all-eight compact raw machine code, 64-bit native-word offset tracking, and BF-owned bracket matches in disk-backed dynamic storage. The verified output is **unrelocated code plus matched pairs**; branch-word encoding, ELF/DSO layout, Android-native execution, original eleven policy compilation and JNI/APK parity are outstanding. The existing full ELF limit of 2,719 instructions is unchanged.

---

# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Android real-application priority — Iteration 46

## Iteration 49 — dynamic capacity principle

The new [Brainfuck streaming slot stage](../experiments/android_streaming_linear_slots.bf.notes.md) emits linear native AArch64 slots without allocating a fixed source table or encoding a source command count. The host has optional resource quotas; physical memory, storage, address reach and CPU time always remain finite. This is not a general ELF backend, loop-capable native codegen, shared library or APK toolchain. The separately verified 100M source scanner and 32-bit loop pairer do not yet feed general native relocation. [Evidence](../evidence/iteration49_android_dynamic_stream.json).


## Iteration 48 — 32-bit loop pairing without AArch64 relocation

**Executed:** BF-owned streaming bracket pairing at positions 0 and 100,000,001 in a real 100,000,002-byte source, using a 255-deep fixed stack. Rejections, source-to-event parity, atomic output handling and independent seed agreement passed. The old raw scanner protocol is preserved; use the opt-in framed scanner for pairing. [Evidence](../evidence/iteration48_android_100m_pairing.json).

**Required next:** 32-bit positions are *source* offsets, not machine-code addresses. Implement BF-owned compact streaming IR and executable code offset mapping, AArch64 long-branch placement, safe multi-gigabyte artifact accounting and dynamic ELF/DSO output; then compile and test all eleven real Android policies. Native code generation is still limited to 2,719 instructions, not 100 million.

---


## 100-million-command Android compiler objective

The capacity target is now **100M executable BF instructions per source unit**. The separately verified [source analyzer](ANDROID_100M_CAPACITY.md) is not an Android ELF backend. The currently generated native Android images remain limited to 2,719 commands, and eleven real Android policy kernels require JNI/shared-library integration. Do not relabel a generic compressed input scan as target-native code generation.

---

**Real Android application gate (Iteration 46, OPEN):** The 2,719-command shell ELF prototype is not a JNI shared library and does not compile the 11 policy programs from GmailHideAds, TwitterHideAds or ThreadsHideAds (18,192–296,307 commands each). New mandatory targets are original-program BF-native compilation, JNI-loadable AArch64 `.so`, per-program tape/host ABI parity, and end-to-end installed APK tests. Larger-application stretch: >=10M commands per unit and >=100M across project modules. [Contract](ANDROID_APPLICATION_ACCEPTANCE.md).

---

# Iteration 45 target update — Android ELF class eight

Standard BF now generates Android AArch64 PIE images up to **2,719 commands including loops** in the opt-in tape-relocated multiclass pipeline. Class eight places RX and RW regions without overlap, correctly encodes the `ADRP x20` carry, and preserves raw byte I/O and pointer trap behavior under two-load-base AArch64 simulation. **No Android loader/device run of these new artifacts** and no 300,000-command release acceptance. The existing Android-native compiler S2 is supported only by prior bounded device evidence; Windows still has no native loader/S2 verification. See [the class-eight report](ITERATION45_ANDROID_REPORT.md).

---

# Iteration 44 Windows status — PE192 still Linux-tested only

A new [BF-owned 192-command PE32+ pipeline](WINDOWS_FULL192_PE.md) compiles all eight standard BF instructions, including loops. Generated x64 code passed 77 tests under Linux CPU Win32 shims, and 14 Windows-target samples are packaged. **Windows loader/API execution, Windows-native compiler execution and S2 are not verified.** Linux S2 and archived Android bounded S2 remain separate; Android 300,000-command capacity is unmet. [Report](ITERATION44_REPORT.md).

---

# Iteration 43 Windows status — PE128 Linux CPU execution only

The Windows x86-64 backend now has a [BF-owned 128-command PE32+ path](WINDOWS_FULL128_PE.md), producing 3,072-byte images for all eight instructions including nested loops. Linux CPU-shim differential testing passed 100 source programs. This is **not** real Windows loader/API execution and not Windows native S1/S2. Linux S2 and archived bounded Android S2 are maintained; Android 300,000-command acceptance remains open. [Report](ITERATION43_REPORT.md).

---

# Iteration 42 Windows target verification update

The Windows PE path has **all eight original Brainfuck instructions up to 64 commands**. Its code is now **EXECUTED on a Linux x86-64 CPU with independent test-only Win32 import shims** for 164 reference-matched cases and 11 archived binaries. This is not Windows loader/Win32 runtime acceptance, does not increase capacity and does not prove Windows-native compiler execution or self-hosting. See [execution contract](WINDOWS_LINUX_CPU_EXECUTION.md), [report](ITERATION42_REPORT.md) and [evidence](../evidence/iteration42_windows_x64_cpu_shim.json). Android bounded native S2 and Linux S2 remain separate; Android 300,000 commands are unimplemented.

---

# Iteration 41 target status — complete bounded Windows instruction set

The [Windows BF-only loop PE pipeline](WINDOWS_FULL64_PE.md) now produces source-dependent PE32+ images for all eight `><+-.,[]` commands, including nested loops within a **64-command bound**. The BF stages execute on Linux and generated x64 code/headers are inspected offline. **Windows loader execution and Windows-native S2 remain unverified**; a Windows smoke package is ready. Android bounded native S2 is backed by archived device evidence; Android 300,000-command output remains unimplemented. Linux S2 is unchanged. [Iteration 41 report](ITERATION41_REPORT.md).

---

# Iteration 40 checkpoint — Windows six-instruction linear PE backend

The new [Windows linear I/O backend](WINDOWS_LINEAR_IO_PE.md) generates BF-owned PE32+ images for `+ - > < . ,` from at most 64 executable commands, with imported Win32 byte I/O and deterministic x64 pointer traps. Its BF source, native Linux writer and static image tests pass; **no Windows loader/API execution** was performed. `[` and `]`, Windows-native compiler execution/S2, and Android's separate 300,000-command acceptance target remain outstanding. See [iteration report](ITERATION40_REPORT.md) and [evidence](../evidence/iteration40_windows_linear_io.json). Historical notes follow below.

---

# Iteration 39 target status — bounded Windows program compilation

Windows PE32+ x86-64 now has a [Brainfuck-owned source-dependent linear compiler](WINDOWS_LINEAR_PE.md): **64 executable `+ - > <` commands**, generated 2,048-byte `.exe`, zeroed 65,536-cell tape, checked pointer moves, and a Win32 `ExitProcess` import. The PE and x64 bytes were inspected on Linux; **Windows loader execution is NOT RUN**. This is not a complete Windows compiler or native S2. Linux S2 and archived bounded Android S2 are maintained; the Android 300,000-command release goal remains open. [Iteration 39 evidence](../evidence/iteration39_windows_linear_pe.json).

---

# Current target evidence — Android S2 recorded; Windows structural PE seed

Recorded Android Pixel 8 Pro/API37 evidence contains four identical AArch64 native compiler stages and fourteen executable program cases. Offline verification of the uploaded archive passed; [details](ANDROID_NATIVE_S2_AUDIT.md). This supports bounded **S2 EXECUTED (archived evidence)**, not general 300,000-command compiler support or APK/JNI support.

Windows x86-64 now has a BF-written [PE32+ fixed exit image](WINDOWS_PE32_SEED.md), with an import table and read/execute versus read/write sections. The image is **not executed on Windows** and is not a compiler. Linux x86-64 remains S2 with unchanged source. Historical target notes follow.

---

# Target verification — Android USB follow-up, 2026-10-13

**Android AArch64 generated programs: EXECUTED** on Pixel 8 Pro, Android 17/API 37, with **13/13** fixtures through **2,000 commands including loops**. Runtime pages are 4 KiB; 16 KiB-page devices and additional APIs/ABIs are untested. The existing GM release/test APKs also ran successfully, using GM's BF-to-C/JNI implementation. **Android-native compiler/S2 and BrainfuckCC JNI/APK generation remain unimplemented.** Linux source and prior S2 are unchanged; Windows x86-64 PE32+ remains unimplemented. See [follow-up report](ANDROID_DEVICE_FOLLOWUP_20261013.md). Historical target notes follow.

---

# Iteration 37 target verification update

Android AArch64: a prepared [13-program shell acceptance bundle](ANDROID_DEVICE_ACCEPTANCE.md) was structurally inspected and simulator-tested in Linux. **New Android loader execution: NOT RUN.** The compiler is not yet Android-native or self-hosted there. Linux x86-64: the authoritative 15,559-byte standard-Brainfuck source and S2 native compiler are unchanged; native self-compilation replay passed. Windows x86-64 PE32+: UNIMPLEMENTED. See [Iteration 37 report](ITERATION37_REPORT.md). Historical target details follow.

---

# Android AArch64 latest experimental status — Iteration 36

The opt-in Linux-hosted BF-only compilation path generates AArch64 ELF PIE binaries for up to **2,000 commands with nested loops** using `--multiclass --tape-relocated --loops`. It is tested in an AArch64 instruction simulator, **not** by the Android loader on a device. The native Android compiler and target-side S2, broader Android ABI coverage, APK packaging and Windows x86-64 PE32+ backend are still absent. Earlier ten-command Android-device execution remains historical evidence for a different pipeline. See [Iteration 36 report](ITERATION36_REPORT.md) and [evidence](../evidence/iteration36_wide_loops_2000.json).

---

# Iteration 35 active handoff

Android AArch64 now has a separate opt-in BF-only `--multiclass --tape-relocated` image path reaching 2,000 linear commands or 1,024 commands with loops. RX/RW virtual placement and AArch64 startup are BF patched through six ELF size classes, tested in Linux-hosted AArch64 simulation. Android device execution of these images is **not verified**. The Linux x86-64 compiler remains self-hosted; Android-native compiler S2 and the Windows PE32+ backend remain **unimplemented**. See [Iteration 35](ITERATION35_REPORT.md).
---

# Current target update — Iteration 34

**Android AArch64 experimental mode:** `--multiclass --loops` generates PIE shell-oriented images for up to **1,024 BF commands**, including loops, in **four 16 KiB file-size classes**. The final ELF relayout, startup, tape, code bytes and native branch words remain BF-authored. The new artifacts passed Linux-hosted AArch64 simulation, **not Android loader/device tests**. The Android compiler itself is not native on Android and cannot self-host there. Historic ten-command real-device evidence remains separate. Linux x86-64 native self-hosting remains the established base; **Windows x86-64 PE32+ is UNIMPLEMENTED**. See [Iteration 34](ITERATION34_REPORT.md) and the [status matrix](../status/CONFORMANCE_MATRIX.json). The following sections retain earlier iteration findings, not current limits.

---

**Verification addendum:** 71 source programs, 8,137 branch-pair checks and 142 simulator runs passed in Iteration 34. Fresh native Linux Stage 1→2 compilation passed byte-for-byte; cold Stage 0, Android loader tests and the full release suite were not rerun. An independent 75-million-step seed-interpreter comparison was inconclusive. See [Iteration 34 report](ITERATION34_REPORT.md).

# Target update — Iteration 33 Android 512-loop path

A standard-Brainfuck Linux-native stage now supports **512-command loop-bearing Android AArch64 ELF PIE images**, with `--page-class --loops` and the 330→331 size-class transition. The new images passed Linux-hosted AArch64 instruction simulation and `readelf` validation, **not actual Android loader execution**. The existing ten-command historical Android device evidence does not apply to these larger ELFs. There is no Android-native compiler/self-hosting or Windows x86-64 PE32+ backend. See [Iteration 33](ITERATION33_REPORT.md). Older target updates below are historical.

---

# Target update — Iteration 32 partial wider loops

The Linux-hosted Brainfuck stages now produce Android AArch64 PIE images containing **up to 255 commands with loops** using `--page-class --loops` or `--dynamic --loops`. The size-class writer still accepts **512 commands without loops**, with 16,480- and 32,864-byte files. The 255-command loop ceiling prevents loop testing at the 331-command size transition. These are simulator-verified ELF images only; there was **no new Android loader/device execution**, no Android-native compiler or S2 cycle, and no Windows PE32+ implementation. See [Iteration 32](ITERATION32_REPORT.md).

---

# Target update — Iteration 31 partial, page class ELF

A Linux-executed standard Brainfuck writer now builds Android AArch64 PIE files in **two aligned ELF file size classes**: 16,480 bytes through 330 commands and 32,864 bytes from 331 to 512 commands. This is an **opt-in linear-program path**; loop-capable images remain bounded at **74 commands**. Independent AArch64 instruction simulation and `readelf` inspection passed, but there has been **no new Android OS/device execution** of these images. Historical ten-command device observations remain separate. Android compiler execution/self-hosting and Windows PE32+ output remain unimplemented. See [Iteration 31](ITERATION31_REPORT.md) and [stage notes](../experiments/android_page_class_elf_wrapper.bf.notes.md).

---

# Latest target update — Iteration 30 partial

Android AArch64 has a separate Linux-native BF-built PIE wrapper whose **RX segment varies with 0..255 linear instructions**. The artifact file itself remains **16,480 bytes** throughout the current 16 KiB-aligned size class. Bracketed programs remain **74-command bounded** using the BF patcher. These images were **simulated**, not executed on an Android device. Android-native compiler/self-hosting and Windows PE32+ remain **UNIMPLEMENTED**. Historical 10-command Android device execution remains valid evidence only for those original artifacts. See [Iteration 30](ITERATION30_REPORT.md) and [current state](STATE.md).

---

# Android backend update — Iteration 29 follow-up

A new Linux-native BF slot patcher now integrates wide loop branches into the fixed 74-slot AArch64 PIE wrapper. This path has AArch64 simulator evidence for 85 programs at two load bases, **not new Android-device tests**. It supports the tested full eight-command V0 subset **within 74 command slots**; device loader behavior, general ELF image sizing and Android-native self-compilation remain UNVERIFIED. See [`ITERATION29_LOOP_FOLLOWUP.md`](ITERATION29_LOOP_FOLLOWUP.md).

---

# Native target status — 2026-10-13, Iteration 29 extended linear image partial

These are **recorded archive outcomes**. Iteration 29 added 74-command linear AArch64 ELF images constructed by native BF stages on Linux and checked in an independent AArch64 instruction simulator at two load biases. **No new Android device execution occurred.** Iteration 26 re-executed existing Android BF stages on Linux and two Linux native self-compilations. It did not re-execute Android or Windows programs. See [`ANDROID_COMPILER_PROTOCOL_V1.md`](ANDROID_COMPILER_PROTOCOL_V1.md).

| Target and artifact | Native generated-program execution | Native compiler on that OS | Full native self-hosting |
|---|---|---|---|
| **Linux x86-64 static ELF64** | **EXECUTED** | **EXECUTED** | **S2 EXECUTED**, three byte-identical native bootstrap stages |
| **Android AArch64 ELF PIE shell** | **EXECUTED** historical ten-command loop ELF on Pixel 8 Pro Android 17/API 37; **74-command linear** image only Linux-simulated | **UNIMPLEMENTED** | **UNIMPLEMENTED / UNVERIFIED** |
| **Windows x86-64 PE32+ console** | **UNIMPLEMENTED** | **UNIMPLEMENTED** | **UNIMPLEMENTED** |
| Optional Android `armeabi-v7a`, `x86`, `x86_64`, other OS/ISAs | **UNIMPLEMENTED** | **UNIMPLEMENTED** | **UNIMPLEMENTED** |

## Current contracts and proof boundaries

The Linux BF compiler has a 65,536-cell V0 tape, 16,128-executable-command source ceiling, 255 bracket levels, fixed 32-byte native slots, and exact ELF file length of `215 + 32 × commands` with **zero fixed trailing output padding**. Its self-compiled compiler is 475,703 bytes, built from the 15,559-byte raw standard BF source (14,859 executable instructions). The native compiler writes its own machine instructions and headers. Consult [`SELF_HOSTING.md`](SELF_HOSTING.md).

A separate 1,170-instruction BF source scan stage now filters and counts up to 300,001 executable commands (tested on Linux). Its opt-in adapter makes byte-identical images for nine existing bounded Android sources. **The loop-capable Android output limit remains ten executable commands**; a separate 74-command linear generator now exists. Scanner capacity is not general generated-code capacity. See [`../experiments/android_source_scan.bf.notes.md`](../experiments/android_source_scan.bf.notes.md) and [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json).

Iteration 28 adds Linux-executed BF-only 24-bit bracket metadata and BF tape-stack pair extraction across a tested 300,002-command position. **No general AArch64 relocation or large native Android ELF was produced.** See [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md) and [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json).

The experimental Android compiler pipeline is also written in Brainfuck and generates AArch64 image bytes from BF stages. Its historical Iterations 21–25 first passed **structural and simulation** testing on Linux, then later limited generated programs were **EXECUTED on actual Android**; those statements describe *different time periods*, not contradictory evidence. The BF-owned native optimization report contains the latest results. The compiler itself **was not ported to run on Android**. The original loop-capable path has ten-command capacity. A separate Linux-simulated 74-command fixed-image linear path exists, but scalable loop relocation and dynamic ELF remain missing. See [`ANDROID_AARCH64_PROTOTYPE.md`](ANDROID_AARCH64_PROTOTYPE.md) and [`ANDROID_NATIVE_OPTIMIZATION.md`](ANDROID_NATIVE_OPTIMIZATION.md).

Windows independent BF interpreter seed I/O checks did run on a Windows host as tooling for the Android study. That is **not** Windows PE32+ generation, nor Windows-native BF compiler execution.

## Platform-specific acceptance

- **Android first:** `arm64-v8a`, documented minimum *tested* API level, supported shell execution/loader context, native BF program and BF compiler execution, then full native compiler Stage 0→1→2. Correct byte I/O/EOF/traps and robust relocation must hold under PIE/ASLR. The proposed large-source test is **at least 300,000 BF instructions**; not currently available. An executable in `/data/local/tmp` is **not automatically** an APK, app sandbox, JNI or Xposed integration.
- **Windows second:** PE32+ x64 console, correct Microsoft x64 ABI, imports and loader handling, standard handles with binary input/output and pipes, deterministic traps, then Windows-native Stage 0→1→2. No undocumented hardcoded syscalls or foreign production code generators.
- **Linux ongoing:** rerun its established S2 cycle after meaningful compiler changes; do not demote it to a development seed.

Full details, numbered iterations and explicit out-of-scope claims: [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) and [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md). Status evidence remains in [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json); planned work remains separately in [`../status/ROADMAP.json`](../status/ROADMAP.json).

## Iteration 28 follow-up — branch records only

A BF-only Linux-executed AArch64 branch word stage now encodes 26-bit unconditional `B` displacements from the 24-bit matched bracket pairs. The largest tested **source stream** with a branch pair was **300,000 commands**. This does not increase the ten-command **generated Android ELF** limit: applying long branches, producing dynamically sized PIE files, executing the generated branches on Android, and Android-native compiler self-hosting remain **UNIMPLEMENTED**. The stage and test evidence are described in [`../experiments/android_wide_branch_encoding.bf.notes.md`](../experiments/android_wide_branch_encoding.bf.notes.md).

## Iteration 29 partial — BF owned 74 slot linear ELFs

Two BF-native Linux executed stages now construct all 48-byte instruction slots and a runnable **fixed 4,192-byte AArch64 ELF PIE with up to 74 linear commands**. Bracket templates are emitted but marked unrelocated and rejected from executable assembly. The new image has only been exercised in an instruction simulator, not an Android OS loader. **Do not transfer the historical Pixel 8 Pro ten-command device evidence to these new images.** See [`ITERATION29_REPORT.md`](ITERATION29_REPORT.md) and [`../evidence/iteration29_extended_slots.json`](../evidence/iteration29_extended_slots.json).

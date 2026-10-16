# Project name — BrainfuckCC

The project is now **BrainfuckCC** (repository: https://github.com/MrxSiN/BrainfuckCC). The former names `brainfuckC`/`brainfuckc` and `brainfuck-native` are retired in maintained code and docs: the Android JNI test bridge is now Java package `org.brainfuckcc`, library `libbrainfuckcc_bridge.so` and property `brainfuckcc.bridge.absolutePath`. Archived `evidence/` and `build/` records keep their original names and paths as historical data. No compiler source, BF stage or emitted machine code changed.

---

# Iteration 65 — File backed dynamic callable relocation bookkeeping

Replaced in memory Python duplicate patch indexing with a sparse disk backed bitset in the active AArch64 callable pipeline. Five iteration 64 DSO hashes remain byte identical and a 12,000 pair loop program compiles and passes two simulator/reference runs. Linux native self compilation passed twice; no Android loader, ART/JNI, APK or target native dynamic compiler run occurred. [Report](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md), [release gates](../evidence/iteration65_release_gates.json).

---

# Iteration 64 — Callable code and branch target validation

Every BF-produced shared object is now independently scanned for the current BFP1 AArch64 templates, callable entry and exit code, and correct matching nested loop veneers before atomic publication. This is a host validation guard, not foreign code generation. Tests: 52 BF-generated programs; 104 AArch64/reference comparisons; seven native-code corruption rejections; two injected corruption rollbacks; 13 archived DSO structural passes, including three original Gmail/Twitter policy images. The iteration-63 metadata regression and existing DSO and Linux JVM/JNI host tests pass. **No real device execution of the new DSO path occurred here**, and Android-native dynamic S2, full application parity, and fallback retirement remain open. [Report](ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md), [evidence](../evidence/iteration64_dynamic_callable_native_integrity.json).

---

# Iteration 63 — Fail-closed BF callable DSO publication

The standard-BF AArch64 DSO emitter now has an independent, bounded-memory post-generation ELF export validator. It checks the original BF-produced header, load and dynamic segments, symbol lookup tables, section entries and 64-bit file extent before replacing the requested output. This performs no compilation in Python. Local regression passed 240 generated programs, 960 AArch64/reference simulations, 40 corrupted header tests, 4 size mismatch tests and an injected bad-header atomic rollback. A sparse length test passed above 4 GiB; **this is not a compiled 4 GiB program**. DSO structural tests and Linux JVM JNI C-stub tests still pass. No Android Bionic/ART/installed APK or native Android S2 execution happened this iteration. [Iteration 63 report](ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md), [evidence](../evidence/iteration63_dynamic_callable_integrity.json).

---

# Iteration 62 — Installed APK acceptance scaffold, not executed on device

Nine BF-generated AArch64 callable DSOs are now packaged byte-exactly into a test-only Android APK project alongside an NDK-compiled JNI transport library. A shared Java assertion suite runs with both shell and APK library naming; the APK uses its actual native library directory, nonce-bound private results and hash-verified installed-package acceptance. Linux host Java/C-stub checks and fake-device negative tests passed. **Gradle build and Android app installation have not run here.** BF codegen unchanged; the nine policies and prior DSO/ELF simulator evidence still pass. Original app parity and native Android S2 remain open. [APK guide](ITERATION62_ANDROID_APK_ACCEPTANCE.md), [release gates](../evidence/iteration62_release_gates.json).

---

# Iteration 61 current state — ART/JNI device test prepared

The Android BF-generated callable `.so` and its native BF compiler stages are unchanged. A Java ART test client now invokes `Bfp1Bridge.run` against all nine existing BF-generated fixtures and checks byte output, tape state, loop gas and traps. Linux-host JNI tests passed through nine **C test-only policy stubs**, including fault-injection rejection; ADB transport logic passed mock checks. No Android execution has occurred for the new DSO/JNI path, and APK namespace parity is a separate test. Continue using the [Iteration 61 device command](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md); full Android dynamic-native S2 and eight absent policy sources remain open. Previous numbered capacity objectives are retired; old routes are fallbacks.

---

# Iteration 60 — actual Android loader acceptance remains open

Added a reproducible device-loader probe and nine BF-generated dynamic callable `.so` fixtures. All nine compile and pass independent BF-reference versus AArch64-instruction-simulator parity on Linux; ELF structure and host native-loader smoke pass. Linux JVM JNI bridge coverage now includes zero-length input/output, output-capacity zero and validation errors. **No Android device execution or app JNI/APK parity was performed.** Android NDK/ADB are unavailable in this runtime. Run `python3 -m tools.android_bfp1_bridge.device_acceptance60 --device --serial DEVICE_SERIAL` with `ANDROID_NDK_HOME` set on an arm64 Android device to test actual `dlopen` and policy calls. This does **not** substitute for JNI/APK parity or dynamic-compiler native Android S2. Legacy paths remain fallbacks; original BF compiler and stage code unchanged. [Iteration 60 report](ITERATION60_ANDROID_LOADER_ACCEPTANCE.md), [evidence](../evidence/iteration60_loader_readiness.json), [roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 59 active state — BF-native callable shared-object output

Resource-scaled BF-native all-eight-command AArch64 compilation now emits a linkable ELF shared-object container, complete with BF-generated PT_DYNAMIC, dynamic symbol lookup and a global `bfc_call_v1` entry. Independent `readelf` and AArch64 cross-linker tests passed; 13 DSO programs passed 52 simulated native runs. Three locally pinned original policies compiled to `.so`. A host-only JNI adapter was executed on Linux JVM with a **test-only x86_64 stub**. This does **not** constitute Android Bionic loading, JNI execution of BF-produced code, original app parity, all eleven policies or Android self-hosting. The old numeric command-count goal remains retired. Evidence and next blockers: [Iteration 59 report](ITERATION59_DYNAMIC_CALLABLE_DSO.md), [DSO validation](../evidence/iteration59_dynamic_callable_dso.json), [dynamic roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Iteration 57 — resource-scaled callable compiler work

A new standard-BF callable ELF lane compiles six loop-free operators without the previous 4,096-record source table, and BF emits checked 64-bit ELF file sizes. **60 cases / 240 simulated AArch64 runs / 14 wide-size tests** passed, including growing mixed programs. Loop relocation, Android device execution, JNI exports and full self-hosting remain open. The synthetic 100M objective is **retired** in the active plan, with archived measurements unchanged. Legacy bounded and freestanding code remain temporary fallbacks until replacement. [Evidence](../evidence/iteration57_dynamic_callable_linear.json); [report](ITERATION57_DYNAMIC_CALLABLE_LINEAR.md); [active gates](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 56 — original Twitter action policy compiles on Linux

The opt-in standard-BF `policy_clear56` prepass shrinks Twitter `action.bf` from 4,723 to 3,819 callable IR records, allowing source-to-ELF compilation: 15,300 AArch64 bytes. Independent native byte encoding and 10 original-source/IR frame comparisons pass, and prior Gmail images remain unchanged with the new prepass. This is **Linux-hosted** code generation, **not Android device execution**. The fixed 4,096-record ceiling and 100M target remain open. See [implementation contract](ITERATION56_TWITTER_ACTION_CLEAR.md) and [roadmap](ANDROID_APP_ROADMAP_ITERATION56.md).

---

# Iteration 55 — opt-in policy constant stores (Linux verified)

Two original Gmail BF policies now compile into smaller callable AArch64 images using a new standard-Brainfuck-only value propagation stage. The original archived Android baseline and default codegen stay byte-identical. Linux execution checked 109 compiler cases, 480 functional Gmail IR cases, full source-to-ELF parity and a fresh two-stage native compiler replay. **No new Android device execution, APK parity or speedup has been established.** Remaining gates: device validation of the opt-in images, original Twitter/Threads policies, and genuinely resource-scaled callable IR for the 100M target. See [the Iteration 55 contract](ITERATION55_GMAIL_VALUEFOLD.md) and [roadmap](ANDROID_APP_ROADMAP_ITERATION55.md).

---

# Iteration 54: original Gmail native policy replayed independently on Linux

The uploaded Android record now supports **nine device ELF loader passes**,
**bounded Android native S2**, and a **Gmail native-policy test APK** with
21 instrumentation runs and 634,229 Java-oracle parity comparisons. Fresh
Linux BF-stage replay produces the **same 13,064-byte row** and
**13,168-byte scope** AArch64 policy images, byte-for-byte. This is
independent Linux reproduction of the BF-owned compiler logic, **not new
Android device execution or a speed win**. Both Gmail BF native policies
remain slower than optimized C/Java baselines. See
[the engineering report](ITERATION54_PROGRESS_REPORT.md),
[reproducibility contract](ITERATION54_LINUX_GM_REPLAY.md) and
[the revised roadmap](ANDROID_APP_ROADMAP_ITERATION54.md).

---

# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Iteration 53 — BF-owned far-loop AArch64 ELF path

The experimental Android compiler now emits compact, dynamically sized, all-eight-instruction freestanding PIE ELFs with **64-bit PC-relative long loop jumps**. New 32-byte bracket templates and BF-owned 64-bit position/literal arithmetic replace direct AArch64 `B` branch reach limits. **57 small ELF programs / 114 AArch64 simulator runs passed**. A 296,307-command **synthetic** program produced a 3,686,824-byte ELF accepted by `readelf`; this was not an Android device run or an original application policy compilation. No JNI/DSO or 100M executable compilation acceptance is claimed. Read [the engineering report](ITERATION53_LONG_RANGE_ANDROID_ELF.md), [roadmap](ANDROID_DYNAMIC_ROADMAP_ITERATION53.md), and [evidence](../evidence/iteration53_android_far_elf_tests.json).

---

# Iteration 52: experimental dynamic AArch64 ELF code generation

Full all-eight-instruction AArch64 ELF generation now works in a resource-growing Linux-hosted standard-BF pipeline. **55 ELF programs passed 110 simulated runs**; one synthetic 296,307-command source produced an ELF accepted by `readelf`. None of the original eleven policy programs have been compiled with this route, and Android-native loading/JNI/DSO and long-branch veneers are unverified/unimplemented. The historical 2,719-command bound applies to the **legacy** image generator, not the new experimental path. [Contract](ITERATION52_DYNAMIC_AARCH64_ELF.md) and [evidence](../evidence/iteration52_android_dynamic_elf_tests.json).

---

# Iteration 51 Android integration checkpoint

[The current integrated code/pair stream](ITERATION51_COMPACT_AARCH64_RELOCATION_LEDGER.md) has BF-owned all-eight compact raw machine code, 64-bit native-word offset tracking, and BF-owned bracket matches in disk-backed dynamic storage. The verified output is **unrelocated code plus matched pairs**; branch-word encoding, ELF/DSO layout, Android-native execution, original eleven policy compilation and JNI/APK parity are outstanding. The existing full ELF limit of 2,719 instructions is unchanged.

---

# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Iteration 49 — resource scaled native code streaming

A new [standard BF native slot stage](../experiments/android_streaming_linear_slots.bf.notes.md) reads arbitrary raw source bytes and emits AArch64 linear instruction slots as a stream with **no built in source command count ceiling**. A 300,001-command program generated 14,400,048 native bytes and matched existing BF-owned templates. The host only frames and copies bytes, with optional caller supplied output quotas; it does not parse BF or emit instructions. **Not a runnable ELF:** brackets, scalable relocation, dynamic executable layout, JNI and the eleven real application policies remain open. The complete Android ELF backend still supports only 2,719 commands. [Report](ITERATION49_DYNAMIC_ANDROID_STREAMING.md) and [evidence](../evidence/iteration49_android_dynamic_stream.json). The 100M benchmark remains a target, not an artificial maximum or a completed native executable. Earlier iteration notes remain historical.

# Current state — Iteration 47

## Iteration 48 — current evidence-gated state

The latest opt-in Linux-native BF pipeline now **pairs 32-bit bracket offsets spanning 100 million instructions** after the 32-bit source scanner. The original scanner remains unchanged; the framed variant adds a BF-emitted event terminator. The pairing stage supports up to **255 concurrent open brackets** and rejects depth 256. The real 100,000,002-byte single-loop source passed generic-transport ingestion and BF-owned pairing. [Evidence](../evidence/iteration48_android_100m_pairing.json); [report](ITERATION48_ANDROID_100M_PAIRING.md).

This does **not** compile 100 million BF commands to machine code. Actual AArch64 ELF output is still limited to **2,719 commands**. Eleven original Android application policies are still uncompiled by this backend. Linux native S2 source remains unchanged at **15,559** bytes with zero fixed padding; archived bounded Android-native self-hosting remains separate. The next implementation is BF-owned streaming IR/code layout, relocation and dynamic AArch64 ET_DYN emission.

---


## Iteration 47 source-analysis evidence

100M **per-unit** is the new target. A Brainfuck-only 14,880-instruction RLE source analyzer now handles 100M raw BF instructions with 32-bit command positions and bracket-depth checks; real raw-file transport and independent interpreter evidence pass. This is [source capacity only](ANDROID_100M_CAPACITY.md). Android AArch64 codegen remains at 2,719 commands; native target S2 compiler input remains 16,128 commands. The eleven application policies, 100M native compiler and APK acceptance are **not** complete. Core BF source remains **15,559 bytes**, including 14,859 executable instructions and zero fixed trailing padding. Historical snapshots below are not revised.

---

**Iteration 46 contract checkpoint (PLANNED, not executed):** The three mandatory real Android module workloads contain 11 BF policies and 1,312,912 filtered commands in total (largest 296,307). The recorded 2,719-command AArch64 output path and separate 16,128-command Android native compiler input capacity cannot compile any of them. A working Android policy compiler must produce all 11 native kernels, preserve per-app tape/host protocols, integrate a JNI-loadable native library and pass rebuilt APK tests. The earlier >=10M-per-source stretch has been superseded by >=100M per source; neither native compilation target is implemented. [Acceptance contract](ANDROID_APPLICATION_ACCEPTANCE.md), [machine gates](../status/ANDROID_APPLICATION_GATES.json).

---

# Iteration 45 current state — Android bounded expansion

The Linux-hosted, standard-Brainfuck AArch64 toolchain now accepts **0–2,719 Brainfuck commands with loops** in opt-in `--multiclass --tape-relocated --loops` mode. The class-eight BF carry stage patches ELF RX sizes and `ADRP` at fixed locations while passing every other byte unchanged; the Python adapter only performs byte transport, framing, hash checks and atomic output placement. **35 source programs, 70 AArch64 simulator runs and 31 loop pairs** passed the focused check, along with independent interpreter agreement for the new BF stage. New images **have not run on an Android device**. Existing archived Android S2 stays bounded to its previous compiler input profile. The **300,000-command universal goal remains open**. Historical milestones follow without changes. [Iteration 45 report](ITERATION45_ANDROID_REPORT.md) and [evidence](../evidence/iteration45_android_class8.json).

---

# Iteration 44 state — Windows 192-slot BF-generated PE32+

The optional Windows x86-64 compiler path emits **3,584-byte PE images for up to 192 BF commands** using standard-BF slot generation and branch patching. Linux x64 test-only Win32 shims executed 77 programs with 990 checked loop targets. **No actual Windows loader execution or Windows S2.** The older 128/64 paths remain tested. Linux canonical source remains **15,559** bytes with zero fixed trailing padding and **569** bytes of raw-source headroom; native Stages 1–2 remain byte-identical. Android bounded native S2 is archived, but 300,000-command Android acceptance remains open. [Report](ITERATION44_REPORT.md) · [contract](WINDOWS_FULL192_PE.md).

---

# Iteration 43 status — Windows PE128 source-dependent code generation

An opt-in [standard-BF PE128 pipeline](WINDOWS_FULL128_PE.md) now supports **all eight instructions through 128 BF commands including loops**, emitting 3,072-byte PE32+ executables. Linux x64 CPU shim execution passed 100 cases (26 beyond the old ceiling) and 868 branch patch checks. Fresh Linux native Stages 1–2 self-compilation is byte-identical. **Windows loader execution, real Win32 API verification, and Windows-native compiler/S2 remain open**. Android bounded S2 is supported by historical device evidence; the 300,000-command goal has not been achieved. [Report](ITERATION43_REPORT.md) and [evidence](../evidence/iteration43_windows_full128.json).

---

# Iteration 42 status — Windows x64 machine-code execution checked on Linux

All eight standard Brainfuck instructions still compile through the bounded 64-command Windows PE writer. A [test-only Linux CPU harness](WINDOWS_LINUX_CPU_EXECUTION.md) executed the real generated x64 code with Win32-import test doubles: **164** differential source programs and **11** unchanged archived Windows images matched expected results, including byte I/O, loops, EOF and pointer traps. **The Windows loader and KERNEL32 were not used. Windows native self-hosting remains unimplemented.** The BF production emitter/source is unchanged, and Linux S2 native Stages 1–2 matched. Android bounded native S2 is still archived; 300,000-command support is outstanding. [Iteration 42 report](ITERATION42_REPORT.md) and [evidence](../evidence/iteration42_windows_x64_cpu_shim.json).

---

# Iteration 41 checkpoint — all eight Windows BF commands emitted

The new [Windows all-eight-command path](WINDOWS_FULL64_PE.md) emits 2,048-byte PE32+ images for up to **64 Brainfuck commands with nested loops**. Loop matching, signed branch arithmetic and final PE patching are implemented in standard BF and executed on Linux. **Windows loader, Win32 API runtime and Windows native self-hosting were NOT RUN**. The prior six-command backend is preserved. Linux's canonical **15,559-byte** BF compiler with **zero** fixed trailing padding remains native S2; Android bounded S2 is archived, its 300,000-command target unmet. See [Iteration 41 report](ITERATION41_REPORT.md) and [evidence](../evidence/iteration41_windows_full64.json). Historical notes follow.

---

# Iteration 40 checkpoint — Windows six-instruction linear PE backend

The new [Windows linear I/O backend](WINDOWS_LINEAR_IO_PE.md) generates BF-owned PE32+ images for `+ - > < . ,` from at most 64 executable commands, with imported Win32 byte I/O and deterministic x64 pointer traps. Its BF source, native Linux writer and static image tests pass; **no Windows loader/API execution** was performed. `[` and `]`, Windows-native compiler execution/S2, and Android's separate 300,000-command acceptance target remain outstanding. See [iteration report](ITERATION40_REPORT.md) and [evidence](../evidence/iteration40_windows_linear_io.json). Historical notes follow below.

---

# Current checkpoint — Iteration 39 bounded Windows BF compilation

A 10,831-command standard-BF stage now generates source-dependent PE32+ executables for **0–64** `+ - > <` commands, with BF-authored headers, x64 instruction slots, a 65,536-byte tape and checked pointer movement. Verified by native Linux BF-stage execution, BF reference comparisons and PE/x64 byte inspection. **Not executed on Windows; no I/O, loops or Windows S2.** Original Linux compiler and Android compiler are unchanged. Linux native Stage 1→2 passed again; Android bounded native S2 is recorded in archived Pixel 8 Pro evidence, and 300,000-command support remains unimplemented. [Contract](WINDOWS_LINEAR_PE.md), [Iteration 39](ITERATION39_REPORT.md).

---

# Current checkpoint — archived Android S2 and first Windows artifact

Android target: the new archive supplies [bounded Android S2 evidence](ANDROID_NATIVE_S2_AUDIT.md), with 14,575 executable BF commands in the target compiler and a 16,128-command compiler input limit; four compiler images and 14 on-device program results are archived and were audited offline. Target execution was not rerun here. The 300,000-command release target is unimplemented. Linux remains the same **15,559-byte** standard-BF source with **zero fixed trailing padding**, and fresh native Stage 1→2 compilers were byte-identical. Current Linux source limit remains 16,128 commands, leaving 1,269 slots relative to its 14,859 commands.

Windows x86-64 has an [initial PE32+ image emitter](WINDOWS_PE32_SEED.md) implemented as 6,194 standard BF instructions. It emits one fixed console ExitProcess executable, structurally verified only. Windows-native code execution, Brainfuck source compilation and self-hosting have **not** been demonstrated. [Iteration 38](ITERATION38_REPORT.md). Earlier sections are historical.

---

# Current state — Android USB device follow-up, 2026-10-13

The expanded BF AArch64 generated-program loader gate passed **13/13** fixtures on Pixel 8 Pro, Android 17/API 37, including **2,000 commands with loops**, binary I/O, EOF and tape traps. APK instrumentation passed **21 test executions**, including **634,229 parity comparisons**. Native BF remains slower than the strongest C transfer baseline in this session; the existing GM BF-to-C/JNI APK policies remain slower than warmed Java. Android-native compiler/S2, callable BF-native APK integration, larger source emission and Windows remain open. Canonical Linux BF source is unchanged at **15,559 bytes**. [Report](ANDROID_DEVICE_FOLLOWUP_20261013.md) and [device evidence](../evidence/android_device_20261013/device_verification.json) bind the new facts; the following snapshots retain their earlier claims.

---

# Iteration 37 current state — device gate prepared, not passed

The Brainfuck-owned AArch64 ELF pipeline remains bounded to 2,000 commands with loops. A thirteen-executable device test bundle and raw byte/status verification harness were created; offline ELF checks and 24 AArch64 simulator executions passed. **No Android device or adb is available in this environment.** Android loader execution is therefore NOT RUN, Android-native compiler/S2 is absent, and Windows is unimplemented. Linux Stage 1→2 still produces byte-identical 475,703-byte compiler ELFs, with cold Stage 0 NOT RERUN. The canonical source is unchanged at 15,559 bytes. See [Iteration 37](ITERATION37_REPORT.md), [Android device procedure](ANDROID_DEVICE_ACCEPTANCE.md), and [evidence](../evidence/iteration37_android_acceptance_preflight.json). Subsequent sections retain historical snapshots.

---

# Iteration 36 current state — 2,000 commands including loops

The opt-in Linux-hosted Android AArch64 path now produces executable ELF PIE images for **2,000 standard Brainfuck commands including loops** using reused, unchanged Brainfuck-owned two-byte bracket relocation, six ELF size classes, and BF-owned tape rebase. The focused suite passed 39 programs, 164 bracket pairs and 78 simulated executions. No Android loader/device run or Android-native compiler/S2 happened. Windows remains unimplemented. Linux compiler source is unchanged at **15,559** raw bytes, **14,859** BF instructions, **569** raw bytes below the 16,128-byte ceiling, and zero fixed output padding; native Stages 1→2 match byte-for-byte, cold Stage 0 not rerun. See [Iteration 36 report](ITERATION36_REPORT.md) and [evidence](../evidence/iteration36_wide_loops_2000.json). The following sections are historical snapshots.

---

# Project state — Iteration 35 tape relocation partial

The new opt-in Linux-hosted Brainfuck backend generates AArch64 PIE images with **up to 2,000 linear commands**, or **1,024 commands containing loops**, and six aligned file-size classes. The tape virtual address and startup pointer follow the writable segment as calculated by standard Brainfuck; RX length carries beyond 64 KiB are repaired. This has Linux-native BF-stage and AArch64-simulator verification, **not** Android loader/device execution. Native compiler self-hosting on Android, 300,000-command artifacts and the Windows PE backend remain open. Fresh Linux native Stage 1→2 replay is byte-identical; cold Stage 0 not rerun. The canonical compiler source is unchanged at **15,559** bytes with 14,859 commands and 1,269 executable-instruction slots of headroom and zero fixed trailing padding. See [Iteration 35](ITERATION35_REPORT.md).
---

# Project state — Iteration 34, Android four-class partial

**Newest verified capability:** the optional `--multiclass --loops` pipeline emits BF-generated AArch64 PIE images for **up to 1,024 standard Brainfuck instructions**, including loops, with Linux-native BF stage execution and AArch64 simulator testing. Four 16 KiB-aligned file-size classes now exist; the new boundaries are at commands 672 and 1013. The new BF relayout stage is 4,486 executable instructions and its Linux-native program is 143,767 bytes. Its source, binary and test results are bound in [Iteration 34 evidence](../evidence/iteration34_multiclass_elf.json). See [engineering report](ITERATION34_REPORT.md). The existing canonical Linux compiler is still **15,559 bytes of raw source**, 14,859 BF instructions, with **1,269 instructions** of headroom and **zero fixed trailing output padding**.

This remains a **partial** Android milestone. The simulated binaries were **not run under Android's loader**, there is **no Android-native compiler nor target-side self-hosting**, and 300,000-command native output remains unimplemented. The BF image has a fixed RW tape virtual address (`0x10000` segment and `0x10060` tape); it needs redesign before executable RX code reaches that region. Windows PE32+ generation has not begun. A separate independent BF seed interpreter run exhausted a 75-million-step limit on the new byte-heavy stage and is **inconclusive**. Older source-state claims below are preserved as **historical snapshots**, not the latest target matrix.

---

**Verification addendum:** 71 source programs, 8,137 branch-pair checks and 142 simulator runs passed in Iteration 34. Fresh native Linux Stage 1→2 compilation passed byte-for-byte; cold Stage 0, Android loader tests and the full release suite were not rerun. An independent 75-million-step seed-interpreter comparison was inconclusive. See [Iteration 34 report](ITERATION34_REPORT.md).

# Current status — Iteration 33 partial

The optional Android AArch64 **Brainfuck-owned** Linux-hosted cross-generation pipeline now compiles **512 BF commands with loops** using `--page-class --loops`, including the 330→331 ELF size-class transition. The new BF stage contains **2,848** instructions, and **66** source cases / **132** AArch64 simulator runs / **3,707** bracket pairs passed. The native Linux compiler source is unchanged at **15,559** bytes; the test recompiled it byte-identically through native Stage 1→2, with cold Stage 0 **not rerun**. Old 255 and 74 command writers remain bounded; new AArch64 executables have not run on Android hardware. Android-native compiler execution, native S2 and Windows PE32+ remain **UNIMPLEMENTED**. Next: broader BF ELF sizing and real Android loader execution. See [Iteration 33](ITERATION33_REPORT.md), [stage notes](../experiments/android_wide_slot_patch_512.bf.notes.md), [evidence](../evidence/iteration33_wide_slot_patch_512.json). Previous dated sections below are historical.

---

# Current state — Iteration 32 bounded loop relocation

The optional BF-only Android AArch64 path now supports **255 loop-containing commands** using `--page-class --loops` or `--dynamic --loops`. The default 74-slot writer is unchanged, and the two-class page writer still handles **512 linear** commands. The new patched images passed 136 Linux-hosted AArch64 simulator runs, 1,524 branch pair checks and independent BF-interpreter comparisons. Android device loader execution and an Android-native self-hosted compiler remain **UNIMPLEMENTED/UNVERIFIED**; Windows PE32+ remains absent. The fixed Linux compiler source is **15,559** bytes, 14,859 standard BF instructions, with **569** raw-source bytes headroom and **zero** fixed trailing output padding. Linux native Stages 1–2 match; cold Stage 0 not rerun. See [Iteration 32](ITERATION32_REPORT.md), [evidence](../evidence/iteration32_wide_slot_patch_255.json) and [stage notes](../experiments/android_wide_slot_patch_255.bf.notes.md).

---

# Current state — Iteration 31 partial file size classes

The Linux-hosted Brainfuck compiler pipeline can now produce **two size classes of Android AArch64 PIE images for up to 512 linear Brainfuck commands**, with `--page-class`. The BF writer emits 16,480-byte files for 0–330 commands and 32,864-byte files for 331–512 commands, with separate RX and RW load segments. **Bracketed programs remain limited to 74 commands** by the separate BF relocation patcher. The AArch64 program images have been simulated at two load biases, **not newly executed on Android**. The Android compiler itself does not execute or self-host on Android. Windows PE32+ remains unimplemented.

Source purity, Linux native BF compilation, 164 new simulated execution checks, 13 size boundary checks and focused regressions passed. Linux native self-hosted Stages 1–2 match the unchanged 475,703-byte compiler. Cold Stage 0 was not rerun. Documentation: [Iteration 31 report](ITERATION31_REPORT.md), [stage notes](../experiments/android_page_class_elf_wrapper.bf.notes.md), [test evidence](../evidence/iteration31_page_class_elf.json). The full release suite and device loader acceptance are not complete.

The following dated snapshots remain historical; older command limits must not be read as the limits of the latest optional pipeline.

---

# Current project state — Iteration 30 partial ELF code length

**Linux-hosted Brainfuck native compilation has extended linear AArch64 images to 255 commands.** A separate 9,087-instruction `.bf` module now computes ELF RX `p_filesz`/`p_memsz` from the command count and keeps the tape in a 16 KiB-aligned RW-only segment. The ELF file remains **16,480 bytes** within this size class; general file-size class switching is not implemented. The existing loop relocation path remains **74 commands**. The new code was tested in an AArch64 instruction simulator, **not on Android hardware**. No native Android compiler or Android self-hosting. Linux core `compiler/core.bf` remains **15,559 bytes** (14,859 instructions) with **569** bytes of raw-source headroom and **zero fixed trailing ELF padding** in its x86-64 backend. Native Linux Stages 1→2 were byte-identical again; independent Stage 0 was not repeated.

Verification: **79** linear cases, **6** loop cases, **170** emulator executions, all **256** counter values, two independent BF seeds; old Android and docs regressions retained. [Iteration 30 report](ITERATION30_REPORT.md), [source notes](../experiments/android_dynamic_elf_wrapper.bf.notes.md) and [evidence](../evidence/iteration30_dynamic_elf.json).

---

# Project state — Iteration 29 wide loop slot relocation follow-up, 2026-10-13

**Latest partial milestone:** The Linux-executed BF pipeline now applies BF-generated 26-bit AArch64 branch words into 48-byte slots, producing **fixed 4,192-byte Android AArch64 ELF PIE images for up to 74 ordinary Brainfuck commands including nested loops**. New source: [`../experiments/android_wide_slot_patch.bf`](../experiments/android_wide_slot_patch.bf), evidence: [`../evidence/iteration29_wide_slot_patch.json`](../evidence/iteration29_wide_slot_patch.json), report: [`ITERATION29_LOOP_FOLLOWUP.md`](ITERATION29_LOOP_FOLLOWUP.md). **85 simulated programs** and **390 bracket-pair patches** passed; those results are *not Android-device execution*. The original 10-command Android device results remain historical and separate. Dynamic ELF sizing, Android-hosted compiler execution/self-hosting and Windows PE remain absent. Fresh Linux native Stage 1–2 self-compilation matched the installed compiler byte for byte; cold Stage 0 was not rerun. Evidence: [`../evidence/iteration29_loop_linux_selfhost_replay.json`](../evidence/iteration29_loop_linux_selfhost_replay.json).

The earlier state snapshots below are dated history, not current backend limits.

---

# Project state — Iteration 29 extended AArch64 linear image, 2026-10-13

**Latest partial milestone:** Two new Brainfuck-native stages generate a 48-byte slot stream and a bounded **74-command linear** Android AArch64 PIE ELF, with Linux-host execution and two-load-bias instruction simulation. Native self-hosting on Android remains absent; no loop relocation is applied to these extended images, and ELF size is still 4,192 bytes. Evidence: [`../evidence/iteration29_extended_slots.json`](../evidence/iteration29_extended_slots.json); detailed report: [`ITERATION29_REPORT.md`](ITERATION29_REPORT.md). The prior ten-command path **still handles loops** and has its own historical Android-device evidence. The 74-command path only handles unbranched linear programs; no broad Android device capability is claimed from the new tests.

The following sections preserve the Iteration 28 snapshot and history. References there to the ten-command *current* cap describe the old loop pipeline as it existed then. Do not read them as a claim about the newly added linear path.

---

# Project state — Iteration 28 Android wide bracket pairing, 2026-10-13

## Classification

**Current work: Iteration 28 has BF-only wide bracket positions and matched-pair extraction executed on Linux, but the milestone remains PARTIAL because AArch64 relocation and ELF generation still stop at ten commands.** Iteration 26 was a verified contract/test-harness milestone, not a new BF compiler implementation. The archive's last numbered Android loop implementation evidence is Iteration 25. Additional Android native optimization and APK/GM benchmarks are dated **2026-10-12** and do not carry a new numbered source milestone. No `.bf` implementation or historical benchmark measurement was modified during D0 or Iteration 26. Iteration 26 added a Python test oracle, a versioned Android compiler protocol document, stage/source hash inventory and new evidence; it did not modify native compiler code. Target execution claims below are *existing archive evidence*, not retests on the present host.

## Current authoritative source and Linux

- **Canonical compiler:** `compiler/core.bf`, **15,559 raw bytes**, **14,859 Brainfuck instructions**, 1,269 instructions of headroom below the 16,128-instruction V0 compiler source ceiling. The raw byte arithmetic gives **569** bytes below 16,128 raw bytes; this is *not* a semantic raw-input limit because noninstructions are filtered.
- **Native Linux compiler:** static x86-64 ELF, **475,703 bytes**. Two independent Brainfuck seed interpreters and Linux native compiler Stages 0, 1 and 2 previously produced byte-identical ELF bytes. Classification: **S2 EXECUTED**.
- **Linux compiler behavior:** in-core ignored-character filtering, maximum **16,128 executable BF commands** and 255 levels of loops. ELF file size is `215 + 32 × executable-command-count`; **zero fixed trailing padding**. Every retained command takes four compiler-tape cells and 32 native slot bytes.
- **V0 target semantics:** zeroed 65,536-cell tape, unsigned wrapping 8-bit cells, EOF→zero, raw byte input/output, deterministic pointer-boundary traps. Exact semantic specification: [`BRAINFUCK_SPEC.md`](BRAINFUCK_SPEC.md).
- **Historical test evidence:** 178 reference correctness cases, 345 adversarial cases, source-filter validation, instruction/ELF checks and independent native bootstrap. Compiler-wide tape-region separation **is not formally proven**; header scratch cell 61 has only a conditional local proof plus eight executed witnesses.

See [`SELF_HOSTING.md`](SELF_HOSTING.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`COMPILER_TAPE_AUDIT.md`](COMPILER_TAPE_AUDIT.md), and source-hash-bound [`../compiler/core.bf.notes.md`](../compiler/core.bf.notes.md). Source and ELF hashes remain in [`../evidence/selfhost.json`](../evidence/selfhost.json) and [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json).

## Iteration 26 — protocol and hosted verification

- Adopted [`ANDROID_COMPILER_PROTOCOL_V1.md`](ANDROID_COMPILER_PROTOCOL_V1.md), freezing stdin `FF01`/`FF02` byte stuffing, one-byte output status, BF ownership of parsing/codegen, proposed diagnostic categories, target shell/loader assumptions, multi-pass bounded capacity strategy and deliberate lack of APK claims. This is a **DESIGN CONTRACT**, not an implemented scalable source processor.
- Executed `tests/verify_android_contract_v1.py`: provenance hashes for **8 BF stages**, **256 raw byte values**, **6 malformed wire cases**, **9 bounded compiled ELF images**, **14 AArch64 load-base simulator/reference comparisons**, **6 rejected invalid/oversized command sources**, 1 MiB raw transport rejection, and atomic CLI preservation passed. Details: [`../evidence/iteration26_contract.json`](../evidence/iteration26_contract.json).
- Ran **two native Linux self-compilations** of the unchanged authoritative source with the existing installed BF compiler. Both returned byte-identical **475,703-byte** ELF images with SHA-256 `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8`. The source SHA-256 remains `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`. This reconfirms a **causally linked native Stage 1→2 cycle**, not an independent cold Stage 0. Evidence: [`../evidence/iteration26_native_stages.json`](../evidence/iteration26_native_stages.json).
- `tools/check_docs.py`, `tests/verify_source_comments.py`, `tests/verify_target_workloads.py`, and the Android optimized-adapter test pass. The 178-case Linux correctness suite passed. A full `tools/verify_release.sh` attempt was **not completed** (stopped during the expensive compiler-tape audit). The Android filter integration and Linux emission suites also exceeded the local execution budget; the full Android branch pipeline was not rerun. Neither is marked passed. Android OS/device and Windows tests were not run.

## Iteration 27 — BF source scanner and count primitive (partial)

- Implemented [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf), **1,170 standard Brainfuck instructions**, with BF-owned streaming `FF01`/`FF02` decoding, instruction filtering and a **24-bit little-endian executable-command count**. Emitted instructions stream out; the entire source is not stored on the 65,536-cell tape. The final four output bytes carry count and status. The BF stage detects 24-bit overflow (instrumented test) and malformed wire inputs.
- Executed **37 Linux-native scanner fixtures** through the canonical Brainfuck-compiled scanner, including **300,001 executable commands**, byte carries at 256 and 65,536, ignored NUL/FF/comment text and six malformed wire rejections; also **six independent seed interpreter comparisons** and instrumented 24-bit counter overflow. The larger fixture is a **scanner-only throughput/capacity test**, not generated Android code. See [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json).
- Added opt-in `--scanner` to the existing Android BF pipeline transport adapter. **Nine** generated Android ten-slot image hashes matched its original filter path byte-for-byte. Four invalid source cases were rejected identically; an existing image was preserved after CLI rejection. The canonical Linux backend and historical default Android filter are unchanged. See [`../evidence/iteration27_scan_integration.json`](../evidence/iteration27_scan_integration.json).
- **At the end of Iteration 27**, general bracket metadata, wide offsets, streamed multi-pass code emission and large Android ELF output remained unimplemented. **Iteration 28 has since added BF-owned bracket metadata and pair matching; AArch64 relocation and emission remain unimplemented.** The Android output program still supports **no more than ten commands**. The BF scanner directly has a 24-bit counter; the opt-in adapter limits raw source to 1 MiB, and the scanner has not proven a full 300,000-command *compiler*.
- No Android device test, Windows test or newly completed independent cold Linux Stage 0 was performed for this partial slice. Do not upgrade the Android conformance level.

## Iteration 28 — wide BF bracket metadata and stack pairing (partial)

- Added [`../experiments/android_wide_bracket_metadata.bf`](../experiments/android_wide_bracket_metadata.bf) with **2,524 standard BF commands** and [`../experiments/android_wide_bracket_pairs.bf`](../experiments/android_wide_bracket_pairs.bf) with **1,707 standard BF commands**. The former records one-based 24-bit bracket positions and depth; the latter walks a bounded tape stack to extract matching position pairs. These are independent Linux-native programs produced by the canonical Brainfuck compiler.
- Executed **421 valid** paired oracle comparisons, **123 rejected** invalid streams, **16 independent interpreter** comparisons, a depth-255 success/depth-256 failure, instrumented 24-bit offset overflow, and positions in **300,002-command** inputs. All eight opt-in ten-slot Android ELFs remained byte-identical to the unchanged baseline. Evidence: [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json).
- Pair-input records are trusted from the first BF stage, not independently adversarially revalidated. The BF pair stack occupies at most 255 five-cell frames. **No scalable AArch64 branch encoder, image size calculation or relocator has been implemented.** The old emitter stays at **ten commands**, native Android compiler/self-hosting remain absent, and no new device execution took place.
- The authoritative Linux compiler source and ELF are unchanged. A **fresh native Linux Stage 1→2** recompile produced the same binary twice (two passing stages); independent cold Stage 0 was not rerun. See [`../evidence/iteration28_linux_native_replay.json`](../evidence/iteration28_linux_native_replay.json) and [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md).

## Android: native programs executed; native compiler is missing

- The separate BF-only AArch64 PIE pipeline (historical Iterations 21–25) accepts **all eight BF commands for at most ten executable instructions**. Six BF stages handle filtering, bracket metadata, branches and fixed ELF output; two later optional `.bf` stages perform small clear/transfer and resource optimizations. Python transports data and files, not code generation.
- The archive records **real shell execution on Pixel 8 Pro (Android 17/API 37)**, including nested loops and pointer traps. The optimization evidence reports **1,032 Android native program executions**, 444 reference/simulator comparisons, 37 independent BF-seed image comparisons and 1,542 BF/C/Rust byte/EOF checks.
- The measured optimized nine-command transfer program ran at **2.3514 ms** median against **2.3532 ms** for C direct echo in an interleaved 101-round fresh-process trial. The BF/C runtime ratio is **1.000762** by the report's speedup convention; the bootstrap 95% interval **0.972286–1.013517** includes inferior performance. The result is **NOT_PROVEN_FASTEST**. Neither general C/Rust parity nor full applications has been established.
- **No Android-native BF compiler executable, target-side S2 self-compilation, **integrated large-source Android compilation**, APK compilation or universal Android ABI support exists. The Linux-executed scanner is a partial ingestion primitive only.** Bounded ELF execution is not compiler self-hosting.

Detailed historical prototype chronology is in [`ANDROID_AARCH64_PROTOTYPE.md`](ANDROID_AARCH64_PROTOTYPE.md). Device-specific measurements and limitations: [`ANDROID_NATIVE_OPTIMIZATION.md`](ANDROID_NATIVE_OPTIMIZATION.md), [`ANDROID_DEVICE_BENCHMARK.md`](ANDROID_DEVICE_BENCHMARK.md).

## Windows and real projects

Windows x86-64 PE32+ native generation, native compiler execution and Windows self-hosting are **UNIMPLEMENTED**. Running independent C Brainfuck seed interpreters on Windows to generate *Linux* optimizer binaries is **not** Windows PE code generation.

The eleven audited GmailHideAds, TwitterHideAds and ThreadsHideAds BF policy files are 18,192–296,307 commands, above both current compiler input ceilings. They require host/ABI integration beyond V0 shell byte I/O. The G29 program has a separate signed 32-bit checked-cell profile. Whole native Android APK or Windows hardware-driver replacement is **not** established. See [`TARGET_WORKLOADS.md`](TARGET_WORKLOADS.md).

## Priority decision

Proceed **Android first, then Windows**, without modifying the eight-instruction language or losing Linux S2. [The new roadmap](IMPLEMENTATION_ROADMAP.md) estimates **14 Android iterations (26–39)**, **6 Windows (40–45)**, and **2 release qualification (46–47)**: **22 baseline**; allow **28–34 total** with contingency. The proposed **complete native Android compilation** acceptance target is 300,000 BF commands; wide BF **scanning and bracket matching** have been tested, but **not** native Android artifact generation at that size. [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md) defines exact successful coverage. The next pending engineering gate is the remainder of **Iteration 28: wide AArch64 relocations**. Complete any cold-bootstrap/full-release validation requirements before declaring a broader release gate passed.

## Changes in D0 (historical documentation pass)

Active roadmap, acceptance, README, state, targets, handoff, agent guidance, issue list and relevant current-stage notes are synchronized. Historical Iteration 18 documents, archived device benchmark data, compiler source and evidence remain unchanged. The separate [`../status/ROADMAP.json`](../status/ROADMAP.json) deliberately labels *plans* without rewriting the evidence-driven [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json).

## Iteration 28 follow-up — wide AArch64 branch words, not wide Android ELFs

A **13,985-command pure Brainfuck** wide encoder now accepts the prior BF native bracket-pair stream and writes **15-byte position-plus-AArch64-B-word records**. Its native Linux ELF was generated from the commented `.bf` source and tested against independent branch encoding/target oracles, including **300,000-command** metadata input and a bounded signed-26-bit reach limit of **2,796,201** source positions. Six legacy Android images stayed byte-identical when the diagnostic pass was enabled. See [`../evidence/iteration28_wide_branch_encoding.json`](../evidence/iteration28_wide_branch_encoding.json) and [`../experiments/android_wide_branch_encoding.bf.notes.md`](../experiments/android_wide_branch_encoding.bf.notes.md). This is **BF branch record encoding, not relocation application**: the Android ELF emitter stays at ten commands, is not dynamically sized, and has not executed the new branch veneer on Android. Iteration 28 remains partial, with the next blocker being a BF-owned variable-size slot emitter and patcher. The older wide-bracket full-suite retest timed out; fresh Linux self-hosting and Android device tests were not run in this follow-up.

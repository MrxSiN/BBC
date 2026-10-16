# Changelog

Every iteration, newest first. Entries are kept as they were written at the time, so older ones describe limits that later iterations removed. Evidence lives in [`evidence/`](evidence/), long reports in [`docs/`](docs/).

## Project rename — BrainfuckCC

The project is now **BrainfuckCC** (repository: https://github.com/MrxSiN/BrainfuckCC). The former names `brainfuckC`/`brainfuckc` and `brainfuck-native` are retired in maintained code and docs: the Android JNI test bridge is now Java package `org.brainfuckcc`, library `libbrainfuckcc_bridge.so` and property `brainfuckcc.bridge.absolutePath`. Archived `evidence/` and `build/` records keep their original names and paths as historical data. No compiler source, BF stage or emitted machine code changed.

---

## Iteration 65 — File backed callable relocation storage

The active Android AArch64 dynamic callable compiler now tracks BF generated relocation write positions on disk instead of retaining a growing Python set. The native code still comes exclusively from standard BF stages. Five baseline DSOs are byte identical and a 12,000 pair compilation passes structural and simulator checks. This is **not Android execution**. Device Bionic/ART/APK integration and Android native dynamic self hosting are still open; older paths remain fallbacks. [Engineering report](docs/ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

## Iteration 64 — Fail-closed native callable instructions and loops

The BF-authored dynamic AArch64 DSO compiler now validates its **native instruction templates, loop veneers, signed-64-bit relocation targets, callable prologue and epilogue** before publishing the output file. The scanner is independent host-side **validation only**; all compilation logic and emitted machine code remain in standard Brainfuck. 52 BF-generated DSOs, 104 local AArch64/reference comparisons, seven damaged-code/branch literal rejections, two atomic-output-preservation fault injections, and structural checks on 13 existing shared libraries passed. The iteration-63, DSO and JNI host regressions pass; the longer iteration-58 suite timed out and is **not counted as passed this iteration**. Android Bionic/ART/JNI execution, original app parity, and Android-native self-hosting remain unverified for this dynamic lane. Legacy paths remain fallbacks; the 100-million-command objective remains retired. [Engineering report](docs/ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md), [evidence](evidence/iteration64_dynamic_callable_native_integrity.json).

---

## Iteration 63 — Fail-closed dynamic callable shared objects

The resource-scaled BF-authored Android callable compiler now validates generated ELF64 DSO metadata **before publishing output**. A constant-prefix reader rejects broken program headers, dynamic symbol and string tables, ELF sizes, section layout, ABI marker and export metadata without rewriting the BF-produced bytes. The postflight check is host transport validation, not a non-BF code generator. In executed local tests, **240 BF-generated programs passed 960 differential AArch64 simulations**, 40 corrupt headers and four length mismatches were rejected, and a deliberately broken BF header preserved the previous output. A sparse 4 GiB+ file tests 64-bit header validation only, not compiled-code capacity. Existing DSO and Linux JVM JNI regressions pass. Actual Bionic, ART/JNI and installed APK execution of the new DSO remains unverified. [Verification guide](docs/ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md), [evidence](evidence/iteration63_dynamic_callable_integrity.json). The numerical 100-million objective is retired and old paths remain fallbacks.

---

## Iteration 62 — Installed APK callable acceptance prepared

The BF-owned dynamic AArch64 shared-object emitter remains unchanged. An **installable Android debug APK acceptance project** now packages nine unchanged BF-generated `.so` files and the host-only JNI bridge, then checks the app native library namespace through a nonce-bound result. Local Linux JVM C-stub tests and mock-device failure guards pass; **no Android APK was built or executed here** because Android SDK/NDK/Gradle/ADB/device are unavailable. Earlier shell ART/JNI tests are separate. Legacy compiler paths remain verification fallbacks and the old numerical compilation target remains retired. [Iteration 62 guide](docs/ITERATION62_ANDROID_APK_ACCEPTANCE.md), [adapter](tools/android_bfp1_bridge/apk_acceptance62.py), [evidence](evidence/iteration62_release_gates.json).

---

## Iteration 61 — Android ART/JNI callable acceptance path

The dynamic eight-command AArch64 Brainfuck compiler and its nine BF-generated callable `.so` fixtures are unchanged. New device acceptance invokes those libraries through **Android ART → Java → JNI → `dlopen` → `bfc_call_v1`**, in addition to the earlier native shell loader probe. On a Linux JVM, the same Java assertions passed nine **test-only native stub** cases and rejected a deliberately incorrect result. Mock-ADB tests verify strict device hash and transcript checks. **No Android device/SDK/NDK was available; ART/device success and APK parity are not claimed.** Fallback compiler paths remain until target tests pass. The 100-million-command target remains retired. [Iteration 61 report](docs/ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md), [host smoke evidence](evidence/iteration61_jni_host_acceptance.json), [device runner](tools/android_bfp1_bridge/device_acceptance61.py).

---

## Iteration 60 — Android BF callable loader acceptance preparation

Nine actual BF-generated AArch64 shared libraries now have a repeatable **device loader** acceptance bundle (nested loops, EOF, bounds traps, output-full, gas, zero-skip and persistent tape). All nine passed independent reference/AArch64 simulator comparison and ELF inspection; a host loader probe passed on Linux with a **test-only x86 native stub**, and the JNI bridge passed expanded Linux JVM zero-buffer and alias tests. **No Android device, Android NDK or ADB is present here, so Android `dlopen`, real JNI BF policy execution and APK parity remain unverified.** Compile/run on an arm64 device using the documented test command. Original BF compiler sources and output remain unchanged; older routes remain temporary fallbacks. [Iteration 60 report](docs/ITERATION60_ANDROID_LOADER_ACCEPTANCE.md), [local gate evidence](evidence/iteration60_loader_readiness.json), [device harness](tools/android_bfp1_bridge/README.md).

---

## Iteration 59 — BF-produced callable Android shared-object structure

The standard-BF all-eight-command dynamic callable compiler now emits an **AArch64 ELF shared object with an exported `bfc_call_v1` function**, BF-generated dynamic symbol/hash/section metadata, 16 KiB segment alignment, and checked wide code lengths. **13 DSO programs, 52 new AArch64 simulations, 15 wide-length cases, 13 native-code parity checks, and 13 ELF inspections passed.** Three original Gmail/Twitter policy sources produce the new `.so` structure. The JNI bridge ran on a **Linux JVM against a test-only native stub**, and an independent AArch64 consumer linked against the BF-produced DSO. **No Android loader/device JNI execution or new target self-hosting is claimed.** The numeric command-count target remains retired; older compiler lanes are fallbacks. [Report](docs/ITERATION59_DYNAMIC_CALLABLE_DSO.md), [DSO test evidence](evidence/iteration59_dynamic_callable_dso.json), [host bridge](tools/android_bfp1_bridge/README.md), [active roadmap](docs/ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

Run `python3 -m bootstrap.android_dynamic_callable59 examples/nested.bf -o policy.so` to produce a structural AArch64 shared library. The only authoritative native-code and header generation in the new path is executed standard Brainfuck.

---

## Iteration 58 — fully growing AArch64 callable loop compilation (Linux simulated)

The standard-BF dynamic callable compiler now handles **all eight Brainfuck instructions**, including 64-bit PC-relative nested-loop relocation, checked pointer movement and loop-entry budget enforcement. **59 source cases, 354 AArch64 simulator runs, four independent BF-stage interpreter comparisons, six byte-identical linear regressions, and 1,030 nested levels passed.** Three archived original policies (Gmail row, Gmail scope, Twitter action) compile into new callable images. **Android JNI loading, real device execution, all eleven app sources, and Android-native self-hosting remain unverified**. The 100-million-command numerical goal stays retired; bounded older paths are temporary fallbacks. [Report](docs/ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [evidence](evidence/iteration58_dynamic_callable_loops.json), [roadmap](docs/ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

## Iteration 57 — dynamic callable AArch64 compilation (loop-free milestone)

The new BF-owned callable path streams ordinary source bytes without a fixed source/record count, emits AArch64 native instructions for the six linear operators, and calculates 64-bit ELF segment lengths in Brainfuck. **60 source cases, 240 AArch64 simulator runs, 14 wide-header tests and five growing-source ELF examples passed.** Nested loops, Android-device execution and JNI integration remain open; this is **not fully dynamic callable compilation yet**. The **100-million-command objective is withdrawn**; resource-scaled callable correctness is now the sole active Android compiler track. Other compiler paths are temporary fallbacks and are not removed until the full dynamic path is validated. [Report](docs/ITERATION57_DYNAMIC_CALLABLE_LINEAR.md), [active roadmap](docs/ANDROID_DYNAMIC_CALLABLE_ROADMAP.md), [evidence](evidence/iteration57_dynamic_callable_linear.json).

---

## Iteration 56 — first Twitter policy through the callable Android compiler

An optional 3,631-command standard-Brainfuck prepass canonicalizes exact clear loops before the bounded callable IR resolver. The original [TwitterHideAds action policy](docs/ITERATION56_TWITTER_ACTION_CLEAR.md) (24,616 BF commands) now compiles into a **15,300-byte callable AArch64 ELF**, with 4,723 original RLE records reduced to 3,819. The native bytes match an independent encoder; 10 BF-source/IR frame comparisons pass. Gmail archived and valuefold images stay byte-identical. **No new Android execution or APK integration occurred**, and the underlying 4,096-record and 255-depth limits, remaining app policies and full 100M compilation remain open. [Roadmap](docs/ANDROID_APP_ROADMAP_ITERATION56.md).

---

## Iteration 55 — BF-owned Gmail constant-value stores (Linux verified)

The opt-in policy compiler now folds statically known zero-derived byte values into direct AArch64 constant stores. The original `row.bf` and `scope.bf` compile from source into **12,772-byte** and **12,964-byte** callable images, respectively, compared with the unmodified 13,064- and 13,168-byte Android-accepted baselines. **109 compiler differential programs**, **480 Gmail IR execution comparisons**, and **two independent BF interpreter cases** passed. The original Android images and production stages remain byte-identical, and fresh Linux compiler Stages 1 and 2 passed. **The new images have not been run on Android or benchmarked; no speedup is claimed.** See [the engineering report](docs/ITERATION55_GMAIL_VALUEFOLD.md), [the application roadmap](docs/ANDROID_APP_ROADMAP_ITERATION55.md), and [the evidence](evidence/iteration55_policy_valuefold.json).

---

## Iteration 54: original Gmail native policy replayed independently on Linux

The uploaded Android record now supports **nine device ELF loader passes**,
**bounded Android native S2**, and a **Gmail native-policy test APK** with
21 instrumentation runs and 634,229 Java-oracle parity comparisons. Fresh
Linux BF-stage replay produces the **same 13,064-byte row** and
**13,168-byte scope** AArch64 policy images, byte-for-byte. This is
independent Linux reproduction of the BF-owned compiler logic, **not new
Android device execution or a speed win**. Both Gmail BF native policies
remain slower than optimized C/Java baselines. See
[the engineering report](docs/ITERATION54_PROGRESS_REPORT.md),
[reproducibility contract](docs/ITERATION54_LINUX_GM_REPLAY.md) and
[the revised roadmap](docs/ANDROID_APP_ROADMAP_ITERATION54.md).

---

## Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](docs/ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

## Iteration 53 — BF-owned far-loop AArch64 ELF path

The experimental Android compiler now emits compact, dynamically sized, all-eight-instruction freestanding PIE ELFs with **64-bit PC-relative long loop jumps**. New 32-byte bracket templates and BF-owned 64-bit position/literal arithmetic replace direct AArch64 `B` branch reach limits. **57 small ELF programs / 114 AArch64 simulator runs passed**. A 296,307-command **synthetic** program produced a 3,686,824-byte ELF accepted by `readelf`; this was not an Android device run or an original application policy compilation. No JNI/DSO or 100M executable compilation acceptance is claimed. Read [the engineering report](docs/ITERATION53_LONG_RANGE_ANDROID_ELF.md), [roadmap](docs/ANDROID_DYNAMIC_ROADMAP_ITERATION53.md), and [evidence](evidence/iteration53_android_far_elf_tests.json).

---

## Iteration 52 checkpoint — dynamically sized compact AArch64 ELF (Linux-simulated)

The multi-stage standard-Brainfuck pipeline now produces complete freestanding AArch64 ET_DYN ELF images for all eight Brainfuck instructions, with dynamic compact code, BF-owned 64-bit native positions, file-backed loop matching, BF-owned signed B relocation and ELF headers. The 55-case differential suite passed 110 AArch64 simulations; a **synthetic** 296,307-command file generated a 3,686,784-byte ELF accepted by readelf. No Android loader/device execution, original application policy compilation, JNI/shared-library integration or new target self-hosting has occurred. Direct B reach still limits some loop spans. See [Iteration 52 contract](docs/ITERATION52_DYNAMIC_AARCH64_ELF.md), [test evidence](evidence/iteration52_android_dynamic_elf_tests.json), and [large synthetic evidence](evidence/iteration52_large_synthetic.json).

---

## Iteration 51 — compact eight-command output with BF native-coordinate bracket pairs

The [Iteration 51 proof](docs/ITERATION51_COMPACT_AARCH64_RELOCATION_LEDGER.md) integrates BF-generated compact AArch64 instruction templates for all eight commands, a repaired BF 64-bit native-word-position ledger, and dynamic file-backed BF bracket matching. Linux-hosted checks passed 86 cases, 1,025 nested brackets and a 7,502-command mixed-source case. **The result is an unrelocated ZIP bundle of raw code and pair coordinates, not a working Android ELF.** Complete ELF generation remains verified only up to 2,719 commands; actual application policy compilation and new Android device execution are still open.

---

## Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](docs/ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](docs/ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

## Iteration 49 — resource scaled native code streaming

A new [standard BF native slot stage](experiments/android_streaming_linear_slots.bf.notes.md) reads arbitrary raw source bytes and emits AArch64 linear instruction slots as a stream with **no built in source command count ceiling**. A 300,001-command program generated 14,400,048 native bytes and matched existing BF-owned templates. The host only frames and copies bytes, with optional caller supplied output quotas; it does not parse BF or emit instructions. **Not a runnable ELF:** brackets, scalable relocation, dynamic executable layout, JNI and the eleven real application policies remain open. The complete Android ELF backend still supports only 2,719 commands. [Report](docs/ITERATION49_DYNAMIC_ANDROID_STREAMING.md) and [evidence](evidence/iteration49_android_dynamic_stream.json). The 100M benchmark remains a target, not an artificial maximum or a completed native executable. Earlier iteration notes remain historical.

## BrainfuckCC — Android 100-million-command compiler objective

### Iteration 48 — source-to-pair 100M foundation

**Verified Linux-native Brainfuck stages:** 32-bit bracket events are now paired with their 32-bit opening/closing positions, including a real 100,000,002-byte source where one loop spans 100,000,001 commands. A separate framed scanner preserves the original Iteration 47 scanner interface. The pairing stack accepts 255 nesting levels and rejects level 256. See [the report](docs/ITERATION48_ANDROID_100M_PAIRING.md), [stage specification](experiments/android_100m_bracket_pairs.bf.notes.md) and [evidence](evidence/iteration48_android_100m_pairing.json).

**Not yet achieved:** compact native IR, scalable AArch64 loop displacement, ELF or shared-library emission beyond 2,719 commands, native 100M output, eleven Android policy kernels, and three APK parity tests. The Android-native S2 evidence remains bounded and historical. No release universality claim is made.


### Iteration 47 — direct 100-million-command target

**Source analysis only:** the [new standard-BF 32-bit scanner](docs/ANDROID_100M_CAPACITY.md) processes a real 100MB source file representing 100 million executable BF commands through generic raw-byte compression. It also emits verified 32-bit bracket positions across that range. The **native AArch64 compilation ceiling remains 2,719 commands** and the Android-native S2 compiler's historic input ceiling remains 16,128. This does **not** compile 100M commands into an ELF or APK. All eleven target application policy kernels remain uncompiled by this backend. The minimum target is now **100M commands per one source unit**, not 10M per unit. [Evidence](evidence/iteration47_android_100m_source.json).


**Application compatibility priority (Iteration 46 contract, not implemented):** [GmailHideAds, TwitterHideAds and ThreadsHideAds](docs/ANDROID_APPLICATION_ACCEPTANCE.md) are mandatory Android application workloads: 11 standard-BF policies, 1,312,912 commands total, up to 296,307 per file. Current 2,719-command Android code generation cannot compile them. Acceptance includes Android shared-library/JNI integration, original parity suites and installable APKs; the former 10M-per-unit stretch has been superseded by a 100M-per-unit target, not yet implemented. Brainfuck-only compiler logic remains mandatory. [Machine gates](status/ANDROID_APPLICATION_GATES.json).

---

## Iteration 45 — Android eight page class and 2,719 command support

The optional **Brainfuck-owned Android AArch64 ELF PIE pipeline** now emits sources with **up to 2,719 filtered Brainfuck commands, including loops** (`--multiclass --tape-relocated --loops`). A new standard-BF stage fixes the two RX size carries and the startup `ADRP` carry when the tape moves to `0x20000`. The previous 2,000-command image and the original Linux compiler are unchanged. The 300,000-command acceptance target is **not met**. AArch64 simulation and Linux-native BF stages passed; **the newly expanded images were not executed through an Android loader**. Android bounded native S2 remains historical device evidence, not proof of this new image limit. See [the stage contract](experiments/android_adrp_high_byte_class8.bf.notes.md), [engineering report](docs/ITERATION45_ANDROID_REPORT.md), and [machine evidence](evidence/iteration45_android_class8.json).

---

## Iteration 44 checkpoint — Windows BF PE compiler reaches 192 commands

The opt-in [Brainfuck-owned Windows x64 backend](docs/WINDOWS_FULL192_PE.md) generates **3,584-byte PE32+ executables for up to 192 executable `><+-.,[]` commands**, including nested loops. The 128-command path remains unchanged. **77** generated programs executed on the Linux x64 CPU with test-only Win32 shims, 990 branch targets were checked, and 14 target-side Windows executables were prepared but **not executed on Windows**. Native Windows compiler execution/S2 remain unimplemented. Fresh Linux Stage 1–2 self-compilation matched; archived Android bounded S2 remains separate and its 300,000-command goal is open. [Report](docs/ITERATION44_REPORT.md) · [evidence](evidence/iteration44_windows_full192.json).

---

## Iteration 43 checkpoint — Windows BF compiler reaches 128 commands

The optional [standard-BF Windows x64 backend](docs/WINDOWS_FULL128_PE.md) now emits 3,072-byte PE32+ binaries for up to **128** executable `><+-.,[]` commands, including nested loops. The source-dependent x64 slots and branch relocations are entirely Brainfuck-owned; the original 64-command backend remains intact. **100** differential programs executed on a Linux x64 CPU with test-only Win32 shims, including **26** over the previous 64-command limit. No real Windows loader test has run, and Windows-native self-hosting is still absent. Linux native S2 replay passed; Android bounded native S2 stays archived, with 300,000-command acceptance still open. [Report](docs/ITERATION43_REPORT.md) · [evidence](evidence/iteration43_windows_full128.json).

---

## Iteration 42 checkpoint — Windows-generated x64 executed on Linux with test API shims

The all-eight-instruction [Windows BF compiler path](docs/WINDOWS_FULL64_PE.md) is still limited to **64 commands**. An independent [test-only x64 execution harness](docs/WINDOWS_LINUX_CPU_EXECUTION.md) now runs its actual PE `.text` instructions on the Linux x86-64 CPU using `ms_abi` Win32 import shims: **164** differential source cases (162 clean, two expected pointer traps), plus the **11** unchanged Windows 41 smoke images, passed. This **does not** exercise the Windows loader or real KERNEL32 and does not establish Windows S1/S2. The authoritative BF production sources are unchanged. Linux S2 replay remains byte-identical; Android bounded S2 remains archived and its 300,000-command objective open. [Report](docs/ITERATION42_REPORT.md) · [evidence](evidence/iteration42_windows_x64_cpu_shim.json).

---

## Active checkpoint — Iteration 41 Windows all eight BF instructions

A new [Brainfuck-owned Windows nested-loop PE path](docs/WINDOWS_FULL64_PE.md) now accepts **0–64 executable `><+-.,[]` instructions**, including matched nested loops. Three new standard-BF stages encode signed x64 loop jumps, select native slots and patch 2,048-byte PE32+ console artifacts. **252** generated-image checks and **1,610** bracket-pair checks passed on Linux. **Windows loader execution remains NOT RUN**; a [target-side smoke bundle](build/windows41_acceptance/manifest.json) is prepared. The Linux compiler's **15,559-byte** authoritative BF source and zero trailing fixed padding are unchanged; native S2 replay passed. Android's bounded native S2 remains archived; the 300,000-command goal is still open. See [Iteration 41 report](docs/ITERATION41_REPORT.md) and [evidence](evidence/iteration41_windows_full64.json).

---

## Active checkpoint — Iteration 40 Windows linear PE with BF-owned byte I/O

A new [standard-Brainfuck Windows linear byte-I/O backend](docs/WINDOWS_LINEAR_IO_PE.md) now accepts up to **64 linear `+ - > < . ,` instructions** and emits a 2,048-byte PE32+ console image with Win32 `GetStdHandle`, `ReadFile`, `WriteFile` and `ExitProcess` imports. It is **Linux-executed/structurally verified only**; Windows loader execution, loops, Windows-native compiler and Windows S2 remain open. Read the [Iteration 40 report](docs/ITERATION40_REPORT.md) and [evidence](evidence/iteration40_windows_linear_io.json). Original Linux compiler and Android native S2 evidence are preserved. Android's 300,000-command target remains outstanding.

---

## Current checkpoint — Iteration 39 Windows bounded source compilation

The Windows path now has a [standard-Brainfuck compiler for 64-command linear programs](docs/WINDOWS_LINEAR_PE.md), supporting `+`, `-`, `>` and `<` with a zero-initialized 65,536-byte tape, wrapping arithmetic and checked pointer moves. Its **2,048-byte PE32+** output is verified structurally and by source-dependent x64 code inspection on Linux; **nothing from this new path has run on Windows**. Byte I/O, loops, Windows-native compiler execution and S2 remain open. [Report](docs/ITERATION39_REPORT.md) and [evidence](evidence/iteration39_windows_linear_pe.json).

Existing Linux S2 is unchanged and fresh native Stage 1 and Stage 2 match byte-for-byte. Archived Android native S2 evidence remains valid for the 16,128-command bounded compiler; the 300,000-command goal is still unimplemented. Previous checkpoints below retain their dated status.

---

## Current checkpoint — Android native S2, Windows PE32+ started

The uploaded October 13 archive includes [recorded Android-native S2 evidence](docs/ANDROID_NATIVE_S2_AUDIT.md): a 14,575-instruction standard-BF compiler rebuilt itself across four byte-identical stages on Pixel 8 Pro/API37. We validated the archived stage hashes and 14 recorded program outputs here; no Android device was connected in this iteration. Android remains **bounded at 16,128 compiler input commands** and the 300,000-command goal is open. The canonical **15,559-byte** Linux compiler remains unchanged and fresh native Stages 1–2 passed.

Windows work has now started with a [Brainfuck-owned PE32+ exit-image primitive](docs/WINDOWS_PE32_SEED.md): 6,194 BF instructions emit a 1,536-byte `.exe` imported from `KERNEL32.dll`; Linux-stage and independent BF interpreter outputs agree. This is **STRUCTURAL, NOT executed on Windows**, and is not a Windows Brainfuck compiler. [Iteration 38 report](docs/ITERATION38_REPORT.md). Historical checkpoints follow.

---

## Android USB device follow-up — 2026-10-13

The expanded BF-generated Android path now passes **13 real-device tests**, including the **2,000-command loop program**, on Pixel 8 Pro, Android 17/API 37. The isolated GM release APK was rebuilt and executed: **21 test executions** and **634,229 parity comparisons** passed. This APK uses GM's BF-to-C/JNI backend; BrainfuckCC still emits shell executables and has no Android-native compiler/S2 or callable APK backend.

Performance target remains unmet. Native BF took **2.2204 ms** versus **2.1646 ms** for the fastest C transfer baseline; warmed ART AOT Java policies beat BF/JNI by roughly **5–12×**. See [device report and diagnosis](docs/ANDROID_DEVICE_FOLLOWUP_20261013.md), [raw loader results](evidence/android_device_20261013/device_verification.json), and [status](status/CONFORMANCE_MATRIX.json). Older checkpoints below describe their original test environments.

---

## Iteration 37 — Android loader acceptance package ready, device execution pending

The experimental standard-Brainfuck AArch64 pipeline still compiles **up to 2,000 commands including loops**. Iteration 37 adds [13 ready-to-run Android shell fixtures](docs/ANDROID_DEVICE_ACCEPTANCE.md) and an audited `adb` transport, with **24 Linux-hosted AArch64 simulator executions passed**. No Android loader/device execution occurred, and the Android compiler still does not run or self-host on Android. The canonical Linux BF compiler remains S2. See the [report](docs/ITERATION37_REPORT.md) and [offline evidence](evidence/iteration37_android_acceptance_preflight.json). Windows PE32+ remains unimplemented.

---

## Iteration 36 checkpoint — Brainfuck owned Android 2,000-command loops

**Latest verified capability:** `--multiclass --tape-relocated --loops` generates AArch64 PIE images for up to **2,000 standard Brainfuck commands with loops**, reusing the unchanged two-byte BF slot patcher. Linux-native BF stages and AArch64 simulations passed; **no new Android loader/device execution and no Android-native compiler/self-hosting**. The authoritative Linux compiler remains unchanged. The remaining 300,000-command target and Windows PE32+ are not implemented. See [Iteration 36 report](docs/ITERATION36_REPORT.md), [test](tests/verify_android_wide_loops_2000.py) and [evidence](evidence/iteration36_wide_loops_2000.json). Older snapshots follow.

---

## Iteration 35 checkpoint — Brainfuck owned Android tape relocation

**Current Iteration 35 status:** A new opt-in Brainfuck-owned Android AArch64 tape-rebase stage now supports **2,000 linear commands** or **1,024 commands with loops** through `--multiclass --tape-relocated` (add `--loops` for bracketed input). It relocates the tape to a safe page-aligned virtual address, patches AArch64 startup, and repairs RX segment lengths beyond 64 KiB. Its generated ELF images are **Linux-hosted AArch64 simulator verified only**, not Android-loader/device verified. The Linux Brainfuck compiler remains S2 self-hosted; the Windows PE32+ backend and Android-native compiler/self-hosting are not implemented. Read [the Iteration 35 report](docs/ITERATION35_REPORT.md), [source notes](experiments/android_tape_rebase.bf.notes.md), and [evidence](evidence/iteration35_tape_rebase.json).
---

## Iteration 34 checkpoint — four aligned AArch64 ELF size classes

The optional Linux-hosted **standard-Brainfuck Android AArch64 compilation pipeline** now supports **up to 1,024 executable Brainfuck commands with loops** through `--multiclass --loops`. The new BF relayout stage extends the page-class artifact sizes to 16,480, 32,864, 49,248 and 65,632 bytes. All new native code, loop relocations and final ELF layout are Brainfuck-owned. These images have Linux-hosted AArch64 **simulator evidence**, not Android-loader execution. The Android compiler is not running or self-hosting on Android; Windows PE32+ is unimplemented. The older 74, 255 and 512 command modes are unchanged.

Run `python3 tests/verify_android_multiclass_elf.py` and consult the [Iteration 34 report](docs/ITERATION34_REPORT.md), [BF stage notes](experiments/android_multiclass_elf_relayout.bf.notes.md) and [evidence](evidence/iteration34_multiclass_elf.json). The historical checkpoints below retain their original claims **as of those iterations**, not as current limits.

---

**Verification addendum:** 71 source programs, 8,137 branch-pair checks and 142 simulator runs passed in Iteration 34. Fresh native Linux Stage 1→2 compilation passed byte-for-byte; cold Stage 0, Android loader tests and the full release suite were not rerun. An independent 75-million-step seed-interpreter comparison was inconclusive. See [Iteration 34 report](docs/ITERATION34_REPORT.md).

## Iteration 33 checkpoint — BF loops through 512 commands

The optional Linux-hosted **Brainfuck-only Android AArch64 pipeline** now generates **up to 512-command executables with nested/sequential loops**, including the 330→331 command ELF-size transition. Run `python3 tests/verify_android_wide_slot_512.py` or `python3 bootstrap/run_android_extended.py INPUT.bf OUTPUT.elf --page-class --loops`. There are two file classes: 16,480 bytes through 330 commands and 32,864 bytes thereafter. The previous `--dynamic --loops` 255-command and default 74-command paths are unchanged. New images have **AArch64 simulator evidence only**; Android-native compiler execution, Android-native S2, the 300,000-command target and Windows PE32+ remain absent. Fresh Linux native Stages 1–2 reproduced the same **475,703-byte** compiler. Cold Stage 0 not rerun. See [Iteration 33 report](docs/ITERATION33_REPORT.md), [BF source notes](experiments/android_wide_slot_patch_512.bf.notes.md) and [evidence](evidence/iteration33_wide_slot_patch_512.json). The following sections are historical snapshots.

---

## Brainfuck Native — Iteration 32 partial checkpoint

A second **Brainfuck-authored** Android AArch64 loop patcher now handles **up to 255 executable commands containing nested or sequential loops**, using `--dynamic --loops` or `--page-class --loops`. The legacy default loop path still accepts 74 commands. The `--page-class` writer continues to support 512 **linear** commands and two ELF file-size classes; loops crossing the 331-command size-class boundary are **not yet supported**. The new 255-command images passed Linux-hosted AArch64 instruction simulation and independent BF-seed comparisons, **not Android loader execution**. Android-native compiler self-hosting and Windows-native PE remain absent.

Run `python3 tests/verify_android_wide_slot_255.py` and read [Iteration 32 report](docs/ITERATION32_REPORT.md) and [source notes](experiments/android_wide_slot_patch_255.bf.notes.md). Linux native Stages 1–2 remain byte-identical; cold Stage 0 was not repeated. The original compiler source remains 15,559 raw bytes, 14,859 executable commands and zero fixed trailing ELF padding.

---

## Brainfuck Native — Iteration 31 checkpoint

The experimental **BF-only Android AArch64 ELF pipeline** now supports up to **512 linear Brainfuck commands** through the opt-in `--page-class` writer, with two actual ELF file sizes: **16,480** and **32,864 bytes**. The BF-owned loop branch patcher remains limited to **74 commands**. The images passed AArch64 simulator checks on Linux and ELF inspection, **not Android device execution**. The full Android-native compiler and Windows PE32+ backend remain outstanding. Linux x86-64 Brainfuck self-hosting still passes native Stages 1–2.

```sh
python3 tests/verify_android_page_class_elf.py
printf '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.' > /tmp/page-class.bf
python3 bootstrap/run_android_extended.py /tmp/page-class.bf /tmp/page-class.elf --page-class
readelf -Wl /tmp/page-class.elf
```

Read the [Iteration 31 engineering report](docs/ITERATION31_REPORT.md), [updated state](docs/STATE.md) and [test evidence](evidence/iteration31_page_class_elf.json). The earlier material below describes historical milestones and earlier code paths, **not the latest command ceiling**.

---

## Iteration 30 — Android PIE RX layout improvement

**Experimental BF-owned Android output now supports 255 linear commands** through `--dynamic`, or up to **74 commands with loops** through `--dynamic --loops`. The new 9,087-instruction standard-Brainfuck ELF writer computes the mapped executable size but emits a **16,480-byte 16 KiB-aligned image** for every supported count; variable full-file sizing and Android device execution are **not yet proven**. Linux native compiler self-hosting Stages 1–2 still produce the same **475,703-byte ELF**. The canonical `compiler/core.bf` (15,559 bytes, 14,859 BF instructions, zero fixed Linux ELF padding) is unchanged.

```sh
python3 tests/verify_android_dynamic_elf.py
printf '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.' >/tmp/bf255.bf
python3 bootstrap/run_android_extended.py /tmp/bf255.bf /tmp/partial-android.elf --dynamic
readelf -Wl /tmp/partial-android.elf
```

Technical results: [Iteration 30 report](docs/ITERATION30_REPORT.md), [stage notes](experiments/android_dynamic_elf_wrapper.bf.notes.md) and [machine-readable evidence](evidence/iteration30_dynamic_elf.json). Linux simulations are not Android device proof; an Android-native compiler and Windows backend remain outstanding.

---

## Iteration 29 wide loop relocation update

The opt-in `bootstrap/run_android_extended.py --loops` path now integrates BF-native 24-bit bracket pairing, AArch64 26-bit branch encoding, BF slot patching, and the fixed **74-command** ELF wrapper. Linux-executed BF stages and **85 two-base AArch64 program simulations** pass; **Android-device execution of these new images and Android-native compiler self-hosting have not occurred**. Dynamic ELF layout and source capacity remain blockers. See `docs/ITERATION29_LOOP_FOLLOWUP.md` and `evidence/iteration29_wide_slot_patch.json`.

---

## Brainfuck Native

A native compiler written in **standard Brainfuck**. The language remains the original eight commands, `><+-.,[]`; no hidden C/Rust compiler builds the native output.

**Current project status (2026-10-13, Iteration 29 partial linear ELF work):** Linux x86-64 is self-hosted at **S2 EXECUTED**; fresh native Stages 1→2 were repeated in Iteration 29 (not a new cold Stage 0). Experimental native AArch64 Brainfuck programs have **executed on Android**, but the Android compiler **does not yet execute or self-host on Android**. A Windows x86-64 PE32+ compiler is **not implemented**. Historical Android device results were checked against the archive, not rerun here. Iteration 26 added the Android transport contract. Iteration 27 added a standard-BF streamed scanner. Iteration 28 adds BF-owned 24-bit bracket indexing and matching on Linux, tested across 300,002-command inputs. The historical Android loop-capable ELF generator remains limited to ten commands; a separate newly verified BF-native **linear-only** path generates 74-command ELFs in Linux-hosted instruction simulation.

### Android first, Windows second

The original plan totals **22 engineering iterations after documentation pass D0**: **14 Android (26–39)**, **6 Windows (40–45)** and **2 cross-platform release gates (46–47)**. Allow **28–34 total** with engineering contingency; neither number is a calendar commitment. Android means a universal **V0 Brainfuck** compiler for a *documented arm64-v8a shell environment*, not arbitrary source sizes, every Android ABI, APK integration or system APIs. The proposed validation target is **at least 300,000 BF commands**, compared with ten commands in the loop-capable emitter and 74 in the new linear-only emitter. **Iteration 26 completed the [Android protocol contract](docs/ANDROID_COMPILER_PROTOCOL_V1.md), Iteration 27 added wide scanning, Iteration 28 added bracket pairing and branch records, and Iteration 29 added bounded 74-command linear emission. None completes general loop-capable or dynamically sized Android code generation.** See the [iteration-by-iteration roadmap](docs/IMPLEMENTATION_ROADMAP.md) and [explicit platform acceptance contract](docs/PLATFORM_ACCEPTANCE.md).

### What exists now

| Capability | Classification and limit |
|---|---|
| Linux x86-64 static ELF native compiler | **S2 EXECUTED**; source compiles itself through byte-identical Stages 0–2 |
| Linux BF source filtering | **EXECUTED**; standard ignored characters excluded from code slots |
| Linux source size | **16,128 executable commands maximum**; 255 levels of nesting |
| Android AArch64 experimental compiler pipeline | **EXECUTED generated programs on Pixel 8 Pro, Android 17/API 37**; 10 commands maximum; separate BF-only compilation stages |
| Android BF wide bracket metadata and pairing | **EXECUTED on Linux host**, 421 valid/123 rejected test cases, 24-bit positions through 300,002 commands and nesting up to 255; **not yet AArch64 relocation** |
| Android BF 74-command linear ELF path | **EXECUTED Linux BF stages + AArch64 simulator**, not device execution; all six linear instructions, brackets explicitly rejected, fixed ELF size |
| Android BF source scan primitive | **EXECUTED on Linux host**; up to 300,001 commands tested, BF-owned byte filtering and 24-bit count; **not Android codegen** |
| Android BF-owned optimized programs | **MEASURED** small tests; 1,032 native runs, but speed leadership over fastest C baseline **not proven** |
| Android native compiler and Android-native self-compilation | **UNIMPLEMENTED** |
| Windows x86-64 PE32+ emitter/native self-compilation | **UNIMPLEMENTED** |
| Full APKs and Android/Xposed policy application compatibility | **UNVERIFIED / BLOCKED** by source capacity, host ABI and integration contracts |

The authoritative [`compiler/core.bf`](compiler/core.bf) remains **15,559 source bytes**, with **14,859 executable BF instructions**. It emits a **475,703-byte** native Linux compiler ELF. Exact emitted Linux size is `215 + 32 × executable command count`, with zero fixed trailing file padding. The 65,536-byte tape uses unsigned 8-bit wrapping cells, zero initialization, EOF-zero input and deterministic out-of-range traps. These are V0 profile facts, not claims of full compiler-memory proof.

For Android, the ten-command limit applies to the original **loop-capable** experimental pipeline. The separate 74-command path does not yet support loops. Its original Linux-hosted structural experiments, later device execution, optional BF-owned optimizations and GM benchmark are documented separately. The strongest Android BF median was 2.3514 ms vs. 2.3532 ms for C direct echo; its confidence interval includes a tie or loss, so **NOT_PROVEN_FASTEST** is the correct conclusion.

### Verify the Android contract on Linux

```sh
python3 tests/verify_android_contract_v1.py
```

This tests existing ten-command BF code generation and transport. It does **not** execute an Android-native compiler or prove 300,000-command input handling. Source/compiler hashes were retained across Iteration 26.

### Try the new Android BF source scanner on the Linux host

```sh
python3 tests/verify_android_source_scan.py
python3 tests/verify_android_source_scan_integration.py
printf '+++.\n' >/tmp/android_tiny.bf
python3 bootstrap/run_android_loops.py /tmp/android_tiny.bf /tmp/example_android.elf --scanner
```

The scanner compiles itself through the existing Linux BF compiler and streams recognized source bytes plus a three-byte count. The optional Android adapter confirms that its scanner mode makes the **same 4,192-byte images** as the original bounded pipeline for accepted ten-command programs. The scanner's ability to process large sources **does not make the emitter accept large sources**. The CLI sample is four executable commands and therefore fits the original ten-command emitter. Larger sources are still rejected at the following BF stages without installing a partial executable.

### Check wide bracket pairing without changing the Android image

```sh
python3 tests/verify_android_wide_brackets.py
python3 bootstrap/run_android_loops.py /tmp/android_tiny.bf /tmp/example_android.elf --scanner --wide-brackets
```

The additional BF-only parser and stack stage generate matched opening/closing position records. The adapter checks their success status before using the existing ten-slot emitter. **This is not large-program Android code generation.** [Stage details](experiments/android_wide_bracket_pairs.bf.notes.md) and [Iteration 28 report](docs/ITERATION28_REPORT.md).

### Test the new 74-command Android linear ELF path

```sh
python3 tests/verify_android_extended_slots.py
printf '++++++++++++++++++++.\n' >/tmp/android_linear.bf
python3 bootstrap/run_android_extended.py /tmp/android_linear.bf /tmp/android_linear.elf
readelf -l /tmp/android_linear.elf
```

The **new BF-only slot emitter and ELF wrapper** can generate 4,192-byte AArch64 PIE executables with **up to 74 linear commands** (`><+-.,`), exceeding the earlier ten-command limit. The wider fixed code window contains padded NOP slots; this is *not* a dynamically sized image. The extended adapter rejects brackets until the wide BF relocation records are actually applied to slots. All new execution comparisons were **Linux-hosted instruction simulations**, not Android device tests. The old ten-command loop-capable pipeline remains available unchanged. Read [Iteration 29](docs/ITERATION29_REPORT.md) and its [evidence](evidence/iteration29_extended_slots.json).

### Reproduce the Linux baseline

```sh
python3 bootstrap/run_compiler.py examples/hello.bf /tmp/hello.elf
chmod +x /tmp/hello.elf
/tmp/hello.elf
sh tools/verify_release.sh
```

Development verification uses Python test/transport code, two independent C Brainfuck interpreters as cold-bootstrap seeds, and ELF inspection tools. They do **not** parse BF or generate/patch production machine code. After a native compiler is already built, its BF compilation logic executes in native code. This archive includes existing binaries and captured evidence, not a promise that platform device tests can be rerun on any host.

### Documentation map

- [Actual implementation state](docs/STATE.md), [target maturity](docs/TARGETS.md), [self-hosting evidence](docs/SELF_HOSTING.md), [compiler architecture](docs/ARCHITECTURE.md).
- [22-iteration Android-first plan](docs/IMPLEMENTATION_ROADMAP.md), [what “universal” means](docs/PLATFORM_ACCEPTANCE.md), [Android V1 compilation protocol](docs/ANDROID_COMPILER_PROTOCOL_V1.md), [blockers](docs/OPEN_ISSUES.md), [next engineering handoff](docs/HANDOFF.md).
- [Wide bracket metadata](experiments/android_wide_bracket_metadata.bf.notes.md), [matching stack](experiments/android_wide_bracket_pairs.bf.notes.md), [Iteration 28 evidence](evidence/iteration28_wide_brackets.json), [Iteration 28 report](docs/ITERATION28_REPORT.md).
- [Wide 74-slot code emission](experiments/android_wide_slot_emitter.bf.notes.md), [bounded ELF wrapper](experiments/android_bounded_elf_wrapper.bf.notes.md), [Iteration 29 report](docs/ITERATION29_REPORT.md).
- [BF source scan implementation notes](experiments/android_source_scan.bf.notes.md), [Iteration 27 evidence](evidence/iteration27_source_scan.json), [Android executable and optimization evidence](docs/ANDROID_NATIVE_OPTIMIZATION.md), [Android historical prototypes](docs/ANDROID_AARCH64_PROTOTYPE.md), [benchmarks](docs/BENCHMARKS.md), [real application workload audit](docs/TARGET_WORKLOADS.md).
- [Normative V0 semantics](docs/BRAINFUCK_SPEC.md), [original project requirements](docs/PROJECT_REQUIREMENTS.md), [evidence-based status matrix](status/CONFORMANCE_MATRIX.json), [planning-only machine-readable roadmap](status/ROADMAP.json).

The historical requirements document and numbered-iteration evidence have been left intact. A plan does not move a target from **UNIMPLEMENTED** to **EXECUTED**. Brainfuck remains Brainfuck; the compiler still has to compile itself on each claimed platform.

### Verify wide branch words without changing existing Android output

```sh
python3 tests/verify_android_wide_branch_encoding.py
python3 bootstrap/run_android_loops.py /tmp/android_tiny.bf /tmp/example_android.elf --scanner --wide-branches
```

The experimental **13,985-command Brainfuck** encoder emits AArch64 `B` machine-code words with 26-bit signed displacement from real 24-bit BF-owned matched bracket pairs, including tested **300,000-command** sources. It remains a **diagnostic stage on Linux**: the adapter still uses the original **ten-command AArch64 ELF emitter** for final artifacts. Longer BF sources cannot yet be compiled to Android. [Branch encoding record contract](experiments/android_wide_branch_encoding.bf.notes.md), [follow-up report](docs/ITERATION28_REPORT.md), [execution evidence](evidence/iteration28_wide_branch_encoding.json).

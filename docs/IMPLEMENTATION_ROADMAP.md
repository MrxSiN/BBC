# Iteration 65 — Dynamic callable relocation host scaling

The current Android callable path uses sparse file backed patched word occupancy rather than growing Python relocation sets. Device runtime acceptance, original policy parity and native dynamic compiler self hosting remain open. The 100 million command target is retired. [Current report](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 64 — Native callable postflight verified locally

The new all-eight BF compiler path now rejects corrupted AArch64 instruction templates, callable entry/return code and signed-64-bit loop relocations, as well as ELF metadata, before publishing shared libraries. Independent validation only; Brainfuck code generation is unchanged. Next actual blocker: load the newly generated libraries with Android Bionic and execute them under JNI/ART and the installed APK; then verify all eleven original policy sources and app parity, and prove native Android dynamic-compiler self-hosting. Do not remove legacy lanes until replacement acceptance passes. No fixed numerical compiler command target. [Report](ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md).

---

# Iteration 63 — Android shared-object integrity gate complete locally

The dynamic all-eight Brainfuck callable path now rejects malformed ELF export and loader metadata before publishing artifacts. This adds only validation of BF-produced bytes, not Python/C code generation. The AArch64 differential and mutation regressions pass on Linux. Next: actually load BF-generated libraries under Android Bionic and ART/JNI, execute the test APK on device, bring in the remaining eight pinned original BF policies and verify full original app parity, then prove Android-native self-hosting. Keep old bounded/freestanding paths until those target gates pass. No fixed command-count target has been reintroduced. [Iteration 63 report](ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md).

---

# Iteration 62 — APK namespace acceptance ready for device verification

The current path is **fully dynamic BF-owned callable codegen**, followed by real Android loader acceptance and native compiler self-hosting. An installed-APK test harness now checks nine BF-produced policies in the app linker namespace (via JNI), but has only passed host C-stub and mocked ADB tests. Next run the APK, resolve real Bionic/ART defects, compile the other eight source policies, verify installed app behavior and Android-native S2, and only then delete fallback compiler routes. No numerical 100M goal is active. [Technical acceptance](ITERATION62_ANDROID_APK_ACCEPTANCE.md).

---

# Iteration 61 active Android integration gate

Run the BF-produced DSO through real Android Bionic loading and the added ART/JNI acceptance suite, then verify APK linker namespace and original application parity. The ART harness is tested with a Linux JVM and host **test-only C stubs**, not real Android. The Brainfuck source and codegen are unchanged in iteration 61. Old bounded/freestanding paths remain fallbacks until the dynamic callable path is device-verified. The prior 100-million-command goal is retired. [Execution instructions](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md).

---

# Iteration 60 — actual Android loader verification is next

The nine BF-generated shared-library acceptance fixtures, C Android loader probe, independent AArch64 simulator parity and Linux JNI transport edge-case checks are implemented. The loader probe has **not run on Android** in this environment: no NDK/ADB/device was available. Next is the actual ARM64 Android shell `dlopen` run, followed by BF-policy JNI/APK parity, remaining original sources, and native Android self-hosting. Do not remove fallback compilers until those gates pass. The 100-million-command objective remains cancelled. [Device run instructions](ITERATION60_ANDROID_LOADER_ACCEPTANCE.md), [active gated plan](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Iteration 57 onward — only fully dynamic callable compilation

**Active objective:** replace the old bounded callable compiler with resource-growing BF-owned code emission, bracket/IR metadata, 64-bit relocation, ABI-compatible callable artifacts and Android execution. There is **no active 100-million-command compilation gate**. New Iteration 57 BF-native linear emission/ELF sizing is tested, but loop support and JNI are pending. Old bounded and freestanding implementations remain regression fallbacks **until** full dynamic functionality passes the pinned 11 original-policy corpus and Android tests; do not remove them prematurely. [Active gated plan](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md), [Iteration 57 evidence](../evidence/iteration57_dynamic_callable_linear.json). The remainder of this file is historical.

---

# Iteration 56 — first original Twitter policy native image

The optional Brainfuck-owned `policy_clear56` stream reduces the original TwitterHideAds `action.bf` from 4,723 to 3,819 RLE records and compiles it to a **15,300-byte AArch64 callable ELF**. Ten independent source-BF/optimized-IR frame comparisons and native bytecode oracle passed; Gmail historical and Iteration 55 variant images stay exact. **No Android loader/JNI/APK run** for Twitter, no real removal of the 4,096-record working-tape ceiling, and no 100M full codegen. [Technical contract](ITERATION56_TWITTER_ACTION_CLEAR.md) and [next steps](ANDROID_APP_ROADMAP_ITERATION56.md).

---

# Iteration 55 — current callable Android policy implementation

An opt-in standard-Brainfuck IR pass propagates known cell values into native AArch64 constant stores for the original Gmail `row.bf` and `scope.bf`. Both full source-to-ELF outputs and independent bytecode/IR oracles passed on Linux. The legacy BF stages and Android device images are unchanged, and the new images are **not yet device-tested or benchmarked**. This is a small verified code-size optimization, not general resource-scaled compilation. See [the Iteration 55 contract](ITERATION55_GMAIL_VALUEFOLD.md), [roadmap](ANDROID_APP_ROADMAP_ITERATION55.md) and [evidence](../evidence/iteration55_policy_valuefold.json).

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

# Android real-application priority — Iteration 46

## Iteration 48 — 32-bit loop pairing without AArch64 relocation

**Executed:** BF-owned streaming bracket pairing at positions 0 and 100,000,001 in a real 100,000,002-byte source, using a 255-deep fixed stack. Rejections, source-to-event parity, atomic output handling and independent seed agreement passed. The old raw scanner protocol is preserved; use the opt-in framed scanner for pairing. [Evidence](../evidence/iteration48_android_100m_pairing.json).

**Required next:** 32-bit positions are *source* offsets, not machine-code addresses. Implement BF-owned compact streaming IR and executable code offset mapping, AArch64 long-branch placement, safe multi-gigabyte artifact accounting and dynamic ELF/DSO output; then compile and test all eleven real Android policies. Native code generation is still limited to 2,719 instructions, not 100 million.

---


## Iteration 47 — target 100 million per unit directly

Skip further tiny capacity tiers. The capacity target is now **100,000,000 BF instructions in a single compilation unit**, with general BF-native code generation and a real Android execution proof, not only source scanning. The new [BF-owned 32-bit source stage](ANDROID_100M_CAPACITY.md) passes the transport/count/bracket-occurrence primitive. Next implement compact streamed BF IR with verified bracket matching, 64-bit artifact sizing, long AArch64 branch lowering, Android loadable output and the eleven real policy kernels. Keep [the application acceptance contract](ANDROID_APPLICATION_ACCEPTANCE.md) and target-side S2 as hard gates. No remaining-iteration estimate is justified by the scanner alone.

---

**Roadmap reprioritization — Iteration 46 (PLANNING ONLY):** Android BF policy programs from GmailHideAds (2), TwitterHideAds (3) and ThreadsHideAds (6) become mandatory product acceptance tests. First reach compilation of the largest 296,307-command original program; then reproduce all 11 native policy kernels, runtime/JNI host ABI integration and three Android APK parity releases. Increase long-term capacity beyond the old 300,000 ceiling: >=10M commands per compilation unit and >=100M aggregate; these goals do not imply arbitrary Java/Gradle compilation. Keep Linux and historical Android bounded self-hosting gates intact; do not treat this plan as evidence of implementation. [Details](ANDROID_APPLICATION_ACCEPTANCE.md).

---

# Android resumed — Iteration 45 checkpoint

**Implemented:** BF-owned eight page class RX/`ADRP` carry stage and opt-in 2,719-command AArch64 ELF PIE code generation with loops. **Verified:** Linux native BF execution, independent BF stage interpreter comparison, ELF structural checks, and AArch64 simulation. **Still needed:** Android device run of the expanded files; BF-owned 24-bit or larger source offsets and streaming ELF layout (beyond the two-byte table and 48-byte slot output design); native compiler input capacity beyond the recorded 16,128-command profile; 300,000-command ordinary-program compilation and independent repeatable Android on-device self-hosting at the intended final capacity. Windows target-side S2 remains separate and open. The historical 22-iteration estimate is not a guarantee. See [the report](ITERATION45_ANDROID_REPORT.md).

---

# Iteration 44 checkpoint — Windows 192-command PE generator

The optional Windows BF-only backend has grown to **192 commands with loops**, with 77 Linux x64 shim differential tests and 990 verified branch relocations. Complete real Windows loader execution next. The next compiler changes require multi-byte indices, variable PE size classes, and eventually a Windows-native BF compiler plus Stage 0–2 self-hosting. Linux S2 and archived Android bounded S2 are preserved; the Android 300,000-command goal remains open. The historical 22-iteration count is not a verified remaining-work forecast. [Report](ITERATION44_REPORT.md) · [contract](WINDOWS_FULL192_PE.md).

---

# Iteration 43 checkpoint — Windows 128-slot PE writer

The Windows all-eight-command experimental backend advances from 64 to **128 commands**, still entirely standard Brainfuck. It passed 100 source-dependent x64 CPU executions on Linux with Win32 test shims; Windows loader execution and native compiler S2 remain unverified. Next run target-side acceptance, then scale BF-owned PE/loop records and produce a Windows-native self-hosting compiler. Existing Linux S2 and archived Android bounded S2 are retained; Android 300,000-command acceptance remains open. The historical 22-iteration plan is not a verified remaining-work estimate. [Iteration 43](ITERATION43_REPORT.md) · [contract](WINDOWS_FULL128_PE.md).

---

# Iteration 42 checkpoint — Windows CPU-level tests, target gate still open

The BF-owned Windows backend remains **64 commands / eight BF instructions**. [Independent execution testing](WINDOWS_LINUX_CPU_EXECUTION.md) now runs its generated x64 bytes on Linux with test-only Win32 shims; 164 new programs and all 11 earlier smoke binaries pass. **Windows loader execution and Windows-native S2 remain unverified.** Next complete target-side Windows smoke tests, then BF-owned PE source capacity beyond 64, a Windows-native compiler and repeated self-hosting. Preserve the separate Android 300,000-command target as an open gate. The original 22-iteration estimate is historical, not a remaining-work guarantee. [Iteration 42 report](ITERATION42_REPORT.md).

---

# Iteration 41 roadmap update — Windows BF loops generated, loader pending

The bounded [Windows all-eight-command PE path](WINDOWS_FULL64_PE.md) now generates nested-loop executables through 64 instructions using Brainfuck-owned pairing, x64 signed-displacement calculation and binary patching. **Native Windows loader execution and Windows compiler S2 are still open**. Next acceptance: run [Windows 41 smoke-test binaries](../build/windows41_acceptance/manifest.json) on a real Windows x64 host, then expand bounds and prove target-native compiler self-hosting. Linux S2 and archived Android bounded S2 remain separate; Android 300,000-command qualification is unresolved. The original **22-iteration** count is historical baseline planning, not a completion estimate.

---

# Iteration 40 checkpoint — Windows six-instruction linear PE backend

The new [Windows linear I/O backend](WINDOWS_LINEAR_IO_PE.md) generates BF-owned PE32+ images for `+ - > < . ,` from at most 64 executable commands, with imported Win32 byte I/O and deterministic x64 pointer traps. Its BF source, native Linux writer and static image tests pass; **no Windows loader/API execution** was performed. `[` and `]`, Windows-native compiler execution/S2, and Android's separate 300,000-command acceptance target remain outstanding. See [iteration report](ITERATION40_REPORT.md) and [evidence](../evidence/iteration40_windows_linear_io.json). Historical notes follow below.

---

# Current roadmap checkpoint — Windows Iteration 39

The Android **bounded S2 prerequisite** was recorded from the uploaded device archive; the 300,000-command universal-capacity goal is separate and still open. Windows now generates PE32+ images for up to **64** filtered `+ - > <` commands through standard-BF source and tape-aware native lowering. Linux validates images and code structure; **Windows execution is unverified**. Next gates: real Windows loader acceptance, BF-owned Win32 read/write, loop relocation, general source capacity and Windows-native self-hosting. The historical 22-iteration projection is not a completion guarantee. [Report](ITERATION39_REPORT.md), [target contract](WINDOWS_LINEAR_PE.md).

---

# Current roadmap checkpoint — begin Windows after recorded Android S2

The uploaded archive has recorded on-device Android S2 at **16,128-command input capacity**; see [the evidence audit](ANDROID_NATIVE_S2_AUDIT.md). That satisfies the original **native self-hosting prerequisite for beginning Windows**, but not the separately proposed 300,000-command universal Android acceptance target. Windows has started with a [BF-owned structural PE32+ image](WINDOWS_PE32_SEED.md), not native execution. Continue Windows by verifying its loader, then source parsing and x64 code emission, Win32 I/O, bracket relocation, and target-side S2. Retain parallel Android capacity expansion as an open acceptance gate. The old 22-iteration plan is historical and should not be interpreted as the number of iterations now remaining. [Iteration 38 report](ITERATION38_REPORT.md).

---

# Iteration 37 roadmap update — Android device acceptance remains open

The expanded 2,000-command BF-owned Android pipeline is still simulator-verified only. Iteration 37 added a reproducible [13-program device gate](ANDROID_DEVICE_ACCEPTANCE.md), but could not run `adb` in this environment. Actual Android loader execution, Android-native compiler execution/S2 and 300,000-command code generation remain future milestones. Windows still follows Android S2. The 22-iteration baseline was an estimate and its numbered dates cannot be considered completion evidence. See [Iteration 37 report](ITERATION37_REPORT.md). Older roadmap detail follows.

---

# Iteration 36 roadmap checkpoint

The **22-iteration Android-first, Windows-second plan is an estimate, not a completion guarantee**. Iteration 36 verified a bounded BF-owned 2,000-command Android AArch64 loop pipeline through Linux native-stage execution and AArch64 simulation only. Previous 1,024-loop and 2,000-linear restrictions have been unified for `--multiclass --tape-relocated --loops`; no Android-native compiler/S2 or actual Android loader test is complete. Next evidence gates: Android loader execution, broader ELF/tape scaling toward 300,000 commands, a native Android compiler that recompiles itself, and then Windows x86-64 PE32+. See [Iteration 36 report](ITERATION36_REPORT.md).

---

# Iteration 35 active handoff

The Iteration 35 partial milestone adds Brainfuck-owned tape relocation and RX length repair, with **2,000 linear / 1,024 loop commands** in Linux-hosted AArch64 simulation. The **original 22-iteration baseline is still only a forecast**. Android-native compiler execution/S2, larger relocations and Android loader verification are not complete, so Windows development has not started. Next prioritize wider loop table, a device/emulator loader run, and Android-native compiler bootstrap. See [Iteration 35](ITERATION35_REPORT.md).
---

# Active roadmap update — Iteration 34

The **22-iteration baseline remains a forecast**, not an earned maturity level. Iteration 34 has implemented a **four-class, 1,024-command** Brainfuck-owned AArch64 ELF and loop-relocation pipeline in Linux-hosted native stages, tested in AArch64 simulation only. See the [Iteration 34 report](ITERATION34_REPORT.md), [evidence](../evidence/iteration34_multiclass_elf.json) and [acceptance contract](PLATFORM_ACCEPTANCE.md). This improves the bounded image emitter; **Iteration 34 full general-layout gate is not complete**.

Next gates, in priority order: (1) BF-owned tape vaddr relocation and startup suitable for RX code past `0x10000`, (2) larger bounded program emission with loop cases, (3) real Android loader execution with byte input/output/EOF/traps, (4) Android-native compiler and true S2 self-compilation, (5) 300,000-command acceptance. Windows PE32+ work follows verified Android-native S2. The historical 26–47 iteration matrix below describes the original estimate, not completed milestones.

---

# Roadmap update — Iteration 33 slice verified, Android consolidation still open

The BF-owned 512-command loop relocation gate and 330→331 ELF size transition have Linux-native-stage and AArch64-simulator evidence ([Iteration 33](ITERATION33_REPORT.md)). The **300,000-command Android generated-artifact goal**, additional ELF alignment classes, actual Android loader execution, Android-native compiler execution, and complete target-side S2 remain open. Windows PE32+ follows verified Android native S2, not simulator evidence. The original **22-iteration baseline** and **28–34 contingency** describe original planning, not a new remaining-iteration count. Historical roadmap snapshots follow.

---

# Roadmap status — Iteration 32 partial loop relocation

The planned Iteration 32 compiler-consolidation gate remains **OPEN**. A narrower BF-only implementation slice now relocates loops through **255 commands**; the optional ELF writer already supports **512 linear** commands. Next implement multi-byte relocation indexing and test *loop-containing* programs across the 330→331 ELF size-class transition, then generalize code generation and execute an Android-native compiler. The 22-iteration original baseline is still a forecast, not a verified number of iterations remaining. Windows starts after Android-native S2, not after simulator tests. Evidence: [`ITERATION32_REPORT.md`](ITERATION32_REPORT.md).

---

# Iteration 31 checkpoint — bounded size classes, runtime gate still open

BF-owned AArch64 ELF emission now switches the aligned file offset at **331 commands** and supports **512 linear commands**, while the BF relocation stage remains limited to **74 commands with loops**. This is a partial carry-over from the planned Iteration 30 dynamic ELF work. The planned Iteration 31 device I/O and runtime acceptance gate is **not completed**. No on-device tests or Android-native compiler were produced. The forecast of 22 baseline iterations is a planning estimate, **not a confirmed remaining effort or completion guarantee**; later numbered tasks may shift. No fixed revised total is justified by the current evidence. Evidence: [`ITERATION31_REPORT.md`](ITERATION31_REPORT.md).

---

# Roadmap status — Iteration 30 partial, Android first

The **22-iteration baseline** (Android 26–39, Windows 40–45, qualification 46–47) is a forecast, not a promise. Iteration 30 now contains a Linux-executed BF-only PIE writer supporting **255 linear** or **74 loop-containing** commands, with variable executable segment size but **fixed 16,480-byte ELF files** in the first aligned size class. The exit gate for Iteration 30 (arbitrary page-class sizing, Android OS loader runs) is **still open**. The remaining Android and Windows iterations are not credited with unexecuted milestones. Evidence: [`ITERATION30_REPORT.md`](ITERATION30_REPORT.md).

---

# Android-first native compiler roadmap — Iteration 29 partial progress

This remains an **evidence-gated plan**, not a completed Android compiler. Iteration 26 froze the contract; 27 added wide scanning; 28 added BF bracket matching and B-branch words. Iteration 29 then added a separate BF-owned **74-command ELF** path and a subsequent opt-in BF-native **loop relocation** pass, validated by simulator tests. Dynamic image sizing, device execution, and self-hosting remain open. All milestones remain partial with respect to the full Android compiler objective. See [the Android protocol](ANDROID_COMPILER_PROTOCOL_V1.md) and [Iteration 26 evidence](../evidence/iteration26_contract.json). The plan starts after historical Iteration 25 and the unnumbered Android optimization work recorded on 2026-10-12. `compiler/core.bf` and the archived historical evidence remain unchanged; Iteration 27 records new experimental evidence separately.

## The answer: 22 planned engineering iterations

| Order | Iterations | Count | Exit condition |
|---|---|---:|---|
| Android AArch64 first | **26–39** | **14** | Android shell compiler runs, compiles ordinary V0 Brainfuck and compiles its own entire BF source through stable native stages |
| Windows x86-64 second | **40–45** | **6** | Native PE32+ compiler runs, emits V0 Windows executables and repeats native self-compilation |
| Shared release qualification | **46–47** | **2** | Linux, Android and Windows proofs, reproducibility, regression suites and release artifacts agree |
| **Total** | **26–47** | **22** | Evidence-gated baseline, not a guaranteed schedule |

Estimate **28–34 total iterations** if source-buffer redesign, long-branch resolution, Android loader compatibility, native bootstrap or Windows import handling needs additional proof and rework. Counts are engineering planning units, **not elapsed time or a claim of certainty**. A failed exit gate repeats the iteration; nothing advances simply because a number was assigned.

## What universal means in this release

A *universal V0 Brainfuck compiler for Android AArch64 shell use* must accept arbitrary combinations of **all eight original instructions** within an explicit documented resource envelope; ignore non-instruction characters; reject malformed brackets and oversized programs cleanly; emit a real AArch64 PIE; and preserve the common 8-bit, modulo-256, initially zeroed fixed-tape, 65,536-cell, EOF-zero, deterministic-boundary-trap semantics. It must support byte I/O, nested loops, zero bytes and repeated calls with identical results. A compiled **Android-native Brainfuck compiler must itself recompile its complete standard-BF source on Android**. The Linux compiler remains S2 throughout.

The proposed capacity validation gate is **at least 300,000 executable commands** with a documented nesting limit, so the largest of the eleven currently counted Android policy sources (296,307 commands) is not excluded solely by the old input ceiling. A larger or streaming input contract must be designed and proved before implementation. This is a **target, not a currently supported limit or a promise of unbounded input**. The compiler's own potentially growing BF source must also fit, and tests must cover the supported upper bound. Large-program memory use, output-size handling, relocation reach, deterministic exhaustion, and compilation time are separate pass criteria.

This first release covers the documented **`arm64-v8a` shell environment**, not the entire Android ecosystem. Android devices support different ABIs (`arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`), so additional backends or separately verified builds are necessary for multi-ABI universality. An ELF shell executable is not an APK, Java/Xposed bridge, or permission to execute native binaries from every Android app sandbox. External app APIs cannot be invented as a ninth Brainfuck instruction. Windows similarly starts with **x86-64 PE32+ console** and not all Windows architectures or application types. See [the scoped acceptance contract](PLATFORM_ACCEPTANCE.md).

## Android: Iterations 26–39

| Iteration | Deliverable | Mandatory test or evidence gate |
|---|---|---|
| **26 — completed (contract)** | Freeze V0, Android input/output framing and native loader contract; inventory existing BF stages and tape ownership | Versioned contract and stage regression checks executed on Linux; causally chained native Stage 1→2 recompilation identical; cold full release suite not rerun to completion |
| **27 — partial** | BF-owned 24-bit streamed command scanner works through 300,001 commands; opt-in adapter preserves ten-slot output, but general source ingestion into Android emission is unfinished | Wide BF scan, count carry and malformed-input checks executed; **general bracket/ELF integration still pending** |
| **28 — partial** | BF wide bracket pairs and wide AArch64 B-branch instruction words executed; applying relocations in runnable ELF remains open | Branch-word oracle passes; full image relocation gate OPEN |
| **29 — partial** | BF code slots and BF-owned wide loop relocator produce **74-command loop-capable** fixed-size ELF through opt-in path | 85 program simulations at two bases and 390 BF bracket pairs passed; dynamic ELF, native Android execution and full capacity still OPEN |
| **30** | Dynamically sized Android ELF PIE, tape placement, loader compatibility and executable data protections | Real device/emulator loads both short and large artifacts, tested ASLR, no writeable-executable tape |
| **31** | Full eight-command semantics on Android with robust byte I/O, EOF-zero, retries/error paths and deterministic pointer traps | Independent interpreter differentials including stdin redirection, NUL/FF, EINTR and boundary failures |
| **32** | Put source parsing, optimization baseline, instruction selection, ELF construction and relocation under a reproducible **BF-only** compiler path; eliminate reliance on orchestrated fixed-image stages for essential compilation | Compiler logic remains in `.bf`; host only transports/places files; build logs and hashes recorded |
| **33** | Compile the full BF compiler source to a native Android AArch64 compiler executable and execute it on Android | Native compiler produces runnable program binaries without a foreign code generator |
| **34** | Complete Android-native Stage 0→1→2 self-compilation of the entire BF compiler | Repeated compilations equivalent (prefer byte-identical); hashes, native execution and independent programs recorded |
| **35** | Harden compiler-internal tape management, emitted-code bounds, malformed input and resource exhaustion | Differential fuzzing, negative cases, no silent truncation; relevant safety invariants justified |
| **36** | Reach and test the **300,000-command acceptance target**, or document and address any architectural constraint blocking it | Actual large BF sources emitted and executed; target workloads whose semantics/ABI match V0 distinguished from host-dependent policies |
| **37** | Compatibility across a declared Android version/API and loader matrix; device and emulator diversity | Minimum *tested* API level and supported shell location recorded, not inferred from `arm64-v8a` alone |
| **38** | BF-owned safe loop/transfer optimizations and repeatable competitive-performance baselines | Full semantics and native self-hosting rerun; measured C/Rust comparison with uncertainty and regressions |
| **39** | Ship Android AArch64 shell-toolchain candidate with installation, diagnostic protocol, reproducible build and provenance | Acceptance checklist green; Android native self-hosting **EXECUTED**; Linux S2 retained |

A failed early capacity or on-device bootstrap test may split an iteration; later planned numbers then shift. Source handling, backends and optimization must **never** migrate into Python/C/Rust; these may remain independent seeds, tests, analyzers, transports and baselines.

## Windows: Iterations 40–45

| Iteration | Deliverable | Mandatory test or evidence gate |
|---|---|---|
| **40** | Windows x86-64 PE32+ console and Win32 import/loader/diagnostic ABI specification | Explicit calling convention, stack alignment, shadow space, nonvolatile registers, import and error contracts |
| **41** | BF-owned PE32+ header, sections, image-base handling, import-address table and relocation work | Independent PE/COFF inspection and Windows loader acceptance |
| **42** | Complete x64 codegen for eight commands; Win32 standard-handle byte I/O, EOF, errors, tape checks and exit | Native Windows semantic and adversarial differentials incl. redirection and pipes |
| **43** | Integrate scalable parser, general branches and reliable binary output into Windows compiler path | Large BF source execution; no external assembler/linker in the production path |
| **44** | Generate, execute and self-compile a **native Windows BF compiler** through multiple stages | Stage 0→1→2 outputs/behavior agree and execute on Windows; clean checkout repeatable |
| **45** | Windows hardening, version matrix and native C/Rust benchmark baselines | Windows-native checks green; Linux/Android regression gates rerun; release docs accurate |

Use documented APIs such as `GetStdHandle`, `ReadFile`, `WriteFile`, and `ExitProcess` (or a justified equivalent), not undocumented syscall numbers. The standard Microsoft x64 ABI requires register-based argument passing, shadow space and stack alignment. The test matrix names actual Windows versions rather than presuming compatibility.

## Shared qualification: Iterations 46–47

| Iteration | Deliverable | Mandatory test or evidence gate |
|---|---|---|
| **46** | Cross-platform BF semantic corpus, bootstrap trust review, independent artifact inspection and resource/safety regressions | Android, Windows and Linux native Stage 0–2 each executed and compared; target-specific failures reported |
| **47** | Reproducible multi-target release, support matrix, installation/transport guides and evidence bundle | No status conflict; source and binary hashes bound to the release; known limits disclosed |

## Not included in the 22-iteration core estimate

- **All Android ABIs:** estimate **4–8 extra iterations per additional ISA/ABI** for `armeabi-v7a`, Android `x86`, and Android `x86_64` as distinct verified targets. Some reuse is possible; treat estimates as independent until measured.
- **APK/Play Store/Android app sandbox/JNI/Xposed integration:** budget **3–6+ additional iterations per distinct supported integration pattern** after the native shell toolchain exists; requirements and external services may make some cases impossible without a host bridge.
- **G29 or other non-V0 programs:** require a separately versioned semantics profile (G29 uses signed 32-bit checked cells and a different tape/host contract); no blanket claim that V0 compilation preserves their semantics.
- **Every imaginable source size, hardware target, API, or C/Rust performance result:** impossible to guarantee with finite resources or eight-instruction byte-I/O semantics. The contract must say exactly what was tested.

## Hard gates at the end of every iteration

1. No ninth Brainfuck instruction; all authoritative compiler logic remains raw `.bf`.
2. V0 semantic and deterministic tape-boundary behavior does not change.
3. Linux full native self-hosting remains green; Android/Windows native self-hosting must be rerun once those stages exist.
4. Source comments and binary protocol remain valid; invalid inputs never install a partial executable.
5. Independent correctness, optimizer and memory-safety tests run; blocked platform tests are explicitly **UNVERIFIED**.
6. Artifact signatures, build provenance and benchmark metadata are recorded; measured claims are never promoted from structural simulation.
7. Documentation, [`STATE.md`](STATE.md), [`HANDOFF.md`](HANDOFF.md), [`TARGETS.md`](TARGETS.md) and [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json) are synchronized from **executed evidence**, not roadmap forecasts.

## Starting point and priority

Verified historical baseline: Linux x86-64 native S2; a separate Android pipeline that generates bounded ten-command native programs which **were executed on Pixel 8 Pro (Android 17/API 37)**; optional BF-owned optimizers with one small, uncertain median speed lead. **No Android-native compiler or self-hosting yet; no Windows PE32+ backend.** These facts come from the archive's evidence and were not independently rerun on those platforms during this documentation update. Iteration 26 contract is completed. Iterations **27–29 remain partial**: BF-owned scanning, wide matching, encoding, and bounded 74-slot loop relocation execute on Linux; dynamic ELF size and Android target execution remain unverified. Continue with dynamic ELF layout before full device acceptance. Documentation reconciliation was **D0**, not a fabricated compiler milestone.

References: [`STATE.md`](STATE.md), [`ANDROID_NATIVE_OPTIMIZATION.md`](ANDROID_NATIVE_OPTIMIZATION.md), [`TARGET_WORKLOADS.md`](TARGET_WORKLOADS.md), and [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json). Platform references: [Android NDK ABIs](https://developer.android.com/ndk/guides/abis), [Android native APIs](https://developer.android.com/ndk/guides/stable_apis), and [Microsoft x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention).

## Iteration 28 branch-encoding follow-up (partial gate)

The 24-bit BF pairing output now feeds a separate **BF-native Linux-executed 26-bit AArch64 `B` record encoder**, independently checked through a 300,000-command input and explicit range rejection. This completes a **record encoding substage**, not wide branch relocation/application or dynamic Android ELF construction. Iteration 28 remains **PARTIAL**; Iteration 29 still needs the actual variable-length emitter/patcher and target execution evidence. The baseline 22-iteration **forecast is unchanged**, not earned progress. See [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md).

## Iteration 29 bounded loop relocation follow-up

The BF-native wide branch encoder now feeds a separate **BF-native slot patcher**. Its output is consumed by the existing fixed 74-slot BF ELF wrapper without host-side AArch64 instruction modification. This resolves **loop relocation for bounded images**, not dynamic image layout. The opt-in `--loops` path passed 85 AArch64 simulated programs and 390 bracket-pair word checks; no Android-device execution occurred in this follow-up. The Iteration 30 dynamic ELF gate remains open. Full evidence: [`ITERATION29_LOOP_FOLLOWUP.md`](ITERATION29_LOOP_FOLLOWUP.md).

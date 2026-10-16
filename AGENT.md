# Project name — BrainfuckCC

The project is now **BrainfuckCC** (repository: https://github.com/MrxSiN/BrainfuckCC). The former names `brainfuckC`/`brainfuckc` and `brainfuck-native` are retired in maintained code and docs: the Android JNI test bridge is now Java package `org.brainfuckcc`, library `libbrainfuckcc_bridge.so` and property `brainfuckcc.bridge.absolutePath`. Archived `evidence/` and `build/` records keep their original names and paths as historical data. No compiler source, BF stage or emitted machine code changed.

---

# Iteration 65 current task — Android dynamic callable target execution

The active relocation host now uses file backed duplicate patch marks, not a Python set proportional to loop pairs. The BF compiler and emitted code are unchanged. [Iteration 65 report](docs/ITERATION65_DYNAMIC_RELOCATION_STORAGE.md). Obtain actual Android Bionic, ART/JNI and APK execution evidence; retain all fallbacks until dynamic Android native self hosting and parity are proven.

---

# Iteration 64 current task — run BF DSO on actual Android

The BF-native dynamic callable DSO now passes independent ELF and AArch64 instruction/relocation postflight validation locally. The compiler source is unchanged. Continue with actual Bionic loader, ART/JNI, installed APK, original policy parity and native Android self-hosting evidence. Do not label code-template scanning as real Android execution or delete old fallback lanes. [Iteration 64 report](docs/ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md).

---

# Iteration 63 current task — execute BF DSOs on Android

The BF native callable DSO path now rejects malformed export and loader metadata before atomic publication using [bounded-memory validation](docs/ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md). Run `python3 -m tests.verify_android_dynamic_callable63` and the existing DSO and APK host tests. Current evidence is structural and simulated only; real Android Bionic/ART, original policy parity and Android-native dynamic self-hosting remain unverified. Do not replace Brainfuck-owned emission with Python/C and do not remove the old fallbacks before target acceptance. The 100-million-command objective is retired.

---

# Iteration 62 current task — verify installed Android APK JNI loading

Test-only Gradle APK scaffold and ADB verifier exist in `tools/android_bfp1_bridge/apk62/` and `tools/android_bfp1_bridge/apk_acceptance62.py`; they package nine unchanged BF-generated DSOs and call the existing JNI bridge from the app native library directory. Linux JVM/stub, package integrity and mock-ADB guards pass; **actual Android APK build/device execution is unverified**. Next run device acceptance, then original policies and native Android dynamic compiler S2. Do not relabel C JNI transport as compiler logic or remove older fallbacks early. No numerical 100M goal. [Guide](docs/ITERATION62_ANDROID_APK_ACCEPTANCE.md).

---

# Iteration 61 current task — execute ART/JNI callable on Android

The resource-scaled Brainfuck-owned AArch64 DSO path now has an Android `app_process` acceptance test (`tools/android_bfp1_bridge/device_acceptance61.py --device`) which checks nine BF-generated policies through the actual JNI bridge. Local **Linux JVM with test-only C stubs** and mocked ADB checks pass; no Android device run is claimed. Next fix device loader/ABI failures if observed; then APK namespace, original policy parity and native dynamic self-hosting. Preserve the fallback compiler paths. [Detailed acceptance](docs/ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md).

---

# Iteration 59 active mission — Android callable shared-library execution

> Active iteration 60: loader device-acceptance fixture path in `docs/ITERATION60_ANDROID_LOADER_ACCEPTANCE.md`. BF codegen unchanged; Android actual execution unverified. Retain fallback paths.

The dynamic all-eight-instruction BF-native compiler now builds AArch64 ELF shared objects with an exported `bfc_call_v1` function. The new BF-owned DSO header and the loop emitter are verified through Linux-native stages, ELF inspection, a cross-link test and instruction simulation. JNI host transport was executed on Linux only, using a deliberately test-only native stub. Next work: run actual BF-produced DSOs via Bionic `dlopen`/JNI on Android, compile the other eight pinned policy sources, then run all app parity and target-native compiler self-hosting gates. Keep earlier bounded lanes solely as fallbacks until replacement is proven. The 100-million-command objective is retired. [Iteration 59 evidence](docs/ITERATION59_DYNAMIC_CALLABLE_DSO.md), [active roadmap](docs/ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 57 active mission — callable compiler without a fixed command count

Prioritize the BF-owned growing callable Android compiler. The old numeric 100-million-command target is cancelled. Stage 57 provides growing six-operator native callable code and 64-bit header arithmetic; next implement dynamically paired brackets/relocation with BF control. Existing bounded IR and freestanding pipelines remain fallbacks until complete on-device replacement. Verify with `python3 -m tests.verify_android_dynamic_callable57`; the actual compiler logic must remain eight-instruction Brainfuck. [Handoff](docs/HANDOFF.md).

---

# Iteration 56 current task state

The first original TwitterHideAds BF policy, `action.bf` (24,616 instructions), now compiles to a 15,300-byte AArch64 callable ELF via the optional BF-only `policy_clear56.bf` clear-folding pass (4,723 to 3,819 IR records). Verify with `python tests/verify_policy_clear56.py`; see [the technical evidence](docs/ITERATION56_TWITTER_ACTION_CLEAR.md). **No new Android runtime result**. The actual record ceiling and 100M capacity goal are still open. Follow [docs/STYLE.md](docs/STYLE.md).

---

# Iteration 55 current handoff — BF callable policy constant folding

New opt-in standard BF stages `policy_valuefold55`, `policy_oneshot55` and `policy_codegen55` compile both original Gmail policy sources into smaller AArch64 images with verified IR semantics. The original unsuffixed stages and archived Android device evidence are unchanged. Execute `python tests/verify_policy_valuefold.py`, `python tests/verify_policy_valuefold_semantics.py`, `python tools/sync_status.py` and `python tools/check_docs.py`. No new Android device execution or performance improvement has been proven. Next: Android test APK parity and kernel benchmarks, callable >4096 records for original Twitter/Threads, and dynamic source/resource management. Follow [docs/STYLE.md](docs/STYLE.md).

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
[the engineering report](docs/ITERATION54_PROGRESS_REPORT.md),
[reproducibility contract](docs/ITERATION54_LINUX_GM_REPLAY.md) and
[the revised roadmap](docs/ANDROID_APP_ROADMAP_ITERATION54.md).

---

# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](docs/ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Iteration 53 — BF-owned far-loop AArch64 ELF path

The experimental Android compiler now emits compact, dynamically sized, all-eight-instruction freestanding PIE ELFs with **64-bit PC-relative long loop jumps**. New 32-byte bracket templates and BF-owned 64-bit position/literal arithmetic replace direct AArch64 `B` branch reach limits. **57 small ELF programs / 114 AArch64 simulator runs passed**. A 296,307-command **synthetic** program produced a 3,686,824-byte ELF accepted by `readelf`; this was not an Android device run or an original application policy compilation. No JNI/DSO or 100M executable compilation acceptance is claimed. Read [the engineering report](docs/ITERATION53_LONG_RANGE_ANDROID_ELF.md), [roadmap](docs/ANDROID_DYNAMIC_ROADMAP_ITERATION53.md), and [evidence](evidence/iteration53_android_far_elf_tests.json).

---

# Iteration 52 checkpoint — dynamically sized compact AArch64 ELF (Linux-simulated)

The multi-stage standard-Brainfuck pipeline now produces complete freestanding AArch64 ET_DYN ELF images for all eight Brainfuck instructions, with dynamic compact code, BF-owned 64-bit native positions, file-backed loop matching, BF-owned signed B relocation and ELF headers. The 55-case differential suite passed 110 AArch64 simulations; a **synthetic** 296,307-command file generated a 3,686,784-byte ELF accepted by readelf. No Android loader/device execution, original application policy compilation, JNI/shared-library integration or new target self-hosting has occurred. Direct B reach still limits some loop spans. See [Iteration 52 contract](docs/ITERATION52_DYNAMIC_AARCH64_ELF.md), [test evidence](evidence/iteration52_android_dynamic_elf_tests.json), and [large synthetic evidence](evidence/iteration52_large_synthetic.json).

---

# Iteration 51 Android integration checkpoint

[The current integrated code/pair stream](docs/ITERATION51_COMPACT_AARCH64_RELOCATION_LEDGER.md) has BF-owned all-eight compact raw machine code, 64-bit native-word offset tracking, and BF-owned bracket matches in disk-backed dynamic storage. The verified output is **unrelocated code plus matched pairs**; branch-word encoding, ELF/DSO layout, Android-native execution, original eleven policy compilation and JNI/APK parity are outstanding. The existing full ELF limit of 2,719 instructions is unchanged.

---

# Iteration 50 — dynamic Android code and bracket storage, partial

**Current evidence:** the [Iteration 50 engineering report](docs/ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) verifies a standard-BF compact **raw AArch64** six-instruction emitter through 1,000,000 `+` commands (12 MB code), and a BF-controlled disk-backed bracket-pairing stack through nesting depth **4,096**, including a 100,000,002-byte source with a wide loop. The file-backed matcher is not yet connected to compact native code relocation or a loadable ELF. Its upstream scanner is still 32-bit. The original complete eight-instruction ELF path remains tested only through **2,719 commands**; no new Android-native execution, JNI/APK build, original eleven-policy compilation, or universal 100M codegen is verified. The canonical Linux BF compiler and archived Android-native bounded S2 are preserved. [Handoff](docs/ANDROID_DYNAMIC_SCALING_HANDOFF.md). Historical snapshots follow.

---

# Iteration 49 — resource scaled native code streaming

A new [standard BF native slot stage](experiments/android_streaming_linear_slots.bf.notes.md) reads arbitrary raw source bytes and emits AArch64 linear instruction slots as a stream with **no built in source command count ceiling**. A 300,001-command program generated 14,400,048 native bytes and matched existing BF-owned templates. The host only frames and copies bytes, with optional caller supplied output quotas; it does not parse BF or emit instructions. **Not a runnable ELF:** brackets, scalable relocation, dynamic executable layout, JNI and the eleven real application policies remain open. The complete Android ELF backend still supports only 2,719 commands. [Report](docs/ITERATION49_DYNAMIC_ANDROID_STREAMING.md) and [evidence](evidence/iteration49_android_dynamic_stream.json). The 100M benchmark remains a target, not an artificial maximum or a completed native executable. Earlier iteration notes remain historical.

# Android real-application priority — Iteration 46

## Current implementation checkpoint — Iteration 48

Standard Brainfuck now pairs 32-bit source bracket positions, verified on a real 100,000,002-byte single-loop input. The new framed scanner is opt-in; the original Iteration 47 scanner output is unchanged. Pairing stack capacity is 255 and native Android ELF compilation remains at 2,719 commands. Do not label this 100M executable compilation. Run `python3 tests/verify_android_100m_bracket_pairs.py` before changing the framed protocol. Details: `docs/ITERATION48_ANDROID_100M_PAIRING.md` and `evidence/iteration48_android_100m_pairing.json`.


## Iteration 47 capacity boundary

Continue Android development directly toward **100M commands per translation unit**. The [source-stage evidence](docs/ANDROID_100M_CAPACITY.md) verifies only BF analysis, not native generation. For each codegen change preserve Linux S2 and bounded Android S2, require direct original-policy compilation, and do not mark JNI/APK parity or 100M native executable generation passed until executed.

---

**Current product acceptance (Iteration 46; not implemented):** Target original `.bf` policies in GmailHideAds, TwitterHideAds and ThreadsHideAds, followed by JNI native shared-library integration and full Android APK parity/device tests. See [docs/ANDROID_APPLICATION_ACCEPTANCE.md](docs/ANDROID_APPLICATION_ACCEPTANCE.md) and [status/ANDROID_APPLICATION_GATES.json](status/ANDROID_APPLICATION_GATES.json). Preserve BF-only compilation; Java/Gradle host work must not secretly own BF codegen.

---

# Iteration 45 Android current development

The active Android extension is the [Brainfuck-only eighth page class](experiments/android_adrp_high_byte_class8.bf.notes.md), tested via `python3 tests/verify_android_class8_2719.py`. The opt-in pipeline accepts at most **2,719 commands with loops**, not 300,000; do not assert on-device execution of these new images. Keep historic Linux S2, bounded Android device S2 and Windows experimental PE sources intact. The Python adapter handles transport only. Continue toward streaming wide ELF/relocations and on-device validation. Keep the repository style in [docs/STYLE.md](docs/STYLE.md).

---

# Iteration 44 handoff — Windows PE192, real Windows loader still pending

The new [192-command Brainfuck-owned Windows path](docs/WINDOWS_FULL192_PE.md) has 77 Linux x64 shim executions and 990 branch checks. Reproduce with `python3 tests/verify_windows_full192.py`, previous Windows tests, and `python3 tools/check_docs.py`. The 14-case [Windows device bundle](build/windows44_acceptance/manifest.json) is **not Windows-tested**; run `verify_windows44.ps1` on real Windows and retain the generated results before any target acceptance claim. Next: multi-byte relocation indices and true Windows-native compiler/S2. Preserve unchanged Linux source and archived Android bounded S2; the 300,000-command Android target remains open.

---

# Iteration 43 handoff — Windows PE32+ 128 slots, target execution pending

The optional BF-owned [128-command Windows compiler](docs/WINDOWS_FULL128_PE.md) generates 3,072-byte PE files for all eight instructions, including loops. Run `python3 tests/verify_windows_full128.py`, `python3 tests/verify_windows_full64.py` and `python3 tools/check_docs.py`. The new Linux x64 CPU shim has 100 passing differential cases; do not mark these as Windows-loader tests. Use `build/windows43_acceptance/verify_windows43.ps1` on actual Windows x64 and retain raw results. Next: loader acceptance, multi-byte slot indices, scalable PE layouts and native Windows S2. Preserve Linux S2 and the independent Android 300,000-command gate.

---

# Iteration 42 agent handoff — actual x64 instructions, Linux host shims

The bounded Windows BF-owned eight-command emitter remains unchanged. The [Iteration 42 harness](docs/WINDOWS_LINUX_CPU_EXECUTION.md) executed the generated x64 code on a Linux CPU with test-only Microsoft-ABI import shims, matching **164** reference source executions and **11** archived acceptance images. **Windows loader execution is still NOT RUN.** Run `python3 tests/verify_windows_linux_x64_execution.py`, the existing `tests/verify_windows_full64.py`, then `python3 tools/check_docs.py`. Do not turn the test C shim into production compilation logic. Next: Windows-native smoke, >64 BF-owned PE generation, Windows-native S2; keep Android 300,000-command gate open.

---

# Iteration 41 current handoff

Windows now has a bounded all-eight-command, 64-instruction BF-only PE compiler path. Start with [Windows contract](docs/WINDOWS_FULL64_PE.md), [report](docs/ITERATION41_REPORT.md), and [evidence](evidence/iteration41_windows_full64.json). Run `python3 tests/verify_windows_full64.py` and `python3 tools/check_docs.py`. Target-side `verify_windows41.ps1` still **has not executed on Windows**. Native Windows compiler and Windows S2 remain open. Canonical Linux source is unchanged at **15,559** bytes with zero fixed padding. Preserve the requirements and [`docs/STYLE.md`](docs/STYLE.md) voice and source-comment rules.

---

# Active handoff — Iteration 40 Windows BF byte I/O

The current experimental [Windows backend](docs/WINDOWS_LINEAR_IO_PE.md) supports six of eight commands, up to 64 linear BF instructions, via BF-owned Win32 imports and x64 code generation. The Linux-built stage was tested on Linux only; **Windows loader and Windows S2 are not verified**. Run `python3 tests/verify_windows_linear_io.py`, `python3 tools/check_docs.py` and review [the report](docs/ITERATION40_REPORT.md). The exact [Windows acceptance bundle](build/windows40_acceptance/manifest.json) must be executed on an actual Windows x64 machine. Preserve the canonical Linux S2 and archived Android bounded S2; 300,000-command Android support remains open. Keep all authoritative compiler logic in ordinary Brainfuck; Python authoring/transport utilities are not production compilers. Consult [documentation style](docs/STYLE.md). Earlier instructions are historical.

---

# Active handoff — Iteration 39 Windows bounded PE compilation

Use [Windows linear compiler notes](docs/WINDOWS_LINEAR_PE.md), [iteration report](docs/ITERATION39_REPORT.md) and [evidence](evidence/iteration39_windows_linear_pe.json). The 10,831-instruction `.bf` program is the sole source of the source-dependent Windows x64 PE writer; it accepts a maximum of 64 `+ - > <` filtered commands. **No Windows execution** and no byte I/O/loops/S2 have been verified. Run `python3 tests/verify_windows_linear_pe.py` and `python3 tools/check_docs.py` before changes. Preserve existing Linux S2 and archived Android bounded S2, and do not confuse structural Windows PE validation with target execution. Previous instructions are historical.

---

# Active engineering handoff — Android S2 archived; Windows now active

Read [the current report](docs/ITERATION38_REPORT.md). The uploaded repository records bounded Android-native S2 on Pixel 8 Pro; an offline audit verified the stage and program witnesses, but did not repeat ADB execution. The new Windows PE32+ fixed exit emitter is raw Brainfuck and **not** a Windows compiler. Preserve Linux S2 and standard BF source purity. The next target implementation step is Windows loader execution, followed by BF-owned decoding, x64 emission and I/O. Older agent instructions remain below.

---

# Android USB device follow-up handoff — 2026-10-13

The expanded generated-program loader gate passed **13/13** fixtures through **2,000 commands including loops** on Pixel 8 Pro, Android 17/API 37. Read [device follow-up and performance diagnosis](docs/ANDROID_DEVICE_FOLLOWUP_20261013.md) and [actual byte/status results](evidence/android_device_20261013/device_verification.json). The isolated GM APK passed **21 test executions**, including **634,229 parity comparisons**, but uses its existing BF-to-C/JNI backend. Native BF did not beat the strongest C transfer baseline; warmed Java still beats uncached BF/JNI policies. No Android-native compiler/S2 or callable BrainfuckCC APK backend exists. Keep BF production logic authoritative, preserve raw/historical evidence, and continue Android-native compiler work before Windows. Older handoffs below retain their original context.

---

# Iteration 37 agent handoff

Run [Android device acceptance](docs/ANDROID_DEVICE_ACCEPTANCE.md) on real Android with `adb` when available, then preserve the returned raw bytes and device properties. The offline 13-program suite proves only Linux-hosted BF compiler stages and AArch64 simulation, not Android loader execution or Android-native self-hosting. The production compiler and code generation must remain standard Brainfuck. Consult [docs/STYLE.md](docs/STYLE.md) and [Iteration 37 report](docs/ITERATION37_REPORT.md); no Windows implementation before Android native S2. Older agent history follows.

---

# Iteration 36 current handoff

The opt-in Android AArch64 BF-only `--multiclass --tape-relocated --loops` pipeline now accepts **2,000 linear or loop-containing commands**. The unchanged two-byte BF relocation code was verified beyond its earlier 512-slot bound; Linux-native execution and Linux-hosted AArch64 simulation are the only new execution evidence. Run [focused tests](tests/verify_android_wide_loops_2000.py), read [report](docs/ITERATION36_REPORT.md) and [evidence](evidence/iteration36_wide_loops_2000.json). **No Android loader/device retest, Android compiler S2, 300,000-command artifact or Windows PE32+ implementation.** Preserve the unchanged canonical BF compiler and follow [documentation style](docs/STYLE.md). Historical notes follow.

---

# Iteration 35 active handoff

Iteration 35 active facts: the opt-in BF-owned [tape rebase](experiments/android_tape_rebase.bf.notes.md) supports 2,000 linear or 1,024 loop commands with Linux-hosted simulation only. The Linux BF compiler remains unchanged and self-hosted; actual Android loader tests, Android-native S2, generalized 300,000-command output and Windows remain open. Run [test](tests/verify_android_tape_rebase.py) and read [report](docs/ITERATION35_REPORT.md).
---

# Iteration 34 active engineering handoff

Android AArch64 `--multiclass --loops` now generates up to **1,024** executable BF commands using BF-owned loop relocation and four ELF layout classes, verified on Linux-hosted native stages and AArch64 simulation only. The new [Iteration 34 report](docs/ITERATION34_REPORT.md) and [source notes](experiments/android_multiclass_elf_relayout.bf.notes.md) explain the bounded stage. The canonical Linux source remains **15,559 bytes**. Do **not** claim Android loader execution, Android-native compiler/S2, 300,000-command output, or Windows PE32+. Next fix BF-authored tape placement and startup beyond the `0x10000` RW address, then test real Android loaders. Read [documentation style](docs/STYLE.md); older handoffs follow.

---

# Iteration 33 active engineering handoff

The new standard Brainfuck two-byte-index patcher supports loops through **512 commands** with `--page-class --loops`, including the 331-command transition. The **15,559-byte** canonical Linux compiler is unchanged; fresh native Stage 1→2 was byte-identical, and no independent cold Stage 0 ran. The source-comment, tape, safety and documentation rules remain in force. Next: extend BF ELF size classes and validate through a real Android loader before Android-native compiler and self-hosting work. Windows PE32+ remains unimplemented. Start with [Iteration 33](docs/ITERATION33_REPORT.md) and [documentation style](docs/STYLE.md).

---

# Iteration 32 engineering handoff

The new 6,009-command standard Brainfuck patcher raises the `--page-class --loops` and `--dynamic --loops` caps to **255**; 512-command `--page-class` output remains **linear only above 255**. Run `python3 tests/verify_android_wide_slot_255.py` and read [`docs/ITERATION32_REPORT.md`](docs/ITERATION32_REPORT.md). Linux-native BF stage execution and AArch64 simulation passed, not new Android device execution. Linux compiler Stages 1–2 remain byte-identical and cold Stage 0 was not rerun. Next: BF-owned two-byte relocation indices and 331+ command loops, then loader testing and Android native selfhosting. Windows remains deferred.

---

# Iteration 31 engineering handoff

An opt-in standard BF PIE writer now supports 512 linear commands and two 16 KiB aligned file classes. Loops remain limited to 74 commands by the independent BF patcher. Run `python3 tests/verify_android_page_class_elf.py` and read [`docs/ITERATION31_REPORT.md`](docs/ITERATION31_REPORT.md). The new images have only been tested in Linux-hosted AArch64 simulation. Android-native compiler/self-hosting and Windows PE are not implemented. Do not change historical Linux S2 claims; fresh Linux native Stage 1 and 2 compilation passed, independent cold Stage 0 was not repeated.

---

# Iteration 30 developer note

The optional BF-native Android ELF layout writer is now [`experiments/android_dynamic_elf_wrapper.bf`](experiments/android_dynamic_elf_wrapper.bf); its source/test contract is [`docs/ITERATION30_REPORT.md`](docs/ITERATION30_REPORT.md). It calculates dynamic RX load length for 0..255 linear commands and retains 74 slots for bracketed commands. The aligned file is still fixed at 16,480 bytes in this class; Android device/native S2 and Windows work are not complete. Keep `compiler/core.bf` authoritative, and continue [the documentation style](docs/STYLE.md).

---

# Iteration 29 wide loop relocation update

The opt-in `bootstrap/run_android_extended.py --loops` path now integrates BF-native 24-bit bracket pairing, AArch64 26-bit branch encoding, BF slot patching, and the fixed **74-command** ELF wrapper. Linux-executed BF stages and **85 two-base AArch64 program simulations** pass; **Android-device execution of these new images and Android-native compiler self-hosting have not occurred**. Dynamic ELF layout and source capacity remain blockers. See `docs/ITERATION29_LOOP_FOLLOWUP.md` and `evidence/iteration29_wide_slot_patch.json`.

---

# Current implementation update — Iteration 29

A new BF-native extended Android AArch64 **linear** path supports up to 74 commands in fixed 4,192-byte PIE images; Linux-hosted simulator evidence only. See `docs/ITERATION29_REPORT.md` and `evidence/iteration29_extended_slots.json`. The existing ten-slot loop-capable path is separate and unchanged; do not confuse its historical Android execution with tests of the new images. Native Android compiler/self-hosting and Windows are still outstanding. Prioritize BF-owned bracket relocation and dynamic ELF layout. Do not move native code generation into Python.

---

# Agent rules

## Read before implementation

The current task order is **Android first, Windows second**. Documentation reconciliation **D0** and Iteration 26 contract work are complete; **Iterations 27–28 have partial Linux-executed BF primitives**: the wide source scanner and 24-bit bracket metadata/stack pairing pass their dedicated tests, but wide Android relocations and native code emission are not implemented. Full cold-stage revalidation remains outstanding. Read [`docs/ANDROID_COMPILER_PROTOCOL_V1.md`](docs/ANDROID_COMPILER_PROTOCOL_V1.md), [`docs/STATE.md`](docs/STATE.md), [`docs/PLATFORM_ACCEPTANCE.md`](docs/PLATFORM_ACCEPTANCE.md), [`docs/IMPLEMENTATION_ROADMAP.md`](docs/IMPLEMENTATION_ROADMAP.md), [`docs/HANDOFF.md`](docs/HANDOFF.md) and [`docs/STYLE.md`](docs/STYLE.md). The baseline plan is **14 Android iterations (26–39)**, **6 Windows (40–45)** and **2 common release iterations (46–47)**; planned is not executed.

## Source and semantics

The only authoritative compiler is `compiler/core.bf`, raw standard Brainfuck. Only `><+-.,[]` execute. Inline human comments must contain **no** executable Brainfuck characters, because normal BF interpreters do not treat `#` as a real comment delimiter. Preserve source offsets and SHA-bound `compiler/core.bf.notes.md`. Tools in Python or C can seed Brainfuck interpretation, transport bytes, inspect artifacts, independently test outputs, or benchmark. They may **not** implement production parsing, optimization, relocation, machine encoding, or executable construction.

V0 remains 8-bit modulo-256 cells, zeroed 65,536-cell tape, zero-on-EOF, checked pointer boundaries and exact loop semantics. Source/diagnostic protocols and any different execution profile are versioned external contracts, **not new BF instructions**.

## Evidence and required gates

Existing Linux x86-64 **S2 EXECUTED** is authoritative: `compiler/core.bf` has **15,559 source bytes**, **14,859 BF instructions**, native ELF **475,703 bytes**, a 16,128-command source limit, 255 nested loops, and **zero fixed ELF padding**. Two independent BF seeds and native Stages 0–2 agreed in the archived run. The header emitter's scratch-cell 61 safety argument is **conditional**, not a whole-compiler proof.

The new 1,170-instruction BF scanner filters/counts 300,001 instructions; the 2,524-instruction metadata and 1,707-instruction stack matcher now resolve bracket pairs with 24-bit positions (Linux-executed). **The Android code emitter still accepts only ten commands**. The ten-command Android AArch64 native shell program emitter, its optional BF optimizers and generated Android executables have run in limited tests on Pixel 8 Pro, Android 17/API 37, as described in `docs/ANDROID_NATIVE_OPTIMIZATION.md`. **There is no Android-native compiler execution or self-hosting yet.** Windows x86-64 PE32+ target/compiler is **UNIMPLEMENTED**. Neither a simulated AArch64 branch nor Windows C BF seed tests count as native compiler porting.

After any BF source edit, regenerate navigation and run `sh tools/verify_release.sh`, target-specific semantic and adversarial tests and applicable native self-hosting stages. Inability to run a target OS test means **UNVERIFIED**. Keep historical artifact/hash evidence intact. Update the corresponding `docs/STATE.md`, `docs/TARGETS.md`, `docs/HANDOFF.md`, `docs/OPEN_ISSUES.md`, the generated evidence-backed `status/CONFORMANCE_MATRIX.json` and roadmap only when actual facts change.

Read [`docs/STYLE.md`](docs/STYLE.md) for maintained documentation voice. Report exact tools, inputs, outputs, failures, test counts and hashes. Do not invent performance proof, universal Android capability, APK support or application-bridge behavior. The fastest C native Android transfer baseline still has an overlapping confidence interval with the measured BF result; **NOT_PROVEN_FASTEST** stands.

## Latest engineering handoff

Iteration 28 now also has a Linux-executed standard BF stage for wide AArch64 `B` branch word **records**, but the final Android image still uses the legacy ten-command emitter. Follow [`docs/HANDOFF.md`](docs/HANDOFF.md); do not claim scalable Android ELF or native self-hosting until the BF record consumer, dynamic image emission, and target execution are complete.

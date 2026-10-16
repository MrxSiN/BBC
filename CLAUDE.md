# Project name — BrainfuckCC

The project is now **BrainfuckCC** (repository: https://github.com/MrxSiN/BrainfuckCC). The former names `brainfuckC`/`brainfuckc` and `brainfuck-native` are retired in maintained code and docs: the Android JNI test bridge is now Java package `org.brainfuckcc`, library `libbrainfuckcc_bridge.so` and property `brainfuckcc.bridge.absolutePath`. Archived `evidence/` and `build/` records keep their original names and paths as historical data. No compiler source, BF stage or emitted machine code changed.

---

# Iteration 65 active gate — Android callable runtime acceptance

File backed patch occupancy removes linear Python heap growth in relocation transport without modifying BF code generation. Continue with the device Bionic/ART/APK gates, original policy parity and native dynamic self hosting. [Iteration 65 report](docs/ITERATION65_DYNAMIC_RELOCATION_STORAGE.md). Keep earlier paths only as fallbacks.

---

# Iteration 64 current task — Android callable execution evidence

ELF metadata and BFP1 machine-code/loop-relocation validation both pass locally on standard-BF outputs; the authoritative BF code generator is unchanged. Next: real ARM64 Android Bionic and JNI tests, full original policy parity and dynamic Android-native self-hosting. Keep bounded paths as fallbacks until verified. [Report](docs/ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md).

---

# Iteration 63 current task — verify Android BF callable execution

The Linux-hosted BF-generated shared-object emitter has a constant-memory, fail-closed ELF postflight contract with 240 generated programs and 960 reference simulator comparisons. Its job is to reject corrupt BF-generated metadata, not to produce metadata in Python. Run the [iteration 63 verification suite](docs/ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md), then obtain real Android Bionic, ART, installed-APK and native-selfhost evidence. Keep legacy paths as fallbacks until the replacement is proved. The prior 100-million-command goal remains retired.

---

# Iteration 62 current task — installed APK callable verification

The BF-native dynamic all-eight-command AArch64 compiler output is unchanged. Added a test-only Gradle APK with nine BF-generated DSOs and JNI bridge, plus hash- and nonce-checked ADB installed-app acceptance. Local tests run JNI assertions only against C stubs; **device execution, Gradle build and APK parity are not proven**. Preserve old compilation routes solely as fallbacks until Android policy parity and target-native dynamic compiler self-hosting pass. [Technical report](docs/ITERATION62_ANDROID_APK_ACCEPTANCE.md).

---

# Iteration 61 current task — Android ART/JNI acceptance

The compiler's all-eight-instruction resource-scaled Brainfuck code generation remains unchanged. `tools/android_bfp1_bridge/device_acceptance61.py --device` now tests BF-produced DSOs through Android ART/JNI and native loader. Local host JVM tests use **test-only C stubs**; actual device results are unverified. Prioritize real Android loader/JNI evidence, then APK namespace, remaining original policies and native self-hosting. Keep prior implementations as fallbacks, not active throughput milestones. [Report](docs/ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md).

---

# Iteration 59 active mission — dynamic callable AArch64 DSO

> Active iteration 60: loader device-acceptance fixture path in `docs/ITERATION60_ANDROID_LOADER_ACCEPTANCE.md`. BF codegen unchanged; Android actual execution unverified. Retain fallback paths.

Standard Brainfuck compiler stages now emit dynamically sized all-eight-command callable AArch64 DSOs and an exported `bfc_call_v1` ELF symbol. The independent ELF linker test passed, and the Linux JVM ran the new JNI transport using a test-only non-BF stub. There is **no new Android loader or native self-hosting evidence**. Prioritize actual Android `dlopen`/JNI execution, the missing eight pinned original policies, then native Android S2. Keep bounded/freestanding fallbacks only until the new path passes Android parity and safety gates. Do not resurrect an arbitrary command-count target. [Technical report](docs/ITERATION59_DYNAMIC_CALLABLE_DSO.md).

---

# Iteration 57 active mission — fully dynamic callable Brainfuck compiler

Drop the former 100-million-command native compilation milestone. Work only on a resource-growing BF-owned callable backend, especially dynamic bracket metadata, branch relocation, byte-exact ABI and native Android loader/JNI execution. Iteration 57 six-operator callable ELF compiler and 64-bit BF header math are tested, not fully complete. Retain old compiler paths solely as fallbacks until replacement tests pass. [Report](docs/ITERATION57_DYNAMIC_CALLABLE_LINEAR.md).

---

# Iteration 56 current task state

The opt-in standard-Brainfuck `policy_clear56.bf` pass reduces original TwitterHideAds `action.bf` from 4,723 RLE records to 3,819 and the callable compiler emits a 15,300-byte AArch64 image on Linux. Ten BF-original-versus-optimized-IR frames agree; Gmail images preserve their existing hashes. Device execution, Twitter APK/JNI parity and the 100M target remain open. [Test and technical contract](docs/ITERATION56_TWITTER_ACTION_CLEAR.md); follow [docs/STYLE.md](docs/STYLE.md).

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


## Current 100M objective

The new [BF 100M source-stage evidence](docs/ANDROID_100M_CAPACITY.md) is a parsing and address-width primitive; it is not the completed Android compiler. Follow the genuine 100M **per-unit** capacity objective with compact BF-owned code generation, paired branches, valid AArch64 libraries and verified Android execution. Windows work is preserved, not claimed as completed.

---

**Current product acceptance (Iteration 46; not implemented):** Mandatory source set: all 11 GmailHideAds/TwitterHideAds/ThreadsHideAds policies (1,312,912 total commands; largest 296,307). Implement direct BF-to-AArch64, per-program tape/host protocol, Android shared-library and APK parity gates. Stretch target >=10M commands/unit and >=100M aggregate. [Contract](docs/ANDROID_APPLICATION_ACCEPTANCE.md).

---

# Iteration 45 Android engineering checkpoint

See [the current Android extension](experiments/android_adrp_high_byte_class8.bf.notes.md) and [focused verification](tests/verify_android_class8_2719.py). Stage source remains eight-instruction standard Brainfuck; generated ELF image capacity is 2,719 commands including loops under `--multiclass --tape-relocated --loops`. Only Linux-native BF execution and AArch64 simulation are newly verified, not an Android loader run or 300,000-command acceptance. Do not rewrite historical evidence or introduce foreign production compiler logic. [Style](docs/STYLE.md).

---

# Iteration 44 handoff

The latest Windows BF-only executable backend accepts **192 commands**, using [two new BF-native stages](docs/WINDOWS_FULL192_PE.md) and the transport adapter `bootstrap/run_windows_full192.py`. **77** Linux CPU shim cases passed; this does not verify a Windows loader or Win32 APIs. Run `tests/verify_windows_full192.py`, `tests/verify_windows_full128.py`, then `tools/check_docs.py`. Use [Iteration 44 evidence](evidence/iteration44_windows_full192.json); keep 64/128 historical paths and canonical Linux code unchanged. Windows native S2 and Android 300,000 commands are still outstanding.

---

# Iteration 43 current handoff

Windows native PE output now has an opt-in **128-command, all-eight-instruction BF-only path**, documented in [the contract](docs/WINDOWS_FULL128_PE.md) and [report](docs/ITERATION43_REPORT.md). The new BF stages passed 100 CPU-executed Linux-shim program comparisons and 868 branch checks; **no Windows loader run or Windows S2**. Re-run `tests/verify_windows_full128.py` and `tools/check_docs.py` for future edits. Keep test-only Python/C outside compiler logic and historical 64-command files unchanged. Linux S2 and archived Android bounded S2 remain separate; Android 300,000-command acceptance is still open.

---

# Iteration 42 current handoff

Windows BF source/parser/PE emitter remain standard Brainfuck. New test-only [Linux CPU execution harness](docs/WINDOWS_LINUX_CPU_EXECUTION.md) checks the generated x64 bytes against independent semantics: 164 source cases and 11 archived smoke executables pass with a Win32 **shim**, not the Windows loader. Windows target-native execution/S2 and more than 64 commands remain open. See [report](docs/ITERATION42_REPORT.md) and [evidence](evidence/iteration42_windows_x64_cpu_shim.json). Existing Linux S2 and archived bounded Android S2 are unchanged; do not conflate shim tests with Windows acceptance.

---

# Iteration 41 current handoff

Continue the eight-instruction BF Windows PE backend from [the bounded target contract](docs/WINDOWS_FULL64_PE.md) and [test evidence](evidence/iteration41_windows_full64.json). The BF encoder and patcher operate only on trusted, BF-generated frames. Windows loader testing, larger source capacity and native S2 are **not completed**. The 15,559-byte canonical Linux BF source and its zero fixed trailing padding are unchanged. See [`docs/STYLE.md`](docs/STYLE.md) and avoid introducing a foreign-language authoritative compiler.

---

# Active handoff — Iteration 40 Windows BF byte I/O

The current experimental [Windows backend](docs/WINDOWS_LINEAR_IO_PE.md) supports six of eight commands, up to 64 linear BF instructions, via BF-owned Win32 imports and x64 code generation. The Linux-built stage was tested on Linux only; **Windows loader and Windows S2 are not verified**. Run `python3 tests/verify_windows_linear_io.py`, `python3 tools/check_docs.py` and review [the report](docs/ITERATION40_REPORT.md). The exact [Windows acceptance bundle](build/windows40_acceptance/manifest.json) must be executed on an actual Windows x64 machine. Preserve the canonical Linux S2 and archived Android bounded S2; 300,000-command Android support remains open. Keep all authoritative compiler logic in ordinary Brainfuck; Python authoring/transport utilities are not production compilers. Consult [documentation style](docs/STYLE.md). Earlier instructions are historical.

---

# Active engineering state — Iteration 39

Windows now has an experimental standard-BF source-dependent PE writer for 64 linear `+ - > <` commands. See [the contract](docs/WINDOWS_LINEAR_PE.md), [tests](tests/verify_windows_linear_pe.py) and [report](docs/ITERATION39_REPORT.md). GNU `objdump` and a BF reference validate emitted images; the Windows loader, I/O, bracket branches and Windows S2 are **not tested or implemented**. The original Linux and Android compiler sources are unchanged. Continue with target execution and BF-owned Windows byte I/O; keep the 300,000-command Android requirement open. Previous checkpoints below are historical.

---

# Active engineering handoff — Android S2 archived; Windows now active

Read [the current report](docs/ITERATION38_REPORT.md). The uploaded repository records bounded Android-native S2 on Pixel 8 Pro; an offline audit verified the stage and program witnesses, but did not repeat ADB execution. The new Windows PE32+ fixed exit emitter is raw Brainfuck and **not** a Windows compiler. Preserve Linux S2 and standard BF source purity. The next target implementation step is Windows loader execution, followed by BF-owned decoding, x64 emission and I/O. Older agent instructions remain below.

---

# Iteration 37 current engineering gate

Use the [Android device acceptance guide](docs/ANDROID_DEVICE_ACCEPTANCE.md) and [Iteration 37 report](docs/ITERATION37_REPORT.md). The 13-case bundle is ready but **not Android executed**; offline structural checks and 24 simulated executions passed. Do not infer Android S2 or begin Windows. Keep the authoritative Linux compiler source unchanged and honor [documentation style](docs/STYLE.md). Older notes follow.

---

# Iteration 36 current handoff

The standard BF Android pipeline now supports **2,000 commands including loops** only in `--multiclass --tape-relocated --loops`; all native branch words still come from unchanged BF stages. [Report](docs/ITERATION36_REPORT.md), [test](tests/verify_android_wide_loops_2000.py), [evidence](evidence/iteration36_wide_loops_2000.json). Linux-native stage execution and AArch64 simulation are proven; native Android compiler execution/S2 and Windows remain absent. The original Linux BF compiler remains unchanged. Historical notes follow.

---

# Iteration 35 active handoff

Iteration 35: the latest experimental Android `--multiclass --tape-relocated` path uses a BF-only page-aligned tape rebase and RX length fix. It supports 2,000 linear / 1,024 loop commands in Linux-hosted simulation, not Android device execution or native self-hosting. Prioritize larger loops and real Android loader verification before Windows. See [Iteration 35](docs/ITERATION35_REPORT.md).
---

# Iteration 34 active handoff

The new Brainfuck-only `--multiclass --loops` AArch64 pipeline supports **1,024 commands** in four ELF classes. Linux-native BF-stage execution and AArch64 simulation are verified, but Android device execution and Android-native self-hosting remain unimplemented. See the [iteration report](docs/ITERATION34_REPORT.md), [tests](tests/verify_android_multiclass_elf.py) and [style guide](docs/STYLE.md). The older 512-command notes below are historical. The remaining blocker is BF tape relocation for executable RX code past the fixed `0x10000` RW segment; Windows follows Android S2.

---

# Iteration 33 active handoff

Standard BF now owns two-byte slot relocation through **512** commands in opt-in Android AArch64 `--page-class --loops` builds. This is Linux-native stage execution plus AArch64 simulation, **not Android device execution** or Android-native self-hosting. Full 300,000-command output and Windows PE32+ are not implemented. See [Iteration 33 report](docs/ITERATION33_REPORT.md) and [test](tests/verify_android_wide_slot_512.py); the older notes below remain historical.

---

# Iteration 32 engineering handoff

BF-owned loop relocation now handles up to **255 commands** with `--page-class --loops`, alongside **512 linear** commands under `--page-class`. The previous 74-slot default `--loops` route is intact. Verify with [`tests/verify_android_wide_slot_255.py`](tests/verify_android_wide_slot_255.py), consult [`docs/ITERATION32_REPORT.md`](docs/ITERATION32_REPORT.md) and preserve the source/comment and documented tape rules. Android-native compiler execution and self-hosting were not achieved; Windows PE remains unimplemented. The next priority is multi-byte loop positions and the 331-command file-class crossing.

---

# Iteration 31 engineering handoff

An opt-in standard BF PIE writer now supports 512 linear commands and two 16 KiB aligned file classes. Loops remain limited to 74 commands by the independent BF patcher. Run `python3 tests/verify_android_page_class_elf.py` and read [`docs/ITERATION31_REPORT.md`](docs/ITERATION31_REPORT.md). The new images have only been tested in Linux-hosted AArch64 simulation. Android-native compiler/self-hosting and Windows PE are not implemented. Do not change historical Linux S2 claims; fresh Linux native Stage 1 and 2 compilation passed, independent cold Stage 0 was not repeated.

---

# Iteration 30 status and next safe change

The BF-only `--dynamic` ELF wrapper now handles 255 **linear** AArch64 instructions in Linux-hosted simulations, with an RX segment sized by BF arithmetic. The current output file is still 16,480 bytes; loop-containing code remains 74 slots. Next implement truly variable aligned file size across ELF segment size classes, extend the BF bracket patcher, and test Android loader behavior. Reference [`docs/ITERATION30_REPORT.md`](docs/ITERATION30_REPORT.md) and [`docs/STYLE.md`](docs/STYLE.md). Do not describe this as Android-native self-hosting.

---

# Iteration 29 wide loop relocation update

The opt-in `bootstrap/run_android_extended.py --loops` path now integrates BF-native 24-bit bracket pairing, AArch64 26-bit branch encoding, BF slot patching, and the fixed **74-command** ELF wrapper. Linux-executed BF stages and **85 two-base AArch64 program simulations** pass; **Android-device execution of these new images and Android-native compiler self-hosting have not occurred**. Dynamic ELF layout and source capacity remain blockers. See `docs/ITERATION29_LOOP_FOLLOWUP.md` and `evidence/iteration29_wide_slot_patch.json`.

---

# Current implementation update — Iteration 29

A new BF-native extended Android AArch64 **linear** path supports up to 74 commands in fixed 4,192-byte PIE images; Linux-hosted simulator evidence only. See `docs/ITERATION29_REPORT.md` and `evidence/iteration29_extended_slots.json`. The existing ten-slot loop-capable path is separate and unchanged; do not confuse its historical Android execution with tests of the new images. Native Android compiler/self-hosting and Windows are still outstanding. Prioritize BF-owned bracket relocation and dynamic ELF layout. Do not move native code generation into Python.

---

# Same compiler, same rules

Read [`AGENT.md`](AGENT.md) and the [Android-first implementation roadmap](docs/IMPLEMENTATION_ROADMAP.md). Iterations **27–28 are partial** (wide BF scanning and bracket pairing executed on Linux; general Android relocation and emission pending); Windows follows Android. Authoritative compiler logic remains only standard Brainfuck in `compiler/core.bf`; no ninth instruction or hidden C/Python/Rust codegen.

Keep the documented V0 tape profile, Linux native S2 regression gates, and original output/diagnostic behavior. The source is **15,559** bytes, compiler output has **zero** fixed ELF padding, and Android's ten-command emitted programs **have executed on a device**, but Android-native compiler self-hosting and Windows target emission do not exist. See [`docs/ANDROID_COMPILER_PROTOCOL_V1.md`](docs/ANDROID_COMPILER_PROTOCOL_V1.md) and [`docs/STATE.md`](docs/STATE.md), [`docs/PLATFORM_ACCEPTANCE.md`](docs/PLATFORM_ACCEPTANCE.md), and [`docs/STYLE.md`](docs/STYLE.md) for current facts, evidence limits and writing style. Plans are not evidence.

Iteration 28 evidence: [`docs/ITERATION28_REPORT.md`](docs/ITERATION28_REPORT.md) and [`evidence/iteration28_wide_brackets.json`](evidence/iteration28_wide_brackets.json). The Android native emitter remains limited to ten commands.

## Iteration 28 continuation

Wide AArch64 branch words are computed by a new 13,985-command BF stage on Linux. This is record evidence only; the final Android ELF is still ten-command bounded. See [`docs/ITERATION28_REPORT.md`](docs/ITERATION28_REPORT.md) and [`docs/HANDOFF.md`](docs/HANDOFF.md).

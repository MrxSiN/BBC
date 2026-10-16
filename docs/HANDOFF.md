# Iteration 65 handoff — Growing callable relocation bookkeeping

Use `python3 -m tests.verify_android_dynamic_callable65` to check sparse file backed duplicate patch records, the injected duplicate rollback, five byte identical iteration 64 reference DSOs and a 12,000 loop pair BF generated shared library. Compilation stays standard BF; this is transport storage only. Linux simulator and JNI host regressions passed, but Android Bionic/ART/APK and Android native dynamic compiler self hosting remain unverified. Proceed with device execution; retain fallbacks until replacement proof. [Iteration 65 report](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 64 handoff — native callable stream checked

Run `python3 -m tests.verify_android_dynamic_callable64` to verify BF-generated AArch64 code templates and all matching signed-64-bit loop relocations. `bootstrap.android_dynamic_callable59` now invokes **both** `android_callable_elf_validate63` and `android_callable_code_validate64` on the temporary output before atomically installing it. The new scanner uses constant-size byte reads and file-backed loop records, without a fixed bracket depth. It never generates code. Local tests passed; the Android shell loader, actual ART/JNI, installed APK, remaining eight original policy sources, original app parity and native Android dynamic compiler self-hosting still need executed evidence. Preserve historical tests and bounded lanes as fallbacks until these gates pass. [Details](ITERATION64_DYNAMIC_CALLABLE_CODE_INTEGRITY.md).

---

# Iteration 63 handoff — DSO integrity gate and Android loader

Compilation via `bootstrap.android_dynamic_callable59` now validates the BF-generated ELF shared object with `bootstrap.android_callable_elf_validate63` before its atomic output replacement. The validator reads only the first 1,024 bytes, checks the 64-bit image extent and the exact callable export contract, and never repairs the BF generator. The completed 240-case randomized regression passed 960 reference-vs-AArch64 simulator comparisons and 44 deliberate structural corruptions were rejected. A simulated BF header corruption left the existing output untouched. This remains local structural and simulated evidence, **not actual Android dynamic loading**. Run `python3 -m tests.verify_android_dynamic_callable63`, then obtain real Bionic and ART/JNI results using the existing Android loader and APK harnesses. Do not remove legacy fallbacks until target-side tests, original policy parity and Android-native self-hosting are complete. [Report](ITERATION63_DYNAMIC_CALLABLE_INTEGRITY.md), [evidence](../evidence/iteration63_dynamic_callable_integrity.json).

---

# Iteration 62 handoff — real installed APK acceptance

Run [the APK acceptance adapter](ITERATION62_ANDROID_APK_ACCEPTANCE.md) on an authorized ARM64 Android device with SDK/NDK/Gradle/ADB. It builds nine BF-generated policy DSOs, packages them into a test-only debuggable app, and verifies the installed APK hash and fresh JNI acceptance transcript. Local tests use C stubs and fake ADB only; **actual APK device loading is unverified**. Also retain the separate [shell ART/JNI gate](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md). Do not remove old compiler fallbacks until Android device policy parity and native dynamic compiler self-hosting are shown. The 100M objective stays retired.

---

# Iteration 61 handoff — run Android shell and ART/JNI gates

Start with [the Iteration 61 acceptance guide](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md). `tools/android_bfp1_bridge/device_acceptance61.py --device` runs the nine BF-produced AArch64 DSO cases through both the native `dlopen` probe and `app_process` Java/JNI. Local tests `python3 -m tests.verify_android_jni61_host` and `python3 -m tests.verify_android_jni61_transport` passed using **test-only x86 policies and mock ADB**, respectively, not Android. Native BF compiler code and generated DSOs are unchanged. **Resolve actual ART/device linker behavior next**, followed by installed-APK namespace tests, eleven-policy parity and the dynamic compiler's native Android self-hosting. Do not remove legacy fallbacks yet; do not revive numerical 100M targets.

---

# Iteration 60 — actual Android loader acceptance remains open

Added a reproducible device-loader probe and nine BF-generated dynamic callable `.so` fixtures. All nine compile and pass independent BF-reference versus AArch64-instruction-simulator parity on Linux; ELF structure and host native-loader smoke pass. Linux JVM JNI bridge coverage now includes zero-length input/output, output-capacity zero and validation errors. **No Android device execution or app JNI/APK parity was performed.** Android NDK/ADB are unavailable in this runtime. Run `python3 -m tools.android_bfp1_bridge.device_acceptance60 --device --serial DEVICE_SERIAL` with `ANDROID_NDK_HOME` set on an arm64 Android device to test actual `dlopen` and policy calls. This does **not** substitute for JNI/APK parity or dynamic-compiler native Android S2. Legacy paths remain fallbacks; original BF compiler and stage code unchanged. [Iteration 60 report](ITERATION60_ANDROID_LOADER_ACCEPTANCE.md), [evidence](../evidence/iteration60_loader_readiness.json), [roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 59 — active Android DSO and JNI handoff

The new standard-BF `android_callable_dso_header59.bf` stage emits ELF64 ET_DYN PT_DYNAMIC, dynsym/dynstr/hash, section tables and checked 64-bit lengths. The existing BF-native callable all-eight-command backend remains byte-identical. Three archived original policies have structural DSOs. 13 DSO cases/52 AArch64 simulations, 15 length vectors, 13 independent code parity checks, one cross-link of the BF DSO, and real Linux host JVM JNI transport against a **test-only** stub passed. No Android `dlopen`/JNI, new BF-native Android self-hosting, eight missing policy sources or original app parity is verified. Next gate is **execute BF-produced `.so` on an actual ARM64 Android target**; test traps, gas, EOF, state persistence, source parity, then address platform-specific loader defects in Brainfuck. The 100M numerical objective is cancelled; bounded older paths remain fallbacks. [Iteration 59 report](ITERATION59_DYNAMIC_CALLABLE_DSO.md), [bridge instructions](../tools/android_bfp1_bridge/README.md), [roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Iteration 57 handoff — dynamic callable compilation only

Run `python3 -m tests.verify_android_dynamic_callable57` to verify BF-stage rebuilds, 60 small programs, 240 callable AArch64 simulated executions, checked 64-bit ELF sizing and four large linear source cases. The opt-in entry is `python3 bootstrap/android_dynamic_callable57.py program.bf -o callable.elf`. Brackets are **rejected**; next change must connect BF-owned file-backed loop metadata and signed-64 relocation to callable emission. Do not spend work on synthetic 100M thresholds or retired paths. Previous callable, freestanding and scanner experiments are temporary fallbacks, not the new production architecture. No Android-device/JNI claim. [Full contract](ITERATION57_DYNAMIC_CALLABLE_LINEAR.md), [roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 56 current Android handoff — Twitter action source-to-ELF

Run `python tests/verify_policy_clear56.py` for 136 native BF prepass comparisons, real Twitter `action.bf` end-to-end compilation, independent AArch64 byte oracle, 10 source/IR frame parity cases, and byte-identical Gmail baseline/valuefold regressions. The opt-in switch is `PolicyCompiler.compile(..., canonical_clears=True)`; the default build is unchanged. **4,096 record and 255 nesting constraints persist**; other Twitter and Threads policies, Android JNI/loader execution, and 100M full compilation remain open. [Technical contract](ITERATION56_TWITTER_ACTION_CLEAR.md).

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

# Android real-application priority — Iteration 46

## Iteration 48 handoff — 32-bit BF bracket pairing verified

Begin with [the iteration report](ITERATION48_ANDROID_100M_PAIRING.md), [BF stage](../experiments/android_100m_bracket_pairs.bf), [framed scanner](../experiments/android_100m_rle_scan_framed.bf) and `python3 tests/verify_android_100m_bracket_pairs.py`. The new transport-only CLI is `python3 bootstrap/android_100m_pair_transport.py source.bf --pairs pairs.bin`. Existing Iteration 47 scan responses have **no** event marker; only the opt-in framed variant has one, and adapters must not silently feed unframed output to the pairer. The real 100M loop pairing gate passed at nesting depth one, while 256 nesting is rejected; the eleven production policies are not compiled and AArch64 codegen remains capped at 2,719. Next: BF-owned compact IR, code-address planning, long-distance native branches, dynamic Android ELF/DSO.

---


## Current handoff — Iteration 47

The 100M raw-source stage and its Linux BF native executable are in `experiments/android_100m_rle_scan.bf` and `build/android_100m_rle_scan_x86_64_linux.elf`. Run `python3 tests/verify_android_100m_source_capacity.py` and inspect [evidence](../evidence/iteration47_android_100m_source.json). A genuine 100M AArch64 executable has **not** been generated. Continue with BF-owned IR, source-to-output relocation, dynamic ET_DYN emission, eleven policy compilation and Android-device parity. The canonical Linux compiler is unchanged (15,559 raw source bytes, 14,859 BF instructions, zero fixed padding).

---

**Iteration 46 immediate next step — real Android app acceptance (OPEN):** Start with [the pinned workload manifest](../status/ANDROID_APPLICATION_GATES.json), [acceptance contract](ANDROID_APPLICATION_ACCEPTANCE.md), `python3 tests/verify_android_app_acceptance.py` and upstream `brainfuck/programs.json`. Native AArch64 codegen is still capped at 2,719 commands and cannot compile any of the 11 18,192–296,307-command policy programs. Build streaming 32-bit+ bracket and code-offset handling with BF-owned native emission; test the 11 originals, then implement Android `.so` ABI and run all three original APK/JNI parity suites. Larger goal >=10M per unit/100M aggregate is not verified. Existing Windows and Linux paths remain unchanged.

---

# Iteration 45 Android scaling handoff

Start with [class eight stage notes](../experiments/android_adrp_high_byte_class8.bf.notes.md), [the opt-in adapter](../bootstrap/run_android_extended.py) and [the differential test](../tests/verify_android_class8_2719.py). Confirm the exact 2,378→2,379 tape segment class transition and the 2,719 hard acceptance bound. Reproduce with `python3 tests/verify_android_class8_2719.py` and `python3 tools/check_docs.py`. The stage was compiled from standard BF and corrects **three bytes** in a trusted 131,168-byte intermediate image. No external machine-code patching is permitted. The [seven-case on-device bundle](ANDROID45_ACCEPTANCE.md) is prepared (no device execution). The next gate is actual Android loader execution of the new 2,719-command images, then streaming relocations and dynamic ELF construction well beyond 16 KiB source/compiler limits; the 300,000-command objective remains unachieved. Preserve Linux S2, previously recorded Android bounded S2 and historical Windows code.

---

# Iteration 44 handoff — use the 192-slot Brainfuck Windows path

Start with the [PE192 contract](WINDOWS_FULL192_PE.md), [BF writer](../experiments/windows_loop_slots_pe_192.bf), [BF patcher](../experiments/windows_x64_loop_patch_pe_192.bf) and [differential test](../tests/verify_windows_full192.py). The transport-only CLI is `bootstrap/run_windows_full192.py`. There are 77 Linux CPU-shim comparisons; **none are real Windows loader evidence**. Run the 14-case [Windows acceptance bundle](../build/windows44_acceptance/manifest.json) on Windows x64 and retain `device_results_windows44.json`. Then address multi-byte positions and Windows native S2. Preserve Linux and Android bounded S2 plus the open Android 300,000-command target.

---

# Iteration 43 handoff — use the 128-slot Brainfuck Windows path

Start with the [PE128 contract](WINDOWS_FULL128_PE.md), [BF emitter](../experiments/windows_loop_slots_pe_128.bf), [BF patcher](../experiments/windows_x64_loop_patch_pe_128.bf), and [differential tests](../tests/verify_windows_full128.py). The adapter is `bootstrap/run_windows_full128.py`. On Linux the BF-generated PE x64 bytes passed 100 CPU-shim cases; those are **not** Windows-native tests. The pending target-side gate is the 12-image [Windows acceptance bundle](../build/windows43_acceptance/manifest.json), with `verify_windows43.ps1` to be executed on Windows x64. Linux S2 source/binary remain unchanged; retain separate Android 300,000-command acceptance planning. Next scale beyond 128 with multi-byte source indices and BF-owned PE sections, then work on Windows-native S2.

---

# Iteration 42 handoff — Linux native CPU checks for Windows PE output

The BF-owned [64-slot Windows path](WINDOWS_FULL64_PE.md) is unchanged. Use the new [test-only native x64 runner](WINDOWS_LINUX_CPU_EXECUTION.md) and `python3 tests/verify_windows_linux_x64_execution.py` for **164** differential executions and **11** original Windows smoke binaries. Its `ms_abi` C functions stand in for Win32 APIs; **do not record this as Windows loader or target-side S1/S2**. Both Linux self-hosting replay stages passed unchanged. Next gate: actual Windows x64 execution, then BF-owned capacity >64 and native Windows compiler self-compilation. [Report](ITERATION42_REPORT.md); [evidence](../evidence/iteration42_windows_x64_cpu_shim.json).

---

# Iteration 41 handoff — Windows x64 eight instructions, bounded

Current [Windows compiler contract](WINDOWS_FULL64_PE.md) and [Iteration 41 evidence](../evidence/iteration41_windows_full64.json) cover 64-command BF-owned PE generation for `><+-.,[]`, including BF-owned nested-loop branch patching. Run `python3 tests/verify_windows_full64.py`, prior Windows regressions, `python3 tests/verify_source_comments.py` and `python3 tools/check_docs.py`. **No Windows loader or Windows-native S2 execution occurred**. Use the prepared `build/windows41_acceptance/verify_windows41.ps1` on real Windows x64; preserve device_results_windows41.json. Then scale source/branch sizes. Linux source remains **15,559** bytes and **zero** fixed trailing padding. Android bounded S2 remains archived, 300,000-command goal open. Older handoffs follow.

---

# Iteration 40 checkpoint — Windows six-instruction linear PE backend

The new [Windows linear I/O backend](WINDOWS_LINEAR_IO_PE.md) generates BF-owned PE32+ images for `+ - > < . ,` from at most 64 executable commands, with imported Win32 byte I/O and deterministic x64 pointer traps. Its BF source, native Linux writer and static image tests pass; **no Windows loader/API execution** was performed. `[` and `]`, Windows-native compiler execution/S2, and Android's separate 300,000-command acceptance target remain outstanding. See [iteration report](ITERATION40_REPORT.md) and [evidence](../evidence/iteration40_windows_linear_io.json). Historical notes follow below.

---

# Iteration 39 handoff — Windows linear compiler, not native target verification

Read [Windows linear PE](WINDOWS_LINEAR_PE.md), [report](ITERATION39_REPORT.md), [source](../experiments/windows_linear_pe_64.bf), [tests](../tests/verify_windows_linear_pe.py) and [evidence](../evidence/iteration39_windows_linear_pe.json). The Linux BF compiler executes a **10,831-command** standard-BF writer that builds a fixed 2,048-byte PE image from up to 64 `+ - > <` instructions. Target movement checks use x64 `UD2`; actual Windows exception handling is unverified. Next: run generated images under Windows, implement BF-owned standard-stream I/O, then brackets and native S2. Old fixed PE seed and Linux/Android S2 sources are unchanged.

---

# Iteration 38 handoff — Android bounded S2, Windows backend first

Use [the Android evidence audit](ANDROID_NATIVE_S2_AUDIT.md), [iteration report](ITERATION38_REPORT.md) and [Windows PE seed notes](WINDOWS_PE32_SEED.md) as the current entry points. The archive has recorded Android-native self-compilation on Pixel 8 Pro (four byte-identical 933,008-byte compiler images); we checked the archive offline only. Linux **15,559-byte** BF source and **zero fixed trailing padding** remain unchanged. The Windows source `experiments/windows_pe_exit_seed.bf` emits exactly 1,536 bytes of PE32+ console code through its compiled Linux BF execution path. Next: execute that PE on real Windows, then add BF source decoding, Win32 byte I/O and branch generation, then Windows-native compiler and self-hosting. The Android 300,000-command gate remains open; do not assert that an APK or multi-ABI compiler exists.

---

# Android USB follow-up handoff — 2026-10-13

The **13-program device loader gate has passed** on Pixel 8 Pro over USB, including the 2,000-command loop artifact. Read [device follow-up](ANDROID_DEVICE_FOLLOWUP_20261013.md) and retain raw [output/status evidence](../evidence/android_device_20261013/device_verification.json). The isolated existing GM APK passed parity/robustness and repeated warmed ART tests, but uses BF-to-C/JNI rather than this native backend. Native BF did not beat the strongest C transfer baseline; BF/JNI uncached policies did not beat Java. Next compiler work remains scalable BF-owned source/code layout and a real Android-native compiler/self-hosting cycle; callable APK/JNI integration needs its own ABI. The unchanged canonical compiler is **15,559 bytes**; preserve Linux S2 and zero fixed padding. Earlier handoffs below are historical.

---

# Iteration 37 handoff — Android shell validation awaits a device

Start with the [device acceptance procedure](ANDROID_DEVICE_ACCEPTANCE.md), [report](ITERATION37_REPORT.md) and [offline test](../tests/verify_android_device_acceptance.py). Thirteen BF-generated AArch64 PIE files and raw byte/EOF/trap expectations are ready in `build/android_device_acceptance_37`. The offline suite passed 24 AArch64 simulator executions; **no Android loader test ran**. With `adb` and a spare arm64 Android shell device, execute `python3 tools/android_device_acceptance.py run-device build/android_device_acceptance_37 evidence/iteration37_android_device_results --serial SERIAL` from repository root. Keep real device evidence separate from synthetic audit files. The canonical source remains standard Brainfuck and its Linux executable passes native Stages 1→2. Android-native self-hosting, 300,000-command compilation and Windows PE32+ remain open. Older handoffs follow.

---

# Iteration 36 active handoff

**Next priority:** actual Android loader execution, then larger BF-owned ELF/relocation capacity and Android-native compiler self-hosting. The new `--multiclass --tape-relocated --loops` path supports **2,000 commands including loops** in Linux-native BF stages and Linux-hosted AArch64 simulation; there is **no target-device acceptance evidence** for this path. Start with [test](../tests/verify_android_wide_loops_2000.py), [Iteration 36 report](ITERATION36_REPORT.md) and [evidence](../evidence/iteration36_wide_loops_2000.json). Existing `--multiclass` alone retains 1,024 commands; do not change old historical evidence. Windows PE32+ follows Android target-side S2. The original Linux compiler is unchanged at **15,559** source bytes, and zero fixed ELF trailing padding remains. Earlier handoffs follow.

---

# Iteration 35 active handoff

Current: Iteration 35 implemented the BF-only [tape rebase](../experiments/android_tape_rebase.bf.notes.md), supporting 2,000 linear / 1,024 bracketed commands in Linux-hosted AArch64 simulation. The fixed tape overlap is resolved **for six bounded image classes**, not for arbitrary source sizes. The 300,000 command target, actual Android loader testing, Android-native compiler/S2 and Windows remain open. Run [focused tests](../tests/verify_android_tape_rebase.py); [report](ITERATION35_REPORT.md). The previous reports below are historical.
---

# Current handoff — Iteration 34 AArch64 BF four-class images

Run `python3 tests/verify_android_multiclass_elf.py` and read [Iteration 34 evidence](../evidence/iteration34_multiclass_elf.json), the [report](ITERATION34_REPORT.md), and [BF source notes](../experiments/android_multiclass_elf_relayout.bf.notes.md). The opt-in `--multiclass --loops` path emits BF-owned AArch64 PIE images for **1,024** executable commands in four classes. The original Linux compiler source is **15,559 bytes** and its emitted native ELF has **zero fixed trailing padding**. **Not complete:** Android loader testing, Android-native compiler execution and S2, and 300,000-command source-to-artifact output. The original 74/255/512 modes and historical evidence remain intact.

**Next:** redesign tape placement and ADRP startup in standard BF before scaling executable code past the current `0x10000` tape segment, then execute the new image through an actual supported Android loader. Do not just raise the 1,024-command limit: RX and RW would collide above approximately 1,354 slots. Windows PE32+ follows Android-native S2. Historical handoffs follow below.

---

**Verification addendum:** 71 source programs, 8,137 branch-pair checks and 142 simulator runs passed in Iteration 34. Fresh native Linux Stage 1→2 compilation passed byte-for-byte; cold Stage 0, Android loader tests and the full release suite were not rerun. An independent 75-million-step seed-interpreter comparison was inconclusive. See [Iteration 34 report](ITERATION34_REPORT.md).

# Current handoff — Iteration 33 512-command loop relocation

`--page-class --loops` now accepts **512** BF commands with loops; the Brainfuck-only patcher has two-byte slot indices. This includes 330 and 331 commands with tested native AArch64 ELF layout. Use [Iteration 33 report](ITERATION33_REPORT.md), [source](../experiments/android_wide_slot_patch_512.bf), [tests](../tests/verify_android_wide_slot_512.py), and [evidence](../evidence/iteration33_wide_slot_patch_512.json). The authoritative Linux compiler remains **15,559** bytes, and fixed trailing ELF padding remains **zero**. The project has not executed these generated programs on Android hardware or built an Android-native self-hosting compiler. Next implement >512 general ELF classes, then loader/device execution and compiler S2; Windows follows. Older handoffs below are historical.

---

# Current handoff — extend loop indices beyond 255

Iteration 32 adds [`../experiments/android_wide_slot_patch_255.bf`](../experiments/android_wide_slot_patch_255.bf), a 6,009-command standard Brainfuck slot patcher. In `bootstrap/run_android_extended.py`, use `--page-class --loops` for up to **255** bracketed commands, or `--page-class` for **512 linear** commands. The default `--loops` path remains bounded at 74. See [`ITERATION32_REPORT.md`](ITERATION32_REPORT.md) and [the test](../tests/verify_android_wide_slot_255.py).

**Next gate:** implement a BF-owned relocation table with multi-byte slot indices, verify loop programs spanning **330→331 commands** in both ELF size classes, then advance size-class output and Android loader execution. No Android compiler binary was run on device, and Android self-hosting remains absent. Linux native Stages 1–2 passed again; cold Stage 0 was not rerun. Windows follows Android acceptance.

---

# Current handoff — complete scalable AArch64 loop relocation

The new [`../experiments/android_page_class_elf_wrapper.bf`](../experiments/android_page_class_elf_wrapper.bf) emits BF-owned ELF PIE bytes in two size classes using a **two-byte slot count**. `bootstrap/run_android_extended.py --page-class` handles **512 linear commands**; `--page-class --loops` is deliberately still **74 commands maximum**. Regression test: `python3 tests/verify_android_page_class_elf.py`. Current evidence: [`ITERATION31_REPORT.md`](ITERATION31_REPORT.md) and [`../evidence/iteration31_page_class_elf.json`](../evidence/iteration31_page_class_elf.json).

**Next:** remove the BF slot patcher's fixed 74-slot table, preserving BF-owned 24-bit bracket matching and 26-bit branch encoding; verify nested loops beyond 255 slots and across the 331-command ELF boundary. Keep testing with a reference BF interpreter and at two load bases. Then expand ELF size classes further and run on an Android loader. Do not call simulator results Android device execution or native Android self-hosting. Linux native Stages 1–2 have just matched; fresh cold Stage 0 was not run. Windows follows Android acceptance.

---

# Current handoff — finish Iteration 30 page size classes

Start from [`ITERATION30_REPORT.md`](ITERATION30_REPORT.md), [`../experiments/android_dynamic_elf_wrapper.bf.notes.md`](../experiments/android_dynamic_elf_wrapper.bf.notes.md) and [`../evidence/iteration30_dynamic_elf.json`](../evidence/iteration30_dynamic_elf.json). The opt-in `bootstrap/run_android_extended.py --dynamic` uses a BF-native PIE writer for **up to 255 linear commands**. Adding `--loops` preserves 74-command BF-owned relocation. Do not claim dynamic ELF *file size* or unlimited loops yet: executable `p_filesz` varies but the 16 KiB aligned image is always 16,480 bytes. No Android-device retest, native Android BF compiler, or Windows backend.

Next: implement BF-owned extra page-class selection for sources 256+, with correct aligned RX/RW ELF offsets, tape initialization and startup address; expand bounded loop patching beyond 74 slots, then run Android loader tests. Regression commands: `python3 tests/verify_android_dynamic_elf.py`, `python3 tests/verify_android_extended_slots.py`, `python3 tests/verify_android_extended_loops.py`, `python3 tools/check_docs.py`. Linux `compiler/core.bf` remains **15,559 bytes**, **14,859 BF instructions**, **475,703-byte** executable, **zero fixed output padding**. Fresh Linux S1–S2 produced byte-identical hashes (not independent cold Stage 0). Windows follows Android S2 as before.

---

# Latest handoff — Iteration 29 bounded wide loop relocation

The next engineering gate is **dynamic Android ELF layout**, not bracket-word arithmetic. Start from [`ITERATION29_LOOP_FOLLOWUP.md`](ITERATION29_LOOP_FOLLOWUP.md), [`../experiments/android_wide_slot_patch.bf.notes.md`](../experiments/android_wide_slot_patch.bf.notes.md) and [`../evidence/iteration29_wide_slot_patch.json`](../evidence/iteration29_wide_slot_patch.json). The opt-in `bootstrap/run_android_extended.py --loops` pipeline now supports all eight BF commands in tested **up-to-74-command** image simulations and uses BF-native metadata, pairing, branch encoding, slot patching and fixed ELF creation. The new images are not device tested and the compiler is not Android native or self-hosted there. Linux native Stages 1 and 2 freshly reproduced the same executable, but cold Stage 0 was not rerun. The previous linear path remains the default.

Run `python3 tests/verify_android_extended_loops.py`, `python3 tests/verify_android_extended_slots.py`, `python3 tests/verify_source_comments.py`, and `python3 tools/check_docs.py`. Keep the canonical Linux BF compiler unchanged until a scoped change is justified. Prefer a separately tested BF-native dynamic ELF writer over adding to the 16,075-instruction slot emitter. Windows remains after Android native S2.

---

# Latest handoff — Iteration 29 partial

Start at [`ITERATION29_REPORT.md`](ITERATION29_REPORT.md), [`../evidence/iteration29_extended_slots.json`](../evidence/iteration29_extended_slots.json), [`../experiments/android_wide_slot_emitter.bf.notes.md`](../experiments/android_wide_slot_emitter.bf.notes.md) and [`../experiments/android_bounded_elf_wrapper.bf.notes.md`](../experiments/android_bounded_elf_wrapper.bf.notes.md). New 74-command linear Android ELFs are BF-generated and instruction-simulated; no loop relocations, dynamic ELF sizing, Android-native compiler, on-device execution or Windows progress. Next integrate bracket pair positions and branch records into runnable BF-generated images. Keep the previous ten-slot loop pipeline and Linux S2 stable. The source remains in standard BF, with small transport/test tools in Python only.

Run `python3 tests/verify_android_extended_slots.py`, `python3 tests/verify_source_comments.py`, and `python3 tools/check_docs.py` for the focused gates. Retain historical evidence rather than relabeling older device results as tests of the new image.

---

# Handoff — Iteration 28 BF bracket pairs proved, Android relocator still ten slots

## Do first

Read [`STATE.md`](STATE.md), [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md), and the complete [Android-first roadmap](IMPLEMENTATION_ROADMAP.md). Continue **Android before Windows**. Do not begin by writing C/Rust/Java output or an additional Brainfuck syntax. Compiler logic, parsing, codegen, linker/layout and optimization remain entirely standard `.bf`.

**Planned baseline:** 14 Android iterations (26–39), 6 Windows (40–45), 2 release iterations (46–47) = **22**. Reserve 28–34 total with rework. An iteration is complete only after its exit tests pass; the count is a forecast, not recorded progress.

## Verified base to protect

The canonical Linux compiler `compiler/core.bf` has **15,559 raw bytes**, **14,859 executable instructions**, generates a 475,703-byte static x86-64 ELF and passes archived three-stage native S2 equivalence. Its BF-owned source compaction has a 16,128-executable-command ceiling and 255 nesting levels; emitted ELF has **zero fixed padding bytes**. Its interpreter seeds are C *BF execution only*; the native machine-code emitter belongs to `.bf`. Re-run `sh tools/verify_release.sh` for executable changes.

The Android experimental six-stage BF pipeline plus two BF-only optimization stages now emits *ten-command-bounded* native AArch64 shell executables; archived evidence records execution on Pixel 8 Pro Android 17/API 37. The optional optimized transfer demo improved against its old BF implementation, but it did **not statistically prove superiority to the strongest direct-echo C baseline**. Crucially, the **compiler does not run or self-host on Android**. Windows PE32+ is absent. Consult [`ANDROID_NATIVE_OPTIMIZATION.md`](ANDROID_NATIVE_OPTIMIZATION.md), [`TARGETS.md`](TARGETS.md) and [`../status/CONFORMANCE_MATRIX.json`](../status/CONFORMANCE_MATRIX.json).

## Iteration 27: delivered and remaining

- **Delivered:** `experiments/android_source_scan.bf`, 1,170 standard BF instructions with a 24-bit emitted-command counter. Linux native BF compiled scanner executed 37 fixtures through 300,001 commands; six seed cross-checks, six malformed transport rejections and instrumented 24-bit overflow all passed. See [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json).
- **Integrated without changing legacy behavior:** `bootstrap/run_android_loops.py --scanner` optionally passes the scanner output to existing BF downstream stages. Nine bounded AArch64 images matched byte-for-byte, four invalid cases rejected identically and atomic output placement survived rejection. See [`../evidence/iteration27_scan_integration.json`](../evidence/iteration27_scan_integration.json).
- **Still missing:** this does **not** finish Iteration 27's large source compilation gate. The bracket/relocation/ELF pipeline remains **ten-command bounded**. Begin with BF-owned multi-byte bracket indexing and per-command relocation records, then generalize output emission without foreign patching. 300,000-command actual Android ELF creation is untested.
- **Regression gates:** unchanged canonical Linux `compiler/core.bf` and native compiler hashes are recorded in new evidence. Re-run source comments, bounded Android pipeline, documentation checker, Linux semantic correctness and native self-hosting as available. Historical Android-device execution is not a current retest.

Run now:

```sh
python3 tests/verify_android_source_scan.py
python3 tests/verify_android_source_scan_integration.py
python3 tests/verify_android_contract_v1.py
python3 tools/check_docs.py
```

## Iteration 28: completed substage and blocker

- **Delivered:** 2,524-command BF bracket metadata and 1,707-command BF stack matcher, each compiled to Linux ELF by the verified BF compiler. Together they emit 24-bit opening/closing bracket positions without Python relocation logic. See [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md) and [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json).
- **Executed:** 421 valid differential cases, 123 rejected invalid cases, 16 independent seed comparisons, nesting at 255 and 256, and source offsets through 300,002. The opt-in `--scanner --wide-brackets` pipeline retained eight identical old Android ten-slot outputs.
- **Still blocked:** the old `encode`, `emit`, and `apply` BF stages use one-byte span records and a fixed 4,192-byte image. **Implement BF-owned long-range branch encoding and dynamic image emission.** No changes to the canonical Linux compiler source or ELF were made; a fresh native Stage 1→2 recompile was byte-identical at both stages. Independent cold Stage 0 was not rerun (see [`../evidence/iteration28_linux_native_replay.json`](../evidence/iteration28_linux_native_replay.json)).

```sh
python3 tests/verify_android_wide_brackets.py
python3 tests/verify_android_source_scan_integration.py
python3 tools/check_docs.py
```

## Safety and acceptance invariants

- Standard eight-instruction V0: 8-bit modulo wrapping, zero-initialized fixed 65,536-cell tape, EOF-zero, no host-memory escape, exact loop semantics.
- A multi-pass source transport may only carry/replay bytes at the BF compiler's request; external scripts may not supply hidden BF-specific semantic decisions.
- Confirm both generated-program behavior **and** native compiler self-compilation on target; generated ELF execution alone is insufficient.
- Maintain comment-safe `.bf` source and source-offset notes; read [`STYLE.md`](STYLE.md) before editing prose.
- Retain the conditional nature of scratch-cell proofs and make no blanket formal memory-safety claim from finite tests.
- Record measurements with actual hardware/environment, repetitions, and uncertainty. Current sample has `NOT_PROVEN_FASTEST`, not universal C/Rust superiority.
- Do not replace [`../evidence/selfhost.json`](../evidence/selfhost.json) or historical target artifacts with guessed values. Evidence records past runs.

## Documentation and test tools

```sh
python3 tools/check_docs.py
python3 tests/verify_source_comments.py
python3 tests/verify_android_aarch64_loops.py
sh tools/verify_release.sh
```

The first two are local document/source checks; the latter two need their original execution dependencies. An unavailable device, toolchain or host ABI must be listed as a blocker. This D0 handoff does not assert that any new Android or Windows execution gate ran.

## Latest follow-up — first BF long-branch record stage

Added [`../experiments/android_wide_branch_encoding.bf`](../experiments/android_wide_branch_encoding.bf) (13,985 pure BF commands, 447,735-byte Linux native ELF). It consumes seven-byte BF bracket pairs and outputs 15-byte records with two encoded `B` words; tested through 300,000 source commands. See [`../evidence/iteration28_wide_branch_encoding.json`](../evidence/iteration28_wide_branch_encoding.json). Run `python3 tests/verify_android_wide_branch_encoding.py` and `python3 bootstrap/run_android_loops.py /tmp/android_tiny.bf /tmp/test.elf --scanner --wide-branches`. The latter **still emits the old ten-slot Android image**, not a veneer-enabled wide ELF.

**Next step:** implement an actual BF-native dynamic Android AArch64 ELF emitter/patcher consuming 15-byte wide records, place `LDRB` plus inverted conditional plus encoded unconditional `B` in each appropriate slot, update file/segment lengths and relocations, then independently inspect and execute the output. The prior older wide-bracket regression rerun timed out during this follow-up; record that gate as inconclusive, not green. Windows stays deferred.

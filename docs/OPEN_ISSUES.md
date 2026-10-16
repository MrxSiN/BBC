# Iteration 65 — Android callable remaining blockers

Disk backed duplicate patch tracking removed one host memory growth point in the active dynamic callable compiler. It does **not** resolve actual Android loading, ART/JNI, installed APK execution, original app policy parity, eight unavailable original policy sources or Android native dynamic self hosting. The fallback compiler lanes stay until those acceptance gates execute. [Current evidence](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 57 — active blockers, dynamic callable only

The new standard-BF six-command callable AArch64 compiler accepts growing sources and emits checked 64-bit ELF sizes without the old IR record table. **Brackets still reject**: connect BF-owned dynamically indexed bracket matching and loop relocation before calling the compiler universal. Android JNI/DSO device parity and remaining original Twitter/Threads policies are unverified. The old numeric 100M goal is retired, and older bounded/freestanding lanes remain temporary regression fallbacks. [Active roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

---

# Iteration 56 remaining Android compatibility gates

The original TwitterHideAds `action.bf` compiles via opt-in Brainfuck canonical clear-loop folding, but the **4,096-record IR tape ceiling remains** and other Twitter and Threads programs exceed it. The 15,300-byte Twitter callable image has not run on Android or within the original module's JNI bridge. No 100M native compiler evidence has been produced. See [Iteration 56 technical contract](ITERATION56_TWITTER_ACTION_CLEAR.md).

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

## Priority blocker — 100M native code generation

The new BF source analyzer handles 100M logical commands through raw-byte RLE, but the fixed-slot Android emitter, bounded bracket matcher and ELF writer still cannot compile any of the eleven pinned application policy files. Replace that full path with compact streaming BF-owned IR, paired loop relocation, a loadable AArch64 linker and correct Android runtime/host interfaces. Performance across noncompressible 100M-unit inputs is unmeasured.

---

**P0 / Iteration 46 (OPEN):** Real app compatibility replaces arbitrary command-ceiling increases as the principal Android roadmap test. All 11 Gmail/Twitter/Threads policies currently exceed the 2,719-command backend limit and the separate 16,128-command Android native-compiler input limit. No native BF-produced JNI `.so` or rebuilt app APK has been accepted. See [Android acceptance](ANDROID_APPLICATION_ACCEPTANCE.md).

---

# Iteration 45 Android release blockers

- **Target loader:** 2,719-command new-class images have Linux-hosted simulation only, not new Android device execution.
- **Capacity:** 300,000-command target is still open; current native-image path is bounded by two-byte indexing, tape stack capacity, slot-table size and ELF `ADRP`/length carry handling.
- **Native compiler:** the Android-native S2 artifacts remain bounded to their earlier 16,128-command source input profile; do not infer 300,000-command self-hosting.
- **Portability:** Android shell ELF PIE is not an APK, callable JNI library, other ABI, or generally deployable app.
- **Windows:** PE generation has Linux CPU-shim tests only; actual Windows loader execution and native Windows S2 remain open.

See [Iteration 45 evidence](../evidence/iteration45_android_class8.json) and [report](ITERATION45_ANDROID_REPORT.md). Earlier issues follow historically.

---

# Iteration 44 open gates — Windows loader and self-hosting

The new PE192 emitter has **Linux CPU shim** evidence only. Run `build/windows44_acceptance/verify_windows44.ps1` on a real Windows x64 environment and retain its JSON result; verify binary I/O, EOF, traps, imports and loader compatibility. Source indexing is still one-byte and capped at 192, not general PE compilation. Next implement a BF-owned multi-byte index and section/layout growth, then Windows-native BF compiler execution and self-hosting. Android 300,000-command qualification also remains open. [Evidence](../evidence/iteration44_windows_full192.json).

---

# Iteration 43 open gates — Windows loader, scalable compiler and native S2

Linux-shim execution verified the new 128-command BF-owned Windows PE32+ output. **Actual Windows x64 loader + KERNEL32 behavior is unverified**: execute `build/windows43_acceptance/verify_windows43.ps1` on Windows and retain its JSON output. Future work must extend the BF record/index contract beyond one-byte slot positions, implement general PE binary growth, compile the BF compiler itself into Windows-native PE and repeat self-compilation on Windows. Keep the separate Android 300,000-command goal open. See [new contract](WINDOWS_FULL128_PE.md), [report](ITERATION43_REPORT.md) and [evidence](../evidence/iteration43_windows_full128.json).

---

# Iteration 42 open gates — Windows loader and scalable compiler

A [test-only x64 native-execution harness](WINDOWS_LINUX_CPU_EXECUTION.md) verifies 164 programs plus all 11 earlier smoke files on the **Linux** CPU with Win32 import shims. The Windows loader, actual KERNEL32, Windows ASLR/PE compatibility, target-native compiler execution and Windows S2 have **not** been tested. BF-owned PE layout and branch relocation are still bounded to 64 commands. Android's independent 300,000-command objective remains unmet. Do not classify the shim as Windows target execution. [Evidence](../evidence/iteration42_windows_x64_cpu_shim.json).

---

# Iteration 41 open gates — Windows full BF syntax, not Windows execution

The Windows experimental BF-native image path now supports all eight standard instructions with tested loop relocation, limited to **64 executable commands**. Remaining: (1) run the prepared PE bundle under the real Windows x64 loader; (2) validate Win32 redirected byte I/O, EOF, native trap outcomes and ASLR/loader compatibility; (3) expand PE and BF source capacity; (4) execute the compiler itself on Windows and demonstrate native multi-stage S2. Linux S2 is maintained. Android bounded S2 is audited but the separate 300,000-command target remains unfulfilled. See [Iteration 41 report](ITERATION41_REPORT.md) and [target contract](WINDOWS_FULL64_PE.md).

---

# Iteration 40 checkpoint — Windows six-instruction linear PE backend

The new [Windows linear I/O backend](WINDOWS_LINEAR_IO_PE.md) generates BF-owned PE32+ images for `+ - > < . ,` from at most 64 executable commands, with imported Win32 byte I/O and deterministic x64 pointer traps. Its BF source, native Linux writer and static image tests pass; **no Windows loader/API execution** was performed. `[` and `]`, Windows-native compiler execution/S2, and Android's separate 300,000-command acceptance target remain outstanding. See [iteration report](ITERATION40_REPORT.md) and [evidence](../evidence/iteration40_windows_linear_io.json). Historical notes follow below.

---

# Current blockers after Android native S2 audit

Archived Android-native S2 is recorded and offline-audited; the outstanding Android blockers are the **300,000-command capacity target**, further devices and API levels, callable JNI/APK ABI, and complete optimizer/memory-safety proof. [Evidence](ANDROID_NATIVE_S2_AUDIT.md). Windows has only a **structural PE32+ fixed exit image**, not an executed binary and not a Brainfuck compiler. Required next gates are Windows loader execution, BF-owned parser/x64 generation, standard-handle I/O, nested-loop relocation and Windows-native S2. [Windows seed](WINDOWS_PE32_SEED.md).

---

# Current blockers after USB testing — 2026-10-13

The expanded generated-program loader gate is now **passed on Pixel 8 Pro**, with 13/13 fixtures through 2,000 commands. Android-native compiler execution/S2, general larger-source code layout and callable BF-native APK/JNI integration are still open. The native transfer workload did not beat the fastest C baseline; the existing GM BF-to-C/JNI policies remain slower than warmed Java. Native process startup does not explain steady-state APK performance. Component profiling is needed before attributing request/JNI/runtime costs or choosing an optimization. Other devices, 16 KiB-page hardware and same-device HotSpot JVM remain untested. See [report](ANDROID_DEVICE_FOLLOWUP_20261013.md); previous issue notes below are historical.

---

# Iteration 37 active blockers

The new Android acceptance [bundle and device instructions](ANDROID_DEVICE_ACCEPTANCE.md) cannot pass the device gate without a real arm64 Android shell target and `adb`. The 2,000-command BF AArch64 emitter has not been extended further; general slot tables/ELF lengths and native Android compiler bootstrap remain open. After device execution is evidenced, progress to Android-native self-hosting before Windows PE32+. No claims of new device support are warranted from the offline suite. Historical issue log follows.

---

# Iteration 35 active handoff

The previously fixed `0x10000` tape collision is **resolved only within the six-class, 2,000-command linear / 1,024-command loop path** by a new BF tape rebase. Beyond these bounds, dynamic relocation carries, general source-size support and larger loop tables are open. Android loader/device testing, Android-native compiler and self-hosting, the 300,000-command goal and Windows PE32+ are still outstanding. The older Iteration 34 randomized replay did not finish in this run. See [Iteration 35](ITERATION35_REPORT.md).
---

# Current blockers — Iteration 34

BF-generated AArch64 ELF output now reaches **1,024** commands, including loops, in four aligned ELF size classes with Linux-hosted simulation only. The leading technical blocker is the fixed RW tape segment at virtual address `0x10000`: scaling RX code beyond 1,354 commands would overlap it. Required work is BF-owned tape relocation, startup fixes, larger executable layouts, Android loader/device testing, Android-native compiler execution and full self-hosting. The independent BF seed validation of the new relayout stage is inconclusive due to a 75-million-step interpreter limit. Windows PE32+ remains deferred. See the [Iteration 34 report](ITERATION34_REPORT.md) and [evidence](../evidence/iteration34_multiclass_elf.json). Prior issue notes below are historical.

---

# Open blockers after Iteration 33

**RESOLVED for the bounded path:** BF-owned loop relocation now handles 512 commands, including loop branches across the 330→331 ELF page-class boundary. **OPEN:** scalable ELF RX/RW layout beyond two alignment classes, general source-size and branch-offset representation, real Android loader and device execution of newly generated images, target-native compiler execution/self-hosting, compiler hardening, then Windows PE32+. Untrusted direct BF patch records remain outside the current trusted-stage contract. See [Iteration 33](ITERATION33_REPORT.md). Older open-issue records below are historical.

---

# Iteration 32 open engineering gates

- **Multi-byte Brainfuck slot patching:** The 255-slot relocation table is now implemented and tested. The next gate is at least 512 slots with multi-byte positions and branch relocation across the **330→331** ELF size-class transition. The 300,000-command objective remains distant.
- **Native target execution:** The newest Android AArch64 images were tested only in Linux-hosted instruction simulation; no device loader acceptance was executed.
- **Source and transport trust:** Current BF patch stages rely on upstream validated records; arbitrary standalone corrupted frames are not accepted as a supported API. General native compiler input and streaming output are unfinished.
- **Android native compiler/self-hosting:** Not implemented. Full Android source-to-native-to-self compilation remains the primary release gate.
- **Windows:** PE32+ backend work begins only after Android-native S2, per the agreed roadmap.

See [Iteration 32 report](ITERATION32_REPORT.md) and [new patch notes](../experiments/android_wide_slot_patch_255.bf.notes.md).

---

# Iteration 31 open gates

- **BF-owned loop relocation beyond 74 commands:** The new two-class ELF writer accepts 512 linear commands, but the separate patcher cannot yet relocate brackets in 75–512 command sources. This is the next code-change priority.
- **Further aligned ELF classes:** BF header/padding arithmetic works for 0–512 commands in two file classes. General source sizes and RW virtual placement beyond this range are unimplemented.
- **Native Android execution and self-hosting:** Neither the new AArch64 files nor an Android-native compiler were executed on an Android loader during this iteration. Historical ten-command device evidence does not apply to these images.
- **Robust untrusted slot framing:** The BF writer requires a correctly framed count and byte stream; the host adapter validates transport. The isolated writer does not detect truncated raw slot streams under EOF-zero semantics.
- **Windows:** No PE32+ backend has been implemented.

Evidence: [`ITERATION31_REPORT.md`](ITERATION31_REPORT.md) and [`../evidence/iteration31_page_class_elf.json`](../evidence/iteration31_page_class_elf.json).

---

# Iteration 30 open gate — file size classes and larger loops

**PARTIALLY RESOLVED:** The first BF-native dynamic RX-length PIE stage supports 0..255 linear commands and uses correct 16 KiB-aligned RX/RW loads, but the image occupies a fixed 16,480 bytes until crossing its next alignment boundary. **OPEN:** BF-owned general page-class selection for 256+ sources, startup ADRP relocation, more than 74 loop relocations, Android device loader verification, native Android compiler execution/self-hosting, and Windows. Keep raw BF source size constraints and V0 safety invariant. See [`ITERATION30_REPORT.md`](ITERATION30_REPORT.md).

---

# Current unresolved gate after Iteration 29 wide patch

BF-owned AArch64 branch relocation into **bounded 74-slot ELF images** is now Linux-EXECUTED and instruction-simulated. The next P0 gate is **dynamically sized ELF PIE emission, strict relocation input validation, actual Android execution and eventual Android compiler S2**. The earlier ten-slot and linear-only blocker descriptions below are historical. New evidence: [`../evidence/iteration29_wide_slot_patch.json`](../evidence/iteration29_wide_slot_patch.json).

---

# Open issues — prioritized for Android first (2026-10-13)

This file lists current blockers. Historical experiments and resolved issues remain in their own reports. See [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md) for the proposed iteration order and [`STATE.md`](STATE.md) for what has actually executed.

1. **P0 — Android source capacity (PARTIAL SCANNER AND 74 SLOT LINEAR CODEGEN):** The old loop-capable generator accepts **ten commands**; the new linear-only BF-generated ELF accepts **74 commands**, not arbitrary valid BF. The Linux authoritative BF compiler accepts 16,128, while all eleven audited Android policy BF sources have 18,192–296,307 instructions. BF-owned scalable or repeated-pass input, indexing, multi-byte counters, bounded tape ownership and deterministic overflow handling are required. Proposed gate: *at least 300,000 commands*, not currently supported. Iteration 26 froze the transport contract. Iteration 27 added a BF-only 24-bit streaming scanner, executing 300,001-command input tests on Linux and matching nine ten-slot ELF output images through the opt-in adapter. **That scanner alone did not increase code generation; Iteration 29 subsequently added a 74-command linear ELF stage.** Wide bracket indexing and matching arrived in Iteration 28, but their general AArch64 relocation consumer and dynamic ELF emission remain missing. Planned Iterations **28, 29, 36**.
2. **P0 — General Android AArch64 relocations and layout (PARTIAL):** The successful ten-command loop pipeline uses fixed small branch slots, byte transport and a limited ELF image. Source-wide jumps, long-distance conditional branches, image/file sizes, PI relocation, ASLR and loader tests must be BF-owned. Planned **28–30**.
3. **P0 — Full target semantics and environment (PARTIAL):** All eight operations work within bounded prototype tests, including real Android nested loops and boundary traps, but robust native error handling (`EINTR`, `EAGAIN` policy), redirected raw streams, large loops, API/loader matrix, memory layout and trusted input framing are not general. Planned **31, 35, 37**.
4. **P0 — Android-native compiler and S2 self-hosting (UNIMPLEMENTED):** Linux-hosted BF stages emitting Android ELF do not constitute an **Android-hosted native BF compiler**. Build it, execute it on Android, have it compile its entire authoritative BF source twice, and compare independent programs/hashes. Planned **32–34**.
5. **P0 — Maintain Linux correctness/self-hosting (EXECUTED, MUST REGRESS):** Linux source is **15,559 raw bytes**, **14,859 BF instructions**, ELF 475,703 bytes, zero fixed trailing padding, exact Stages 0–2. Shared backend changes must not regress this. Full compiler-tape ownership proof is still open; header cell 61 has a conditional proof only.
6. **P1 — Windows x86-64 PE32+ (UNIMPLEMENTED):** No Windows native emitter, compiled BF executables or Windows BF compiler. Requires PE headers/imports/relocations, Microsoft x64 ABI, Win32 standard-handle I/O and native self-hosting. Independent Windows C interpreter seeds in old Android tests do *not* count. Planned **40–45**, after Android acceptance.
7. **P1 — Real Android policy workload compatibility (UNVERIFIED):** Gmail/Twitter/Threads BF policies require source capacity and framed call ABI/host integration. G29 requires a distinct signed 32-bit checked-cell execution profile and Windows HID/DirectInput host. APK and host API support are separate from a shell ELF compiler. See [`TARGET_WORKLOADS.md`](TARGET_WORKLOADS.md).
8. **P1 — Compiler safety and reproducibility (PARTIAL):** Known bounded Linux tests and Android simulation/native subsets are useful, but not proof for arbitrary malformed input, compiler scratch overlap, adversarial relocation, resource exhaustion or bootstrap trust. No unvalidated check elimination. Planned **35, 46–47**.
9. **P2 — Measured performance (MEASURED ONLY ON SMALL CASES):** Archived optimized Android transfer median 2.3514 ms versus direct-echo C 2.3532 ms with confidence interval including loss. **NOT_PROVEN_FASTEST**. Linux stress benchmark 12.93x slower than optimized C. Full-size workloads, whole application parity and general C/Rust competitiveness remain open. Planned **38, 45**.
10. **P2 — Optional ecosystems (OUT OF BASELINE):** Android `armeabi-v7a`, x86 and x86_64, packaging/Play Store, other Windows architectures, bare-metal and GPU/hardware services require separate verified support. No ninth BF instruction or hidden external codegen.

**Resolved historical blocker:** In Iteration 19 the BF decoder began discarding ignored characters in-core and emitting exact Linux ELF file sizes; the old 524,280 trailing file bytes were eliminated. Do not reopen that as an unimplemented task. Similarly, the initial Android absence of bracket machine-code generation was resolved *for ten commands* in Iteration 25, and later Android native execution was recorded on a real device. Neither resolves general-source codegen or Android-native compiler self-hosting.

## Iteration 28 follow-up

BF-native wide bracket *matching* is now executed on Linux: [results](ITERATION28_REPORT.md). The P0 blocker remains BF-owned AArch64 long-range branch encoding, dynamic ELF layout, and large native image execution. The bracket-pair stage trusts records from the upstream BF stage rather than independently validating hostile metadata. The ten-command emitter remains unchanged.

## Wide branch record follow-up

The raw AArch64 branch word calculation portion of P0 issue 2 is now **Linux executed in standard BF**; the BF-owned wide relocation consumer and dynamically sized ELF emission remain **UNIMPLEMENTED**. A separate BF-native 74-slot **fixed** ELF linear wrapper was executed in Iteration 29. The conservative supported separation is **2,796,201 source positions** with explicit range rejection. New details are in [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md). Do not call the entire relocation/layout blocker resolved.

## Iteration 29 partial resolution

BF-only 48-byte AArch64 slots and a bounded 74-slot fixed PIE wrapper are **EXECUTED on Linux**, with independent AArch64 instruction simulation of 85 linear sources across two load biases. The adapter rejects bracketed sources rather than run unpatched `B` placeholders; this is not full loop-capable compilation or dynamic image sizing. The next unresolved P0 blocker is **applying BF wide branch records into ELF**, followed by scalable ELF layout. See [`ITERATION29_REPORT.md`](ITERATION29_REPORT.md).

**Source-capacity note:** The new BF slot emitter contains 16,075 instructions, only **53 below** the Linux compiler's 16,128-command source ceiling. Growing the same source file is not a sustainable route to native relocation and dynamic layout. Split independently BF-executable stages or raise the canonical self-hosted compiler's verified source limits without introducing a foreign code generator.

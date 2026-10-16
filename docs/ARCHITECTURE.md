# Iteration 65 — Callable relocation storage contract

The active BF authored AArch64 callable pipeline now stores duplicate patch marks in a sparse temporary file using one bit per native word. BF stages retain all compiler arithmetic and emission decisions; Python only materializes BF supplied indices into files. This change removes a Python heap set proportional to the number of loop pairs. [Report](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Iteration 57 — active resource-scaled callable architecture

Source is transported as opaque `(present, byte)` records to a **standard-BF** streaming callable code emitter; BF produces AArch64 instruction bytes and BF computes the checked ELF header length with unsigned 64-bit carry. The file adapter only frames, stores and commits output. The new lane handles six linear operators with explicit pointer bounds checks, byte I/O and callable `BFP1` ABI. It does **not** yet handle brackets or shared-library exports. The old bounded IR resolver and prior scalable *freestanding* ELF path are temporary fallback references. The active objective is fully dynamic callable compilation **without** a synthetic 100M ceiling. [Code and evidence](ITERATION57_DYNAMIC_CALLABLE_LINEAR.md); [active roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).

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

# Latest target architecture checkpoint

## Iteration 49 — dynamic capacity principle

The new [Brainfuck streaming slot stage](../experiments/android_streaming_linear_slots.bf.notes.md) emits linear native AArch64 slots without allocating a fixed source table or encoding a source command count. The host has optional resource quotas; physical memory, storage, address reach and CPU time always remain finite. This is not a general ELF backend, loop-capable native codegen, shared library or APK toolchain. The separately verified 100M source scanner and 32-bit loop pairer do not yet feed general native relocation. [Evidence](../evidence/iteration49_android_dynamic_stream.json).


## Current experimental source frontend

The Iteration 48 standard-BF stages produce matched unsigned 32-bit source offsets across 100 million commands. They run on Linux and communicate through a framed generic byte transport. This is a source-analysis pipeline; no source-to-native instruction address layout or Android DSO emitter is connected yet. See [source and pairing contract](ANDROID_100M_CAPACITY.md) and [machine evidence](../evidence/iteration48_android_100m_pairing.json).

---

## 100M source stage is not a compiler backend

The new [32-bit BF stage](ANDROID_100M_CAPACITY.md) receives generic losslessly compressed raw bytes and performs command filtering, bracket-depth checks and 32-bit event-position emission inside Brainfuck. It does not store 100M source commands on the compiler tape. There is no 100M bracket pairing, executable emission, Android ET_DYN or JNI ABI support yet.

---

The canonical Linux compiler remains a 15,559-byte standard-BF implementation. A separate 14,575-instruction Android compiler source now has [archived native S2 evidence](ANDROID_NATIVE_S2_AUDIT.md) on one arm64 Android device; it is not yet a general 300,000-command Android compiler. The Windows path is starting from a fixed [PE32+ BF byte emitter](WINDOWS_PE32_SEED.md); it is not yet a code-generating compiler. Existing shared BF semantics remain normative.

---

# Architecture update — Iteration 33 two-byte BF relocation

The optional BF AArch64 pipeline now uses a third relocation stage for 256–512-command `--page-class --loops` sources, in addition to the 74 and 255 command paths. The new [BF program](../experiments/android_wide_slot_patch_512.bf) walks a 12-cell-per-slot tape table with a **two-byte position** and borrows; it consumes BF-owned bracket/branch-word records and emits patched AArch64 slots. The BF-owned page-class writer produces aligned 16,480/32,864-byte PIE images across the 330→331 boundary. Host Python only carries/checks byte frames and places finished output; it does not patch branches. Native Linux stage + simulated AArch64 evidence is available in [Iteration 33](ITERATION33_REPORT.md). Larger page classes, Android loader execution, Android-native S2 and Windows PE32+ remain unsupported. Earlier architecture sections below are historical.

---

# Architecture update — Iteration 32 loop patcher capacity

The opt-in Android pipeline now chooses between two **Brainfuck-native** relocation stages: the original 74-slot table for the fixed 4,192-byte writer, and a new 255-slot table for the `--dynamic` or `--page-class` writers. The upstream 24-bit matching and 26-bit AArch64 branch encoder remain BF-owned. The new patcher still has a one-byte slot index/count contract, so programs containing loops above 255 commands are rejected, even though 512-command **linear** ELF images work. The Python adapter performs framing, provenance checks and file placement, not native instruction synthesis. See [Iteration 32](ITERATION32_REPORT.md).

---

# Iteration 30 architecture addition — BF ELF file layout stage

The optional AArch64 pipeline now isolates a **9,087-BF-instruction ELF construction stage** from the 16,075-BF-instruction machine slot encoder and the existing BF-owned wide loop patcher. The BF wrapper takes a single byte command count and 48 machine bytes per instruction, computes the RX load length inside BF, emits the code and exit sequence, fills a 16 KiB alignment gap and writes the RW dynamic entries. `bootstrap/run_android_extended.py --dynamic` handles only transport, length checks, provenance and atomic file placement. Current 255-linear/74-loop bound and 16,480-byte file class: [source notes](../experiments/android_dynamic_elf_wrapper.bf.notes.md) and [tests](../tests/verify_android_dynamic_elf.py).

---

# Architecture

**Current-state note (2026-10-13):** The architecture below describes the **authoritative Linux** compiler and historical Android components. Later BF-only Android stages have produced bounded **ten-command native programs executed on Pixel 8 Pro**. There is **still no Android-hosted self-compiling compiler** and **no Windows PE32+ emitter**. The [scoped acceptance contract](PLATFORM_ACCEPTANCE.md) and [22-iteration plan](IMPLEMENTATION_ROADMAP.md) define what must be built next. Sections labeled Iteration 21–23 are historical and their pre-device "not tested on Android" statements must not be read as current overall target status.

**One canonical Brainfuck compiler. One byte stream in, native ELF out.**

`compiler/core.bf` owns input decoding, validation, source buffering, exact file-size arithmetic, bracket resolution, fixed-slot native emission and error status. The tools around it don't generate machine code.

```text
byte-stuffed stdin
  -> BF decoder and bounded four-cell-per-command buffer
  -> BF byte-count scan and three-byte ELF file-size accumulator
  -> ELF64 headers with calculated p_filesz
  -> 32-byte native slots and branch relocations
  -> x86-64 exit, then one compiler status byte
```

Maximum source: **16,128 executable commands** and **255** loop levels. Every retained command occupies four BF compiler-tape cells. Noncommand bytes are discarded. The compiler's own annotated source is **15,559** bytes with **14,859** BF commands and **1,269** spare command records for self-compilation.

Safe source annotations are ignored by the native compiler during input filtering; they no longer generate NOP slots.

## Native ELF

Linux x86-64 ELF64, static, no libc or BF VM. RX `PT_LOAD`: base `0x400000`, maximum mapped size **524,288** bytes, *file size* calculated as **`215 + 32 * filtered_command_count`**. RW `PT_LOAD`: base `0x600000`, **65,536** zeroed tape bytes. Startup entry: `0x4000b0`; first source slot offset: 206. The Linux loader zero-fills RX bytes beyond `p_filesz`; the compiler no longer emits any of the previous **524,280** fixed trailing zeros.

All eight BF operations lower to machine instructions in 32-byte slots. Ignored source characters are discarded inside the BF decoder before code emission. The bracket matcher calculates signed relative x86-64 displacements based on those slots. Bad pointer moves trap with `exit(2)` before memory escapes the tape.

Startup sets `r12`/`r13` to the tape base, computes `r14` as its end, and sets `rdx = 1` for byte I/O. `read` and `write` retry `EINTR`, report other unsuccessful returns with exit(4)/(3), and fail fast on `EAGAIN`.

The exact count is computed *before* the ELF header is written, by walking retained command records with a 24-bit size accumulator. The decoder discards escaped `00` and `FF` because neither is a BF instruction. The code emitter also temporarily reuses source-byte cells and restores them. The compiler saves and restores its pending input-error bit because the same tape neighborhood is used for temporary header arithmetic. That restore is necessary to reject malformed/oversized compilation input. Source offsets are in `compiler/core.bf.notes.md`.

## External tools

`bootstrap/seed_interpreter*.c` only execute Brainfuck for cold bootstrap. `bootstrap/transport.py` stuffs bytes and checks the final compiler status. Python reference tests and ELF validators reject incorrect output; they do not alter it. `experiments/elf_file_size.bf` is a standalone 251-command arithmetic reference. `experiments/command_filter.bf` is an 862-command BF lexer, compiled to native ELF and tested separately. Neither is an authoritative compiler frontend or input language. The separate filter is not required because filtering is now wired into `core.bf`; see [`COMMAND_FILTER.md`](COMMAND_FILTER.md). Dynamic compiler-tape measurements and their limits are in [`COMPILER_TAPE_AUDIT.md`](COMPILER_TAPE_AUDIT.md).

The production Linux compiler has no optimizer or generic linker, garbage collector, JIT, additional native target, or bare-metal support. Describing one in a diagram would be considerably easier than writing it in Brainfuck. Not a valid substitute.

## Integrated compiler — Iteration 19

The tested decoder compactor from Iteration 18 is now authoritative. The initial source-capacity blocker was solved by replacing 39 large header-byte arithmetic runs with shorter pure-Brainfuck loops, saving 2,093 commands. The integrated source is **15,559 raw bytes** with **14,859 BF commands** and creates a **475,703-byte** native compiler ELF. Its native Stages 0–2 are byte-identical, and 91 independent native-output comparisons verify comment filtering. The former external streaming filter and adapter remain as historical/reference tools, not a mandatory compilation stage.

Header constant construction uses the zeroed compiler scratch cell 61 and restores it; the compiler-tape audit executes eight witnesses. This is not a universal nonoverlap proof.

See [`STATE.md`](STATE.md), [`SELF_HOSTING.md`](SELF_HOSTING.md), and [`DECODER_COMPACTION_PROTOTYPE.md`](DECODER_COMPACTION_PROTOTYPE.md) for current evidence and the historical prototype.

## Experimental Android backend

Iteration 21 introduced `experiments/android_aarch64_pie_subset.bf`, a second raw-Brainfuck code emitter for a three-operation straight-line source subset. It is compiled into a Linux-native Brainfuck executable using the existing self-hosted compiler. Its output is an AArch64 ELF PIE and not an x86-64 program. The host adapter writes complete artifacts only on a zero compiler status. It does not implement another parser or emitter. This module is not linked into `compiler/core.bf`; no Android native compiler exists yet. Details are in [the target prototype](ANDROID_AARCH64_PROTOTYPE.md).

## Android emitter prototype — Iteration 23

The separate Brainfuck-only AArch64 prototype has grown from three to six
commands by adding guarded pointer movement (`>` and `<`) and byte input (`,`). Its code generator
is still an ordinary `.bf` program compiled by the unchanged Linux S2
compiler. It builds a fixed 4,192-byte PIE with ten 48-byte command slots;
this prototype neither links into `core.bf` nor establishes Android execution
or Android self-hosting. See `ANDROID_AARCH64_PROTOTYPE.md`.

## BF-owned Android optimization — 2026-10-12

The six-stage loop pipeline now has two optional BF-only image stages:
`android_native_optimize.bf` folds six exact clear/adjacent transfer patterns
and removes PT_INTERP. `android_resource_optimize.bf` proves when a sixteen-byte
stack tape is sufficient, retains guards for other programs, specializes the
initial read/transfer, and skips trailing empty slots. Ten-command source and
4,192-byte output limits remain. Windows executes independent BF seeds locally;
Python transports bytes and checks provenance. Native generated code ran on
Pixel 8 Pro. [Proof conditions and measurements](ANDROID_NATIVE_OPTIMIZATION.md).

## Iteration 28 — BF-owned wide bracket pairing stages

The standalone BF-only parser [`../experiments/android_wide_bracket_metadata.bf`](../experiments/android_wide_bracket_metadata.bf) reads filtered instructions and produces 24-bit bracket indices with 8-bit depth. The second BF-only module [`../experiments/android_wide_bracket_pairs.bf`](../experiments/android_wide_bracket_pairs.bf) keeps a 255-entry five-cell tape stack and emits six-byte opening/closing offsets. Neither contains foreign parser logic. The optional `--wide-brackets` pipeline validates both stages before feeding the **unchanged ten-slot AArch64 branch builder**. The new positions cannot be encoded by that builder at general lengths yet. Details: [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md).

## Iteration 27 — experimental Android source scan stage

The new [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf) is standard BF, not a foreign front-end. It consumes the existing byte-stuffed transport stream and emits filtered commands, a 24-bit little-endian command count and a status byte. Counter cells live at 8–10, following the original filter's cells 0–6. See [`../experiments/android_source_scan.bf.notes.md`](../experiments/android_source_scan.bf.notes.md) for the full map and failure protocol. A Linux-native BF-generated executable processed 300,001 commands. The adapter's opt-in `--scanner` mode merely removes the BF-produced frame before feeding the **same ten-slot** Android BF stages. It does not add general bracket relocation, AArch64 layout or Android-native compiler execution. The canonical Linux self-hosted `compiler/core.bf` remains unchanged.

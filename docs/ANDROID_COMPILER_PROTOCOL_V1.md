# Android compiler protocol V1 — Iteration 26

**Decision state:** adopted engineering contract, **not an implemented scalable compiler**. This document freezes the interfaces against which Iterations 27–39 will be measured. It does not change ordinary Brainfuck or claim an Android-native compiler exists. Current executed coverage is the separate ten-command BF-owned pipeline; see [`STATE.md`](STATE.md).

## V0 program behavior stays fixed

Only `><+-.,[]` execute. All other source bytes are ignored, including binary NUL and FF. The generated program has 65,536 zeroed unsigned 8-bit cells, wrapping arithmetic, pointer zero at entry, deterministic out-of-tape traps, raw byte stdin/stdout and EOF→zero. Unmatched brackets fail compilation; they never become runnable partial output. See [`BRAINFUCK_SPEC.md`](BRAINFUCK_SPEC.md).

The first new product is an AArch64 (`arm64-v8a`) Android shell **ELF PIE**, with executable compiler and generated program on a documented device/API/loader. This is not a portable APK, an app host ABI, or the other Android ISAs. The loader compatibility demonstrated historically was **Pixel 8 Pro Android 17/API 37**, limited to ten commands. Do not infer a minimum supported API from that single device.

## Byte transport V1

Input is a byte stream, not a new BF dialect. The transport performs a strictly bytewise reversible transformation so physical EOF does not alias raw NUL. The BF compiler must perform *all* source filtering, bracket resolution and code generation.

| Raw source byte | Compiler stdin bytes |
|---|---|
| `00` | `FF 01` |
| `FF` | `FF 02` |
| every other byte | unchanged |
| physical EOF | stream terminates |

A lone `FF`, `FF 00`, `FF FF` or `FF` followed by any code other than `01` or `02` is malformed. The BF decoder rejects it. Escaped 00/FF decode to ignored non-instructions, **not** command terminators. This preserves the existing Linux source protocol. The caller may store/replay **opaque encoded bytes**, but may not count commands or match brackets. The compiler reads stdin and returns bytes on stdout. A caller may choose a file-based wrapper; the wrapper is not the parser or linker.

**Accepted compiler output:** exact artifact bytes followed by **one trailing status byte `00`**. Other final status bytes mean compilation failure and require discarding any earlier bytes; partial ELF prefixes are never installed. The last byte, not the first embedded zero, is the status. The caller atomically replaces the destination only after status acceptance and independent structural checks. An empty stdout stream is a failure. Normal artifact bytes may include 00 and FF without encoding. A standalone BF-native executable implements stdout emission; writing an output file is only transport/placement.

**Planned distinct failure categories** (not yet supported by the old six-stage pipeline): `01` malformed wire/source/brackets, `02` source command cap, `03` maximum nesting, `04` output/offset capacity, `05` unsupported target configuration, `06` invariant failure and `07` transport fault. These are compiler *result* codes, not runtime program exit statuses. The legacy pipeline promises only `00` success and **nonzero** rejection; do not interpret its error codes as V1 diagnostics yet. For generated programs, target exits 2 for a pointer trap; read and write failures remain separately specified by the eventual Android byte-I/O implementation.

No external script may: filter `><+-.,[]`, compute command offsets, resolve brackets, select native instructions, patch branch bytes, calculate ELF offsets/relocations or repair malformed output. A transport may copy, buffer, replay and atomically place byte streams; independent test code may parse for an oracle **only during testing**.

## Existing BF-only stages: audited boundary

Each of these is a **Brainfuck source** that runs as a Linux-native executable produced by the verified Linux BF compiler. The Python adapter sequences their **unchanged bytes**. The stage-local protocols are not yet a single public V1 protocol.

| BF stage | Source | Owner's job | Current bound / stored state |
|---|---|---|---|
| `filter` | `experiments/stream_filter.bf` | Decode/validate FF escapes and emit BF commands | Stream output; no whole-source storage claimed |
| `resolve` | `experiments/android_bracket_relocations.bf` | Nested bracket spans and closing positions | One-byte records; tape stack starting at cell 21; 10 commands |
| `encode` | `experiments/android_branch_encoding.bf` | Form AArch64 CBZ/CBNZ branch words from span records | One-byte offsets and ten-slot assumptions |
| `mask` | `experiments/android_branch_mask.bf` | Replace brackets with placeholder slots before emission | Source stream passed to ten-slot emitter |
| `emit` | `experiments/android_aarch64_pie_subset.bf` | Machine instructions, 4,192-byte PIE, tape and syscall slots | Exactly 10 × 48-byte slots; scratch cell 3 used during header work |
| `apply` | `experiments/android_branch_apply.bf` | Patch branch instruction words inside the BF-generated image | Single fixed 4,192-byte image; bounded slot indexing |
| `optimize` (optional) | `experiments/android_native_optimize.bf` | Recognize limited clear/transfer loops | Optimizes fixed ten-slot image only |
| `resources` (optional) | `experiments/android_resource_optimize.bf` | Remove proved-unneeded limited image work | Optimizes fixed ten-slot image only |

**Ownership limitation:** these local facts are based on the stage notes and executable behavior. A whole-pipeline proof of scratch-cell nonoverlap, all compiler tape accesses and arbitrary-depth source handling does **not** exist. See [`COMPILER_TAPE_AUDIT.md`](COMPILER_TAPE_AUDIT.md), [`ANDROID_AARCH64_PROTOTYPE.md`](ANDROID_AARCH64_PROTOTYPE.md), and [`../evidence/iteration26_contract.json`](../evidence/iteration26_contract.json).

### Current adapter-only restrictions

- `bootstrap/run_android_loops.py` bounds **raw** input at 1,048,576 bytes, not at 1,048,576 BF commands.
- The emitting pipeline enforces **at most 10 executable commands**, even if the input contains only comments after that point.
- Its result is a fixed **4,192-byte ELF** with trailing transport status `00` from the BF stage.
- The resolver emits `span, closing_position` as one-byte pairs, with `00 00` as end-of-records and status. Branch encoding and application use the old ten-slot format.
- The optional BF optimization stages still assume those ten fixed slots. They cannot be enabled automatically after general codegen without new proofs.
- Python process orchestration is allowed *for this experimental pipeline*. It does **not** establish an Android-native compiler or Android S2 self-hosting.

## Iteration 27 scanner subprotocol (experiment; V1 unchanged)

The independent BF scanner [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf) now emits filtered commands plus three little-endian count bytes and a final status byte. It uses BF tape cells 7–14 for marker, counter, zero-test scratch and carry-overflow sentinel. The scanner is a **tested wide input primitive** and can be selected with `--scanner` in the legacy ten-slot transport adapter. It does not add external BF parsing; the adapter only extracts the last four bytes and verifies the reported count matches the emitted stream length. Nine bounded Android image comparisons agreed with the legacy filter. Details in [`../experiments/android_source_scan.bf.notes.md`](../experiments/android_source_scan.bf.notes.md) and [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json). The Android codegen, relocation and PIE output path **remains fixed at ten commands**. Do not treat the scanner-only 300,001 command fixture as a compiled Android artifact.

## Iteration 28 wide bracket record subprotocol (experiment)

The BF-only [`../experiments/android_wide_bracket_metadata.bf`](../experiments/android_wide_bracket_metadata.bf) consumes only the filtered command bytes obtained from the scanner, not raw `FF`-escaped source. Each bracket yields five bytes: ASCII `5B`/`5D`, 24-bit one-based little-endian position and an 8-bit nesting depth. Successful balanced input ends in `00 00`. Failure ends in `00` plus an error status, and **partial prior records are invalid**. For the tested stage, malformed command/bracket is status `01`, index overflow `02`, and depth 256 `03`.

The BF-only [`../experiments/android_wide_bracket_pairs.bf`](../experiments/android_wide_bracket_pairs.bf) consumes those records **as trusted BF-stage output**, not as an independently authenticated hostile byte stream. It emits a seven-byte record for each closing bracket: `5D` followed by three little-endian bytes for the opening position and three for the closing position, then `00` plus final status. It uses an explicitly bounded BF tape stack at most 255 levels deep and does not rely on external pairing. The two BF modules are Linux-native stages and can be opted into the *old* pipeline with `--wide-brackets` (optionally `--scanner`). **They do not generate wide AArch64 branch displacements or patch a dynamic ELF.** The old ten-slot path still determines the executable bytes.

Details: [`ITERATION28_REPORT.md`](ITERATION28_REPORT.md). No Android-native compiler or self-hosting is claimed.

## Chosen source-capacity architecture for Iterations 27–36

**Decision:** a bounded **multi-pass BF-owned streaming compiler** rather than pretending its 65,536-byte BF tape can hold 300,000 commands or a 14.4 MiB native image. A byte transport can replay an immutable source/spool stream in BF-requested passes; BF source must own parsing, count/index arithmetic, bracket matching, relocation computation, ELF construction, layout and final emission. The final mature toolchain must support native Android compiler execution and recompile its own complete BF implementation. Host scripts cannot become a hidden compilation engine.

1. **Validation/count pass:** a BF module consumes escaped bytes, filters commands, checks the input envelope and nesting and computes bounded *multi-byte* command counters. Failure stops before artifact installation. Count must distinguish zero, maximum, and one-over-maximum exactly; it must never wrap silently. Repeated passes must see identical raw input (hash/check handled by transport), including binary comments.
2. **Relocation/layout passes:** BF-owned bracket analysis and exact instruction selection determine the entry/exit slots and all branch displacements. No one-byte spans or compiler tape-wide buffering of 300,000 records. Future stage boundaries may use opaque BF-emitted record/spool streams and repeated BF-owned traversal. A stream replay service may select **byte offsets requested by BF**, not compute BF command indices. Record formats are versioned and checksummed before implementation.
3. **ELF and code pass:** BF code constructs dynamic ELF64 program headers, machine words, tape layout, runtime I/O and fault paths. It emits bytes sequentially and calculates output size with sufficient-width arithmetic. The transport only places accepted bytes; no host linker or binary patcher is permitted.
4. **Self-hosting:** once the full compiler is constructed from standard BF, compile it into an Android-native compiler and execute repeated on-device compilation stages. A cross-compiled ELF running only as a generated program does not count.

The proposed acceptance limit is **at least 300,000 executable BF commands** plus a separately tested **255-deep** bracket limit. These are targets, not implementation claims. At 48 native slot bytes per command the *old* fixed-slot strategy would require **14,400,000 bytes** of code alone, far beyond the 65,536-cell compiler tape and 4,192-byte ELF. Thus any general solution must stream output or explicitly use a separately versioned compiler-memory profile. The codegen may change the per-command slot size but **must** still compute ELF sizes, offsets and branch displacements correctly. With 48-byte slots, the maximum signed AArch64 `CBZ/CBNZ imm19` branch range is approximately ±1 MiB, so far loops require a BF-owned long-branch strategy. No Python postpatching.

**Risk acknowledged:** repeated sequential passes without a BF-owned efficient relocation index can become quadratic in source length. The 300,000-command gate additionally requires recorded compilation time, memory use and worst-case loop cases; a source-limit check by itself is not acceptance. A BF-implemented index over an opaque external byte spool is a possible refinement, *not an implemented feature*. Do not assume a random-access service exists on standalone Android until its environment, control protocol and test evidence are explicit.

## Gate and verification

Use `python3 tests/verify_android_contract_v1.py` for stage hashes, source filtering, malformed encoding, existing bounded ELF compilation and atomic output. Its JSON record is [`../evidence/iteration26_contract.json`](../evidence/iteration26_contract.json). Run `sh tools/verify_release.sh` for full Linux regression; expensive gates and device-dependent gates are not silently passed if unavailable. Baseline Linux native Stage 1→2 equivalence is separate from *cold* interpreted Stage 0 verification.

The next actual compiler-code gate is **Iteration 27**, a BF-owned streaming source-capacity primitive tested at **16,128 commands**, its following boundary, and progressively larger fixtures. Do not claim the 300,000-command or on-device gate until native artifacts and executed evidence exist.

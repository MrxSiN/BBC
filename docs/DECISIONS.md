# Iteration 65 decision — Store patch occupancy on disk

Use sparse one bit per native word file backed occupancy for the active AArch64 signed 64 bit relocation adapter, rather than accumulating all word indices in a Python set. This keeps transport memory bounded for growing loop counts without changing authoritative BF codegen. [Verification](ITERATION65_DYNAMIC_RELOCATION_STORAGE.md).

---

# Iteration 58 — active callable compiler update

The new BF-owned AArch64 callable path now performs nested-loop compilation with file-backed pairing and signed-64-bit BF relocation, while retaining the eight-command semantics and documented BFP1 budget and pointer traps. Three original pinned local policy sources compiled; 59 source cases passed 354 independent AArch64 simulations. This does **not** establish Android JNI/DSO loading, device execution, all-eleven app acceptance, or Android self-hosting. The active objective is full resource-scaled callable compilation, **not a 100-million-command benchmark**. Old numbered targets in the historical entries below are no longer active. Bounded and freestanding paths are retained only as verification fallbacks until end-to-end Android parity succeeds. See [Iteration 58](ITERATION58_DYNAMIC_CALLABLE_LOOPS.md), [current roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md) and [evidence](../evidence/iteration58_dynamic_callable_loops.json).

---

# Decision — 2026-10-14 — retire synthetic size threshold

The prior numeric 100-million-command compilation objective is withdrawn. Compiler scalability is governed by representable 64-bit code addressing, ABI/ELF limits, resource pressure and executed workload tests, not a fixed instruction benchmark. Prior 100M scanner/pairing evidence stays historical. Dynamic **callable** compilation is the only active Android compiler development target; bounded callable and growing freestanding paths remain fallback references until a tested full replacement exists. [Current implementation](ITERATION57_DYNAMIC_CALLABLE_LINEAR.md).

---

# Decisions that matter

## Iteration 49 — dynamic capacity principle

The new [Brainfuck streaming slot stage](../experiments/android_streaming_linear_slots.bf.notes.md) emits linear native AArch64 slots without allocating a fixed source table or encoding a source command count. The host has optional resource quotas; physical memory, storage, address reach and CPU time always remain finite. This is not a general ELF backend, loop-capable native codegen, shared library or APK toolchain. The separately verified 100M source scanner and 32-bit loop pairer do not yet feed general native relocation. [Evidence](../evidence/iteration49_android_dynamic_stream.json).


## 2026-10-13 — aligned ELF loads instead of compact unaligned tape

The Iteration 30 BF-only AArch64 PIE writer preserves a separate non-executable tape `PT_LOAD` aligned to 16 KiB. The RX `p_filesz` changes as `0x220 + 48 * n`, with `0..255` linear commands, but the file itself stays 16,480 bytes until a future page-class transition. This is intentional: moving the RW load immediately after code without preserving `p_offset ≡ p_vaddr mod p_align` would violate the loader contract. The next BF stage must compute the new file offset, PIE RVA and `ADRP` when moving to larger classes. See [the source notes](../experiments/android_dynamic_elf_wrapper.bf.notes.md) and [Iteration 30](ITERATION30_REPORT.md).


A changelog of architectural constraints. Earlier dated sections describe the compiler at that time; the Iteration 19 decision near the end supersedes the former decoded-byte limit and unintegrated filtering choices.

## Source and bootstrap

- **Brainfuck stays Brainfuck.** One authoritative `compiler/core.bf`. No macros, compiler-aware comments, hidden syscall instruction or alternate high-level compiler source.
- **S2 is a release gate.** Two independent BF execution seeds must agree; native Stages 0–2 must produce identical bytes. A cosmetic refactor is not worth breaking self-hosting.
- **Annotations are separate.** `core.bf.notes.md` is tied to the source SHA and command offsets. `docs/ANNOTATED_VIEW.md` is derived from the raw bytes and cannot affect execution.
- **Testing infrastructure is not the compiler.** C seeds run BF. Python transports bytes, runs reference semantics, decodes ELF templates and records evidence. None generates native code for incoming BF source.

## Runtime contracts

- **Bound the problem honestly.** At most 16,128 executable **Brainfuck commands**, excluding ignored text, and 255 loop levels. Reject oversize input; do not truncate it.
- **Use fixed 32-byte native slots until a proven better design exists.** That makes relocation simple inside BF. File size pays for it.
- **Check memory movement.** Both pointer directions trap at the tape boundary. Removing those checks would require proof, not a benchmark screenshot.
- **Report native I/O failures.** Failed write exits 3; negative read exits 4; EOF stores zero. Both `read` and `write` retry `EINTR` inside their 32-byte slots. `EAGAIN` still fails fast; SIGPIPE remains the kernel's default.
- **ELF backing is real bytes.** The RX map is 524,288 bytes. Iteration 9 now writes exact Brainfuck-calculated `p_filesz` and no fixed zero fill. The kernel zero-fills the unmapped-file portion of RX `p_memsz`.

## Iteration 6

The old padding generator wrote `9 × 255 × 255 = 585,225` bytes. It now writes `8 × 255 × 255 + 16 × 255 = 524,280` bytes. Same ELF mapping, less dead weight. The self-compiler grows by 34 BF commands and still passes its three-stage bootstrap. The independent verifier checks **exact** length and zero padding, not just a minimum file extent.

## Iteration 7

An interrupted `write` now retries the same byte. The new 32-byte x86-64 slot uses `push`/`pop` for small register constants, tests `-EINTR`, and branches back to its own setup on that one error. The source-region emitter is smaller because it builds literal machine-code bytes with byte arithmetic and zero resets instead of repeating hundreds of `+`/`-` commands. This is internal Brainfuck logic, not a macro language in the repository.

A ptrace-based Linux test substitutes `-EINTR` for the first `write` without performing the syscall. The native program must then make a real second attempt and deliver exactly one byte. `-EAGAIN` still exits(3). Interrupted reads remain an open issue. The fixed padding was not changed.

## Iteration 8

The read slot now retries `-EINTR` too. It needed five bytes for the error comparison and jump. Instead of widening every source-command slot, the ELF startup now computes `r14` from the tape base and initializes `rdx = 1`. Linux syscalls preserve that register; write slots also restore it to 1. The BF literal emitter for the read slot uses the existing temporary cells and is shorter than the original. No C-side instruction patching and no new Brainfuck instructions.

The injected read test uses `ptrace` to substitute `-EINTR` without consuming input. It then requires a real second read, once with a byte and once with EOF. The compiler self-hosts unchanged through three native stages. This solves EINTR, not asynchronous nonblocking I/O.

## Documentation

Status comes from executable evidence and hashes; `tools/sync_status.py` rejects inconsistent records. The documentation voice follows `docs/STYLE.md`, derived from the public writing samples linked there. We copy the latest user-supplied requirements into `docs/PROJECT_REQUIREMENTS.md` rather than rewriting them to match the implementation. Unmet requirements stay unmet.

Before claiming an optimization, show its preconditions, preserve trap and byte-I/O behavior, rerun S2, and measure the thing. The compiler has no optimizer yet. Don't manufacture one in prose.

## Iteration 9

**Stop padding the ELF.** The old output scheme added 524,280 fixed trailing zeros. The compiler now scans its buffered source in Brainfuck, adds 32 for every decoded input byte to a 24-bit ELF length starting at 215, and writes that calculated `p_filesz` directly into the program header. The file ends after its native exit instruction. The code mapping remains 512 KiB, so the loader handles the zero-filled memory tail. No Python or C linker repairs the file.

The first attempt accidentally emitted literal success instead of the compiler's actual error cell. Another failed attempt overwrote pending input-error flags. Both were caught by the bootstrap/rejection gates and corrected in BF. The accepted source preserves the flag through the header pass, restores it afterward, and self-compiles to identical 509,239-byte binaries.

**Comments are not free yet.** The existing backend puts noncommands into 32-byte NOP slots and the input buffer counts decoded bytes. Document that contract rather than claiming a 16,128-*command* source limit the compiler never implemented. True comment compaction is separate engineering work.

A 251-command independent BF length routine under `experiments/` checks the arithmetic separately. It is not an authoritative compiler or a new source language.

## Iteration 10

The compiler's self-hosting fixed point already works, so a lexer refactor must not be slipped into the production parser without understanding its four-cell buffer and 32-byte relocation arithmetic. Keep a separately executable **862-command BF command filter** until those contracts can be changed together. All 256 byte values are tested. A testable filter and an integrated compiler pass are not the same thing.

Add a template-level tape-safety audit before attempting bounds-check optimization: the code's `r12` pointer remains inside `[r13, r14)` at instruction-slot boundaries; a move outside it takes `exit(2)` before accessing memory. Keep claims conditional on the exact code bytes, target semantics, and correctness of the verifier. Compiler scratch-region nonoverlap is still open.

Use `tools/verify_release.sh` as the verified runbook for required evidence gates; `tools/verify_release.py` records the accepted gate manifest. Individual validators stay separate so one failed subsystem remains easy to identify. The release does not get a green status by skipping a gate.

## Iteration 11

A diagnostic-only build of the C BF seed now traces the compiler's tape usage on eight inputs. The 16,128-byte witnesses reached cell 64,583, within the fixed 65,536-cell tape. Source-byte cells were checked after decoding and after emission. Escaped `00` and `FF` normalize to ignored byte `01` internally. The emitter temporarily mutates those cells and restores them, so a simplistic always-immutable rule would be wrong. This is execution evidence, not a full nonoverlap proof.

The latest uploaded requirements replace the older project-spec copy. They require inline safe `.bf` comments and native self-hosting on **Windows x86-64 and Android AArch64** as well as Linux. Neither new platform nor comment-independent artifacts are implemented here. Updating the requirement does not magically generate PE headers.

## Iteration 12

**Put safe comments in the real Brainfuck source.** Six short `#` annotation lines now describe the actual compiler phases. They use no Brainfuck command bytes and are checked by a dedicated linter. A standard interpreter sees the same 15,907 instructions as before. Both BF seeds and native Stages 0–2 produce a byte-identical new 512,727-byte compiler, enlarged by 109 source NOP slots.

The extra source text leaves 112 bytes of self-hosting input capacity. That's not enough for the standalone 862-command filter, so this is intentionally **source readability**, not user-source compaction. Tests comparing two BF execution engines with annotations present/absent check that the compiler's logic is unchanged. Input comments still change the emitted artifact and count toward the decoded-byte ceiling. Do not conflate those contracts.

## Iteration 13

A one-byte-length lexer is not yet a frontend for an EOF-terminated compiler. Add a **1,031-command streamed BF filter** which handles the documented `FF01` / `FF02` transport and returns a final status byte. Six malformed-escape cases are rejected and independent BF seeds agree. An experimental two-BF-process chain yields comment-independent ELF artifacts and repeats a filtered self-hosting step, but it is not the single authoritative compiler. Do not elevate experimental chaining to the production path. No change to `compiler/core.bf`, the 112-byte headroom, or the S2 claim.

## Iteration 14 — optional BF-native filtered compilation

Accepted an explicit opt-in file adapter rather than pretending the unchanged decoder includes the BF lexer. Two **native Brainfuck executables** own filtering and machine-code generation. Python owns source byte stuffing, process execution, result status checking, immutable hash verification, and atomic output replacement; it is not compiler logic. The extra process is a disclosed transport dependency. Direct `core.bf` still counts noninstructions and has the old limit. Integrated single-compiler filtering remains the next blocker, rather than a completed milestone.

## Iteration 15 — contracts before decoder surgery

The existing filtered adapter now bounds raw input to 8 MiB rather than loading arbitrarily large files into the Python transport. Filtered command capacity remains 16,128, and the BF backend still validates brackets and emits bytes. The new test contract deliberately inserts ignored bytes inside loops and checks every emitted branch displacement before running resulting ELF binaries. This protects future in-core lexing changes without pretending the two-process setup has become a single Brainfuck compiler. No modification to `core.bf` is claimed.

## Iteration 16 — smaller stream filter without rewriting core

Cumulative comparisons shorten the standalone Brainfuck stream filter from 1,031 to 816 commands. A naive 680-command candidate made common `+`/`-`-heavy streams slower because comparing negative modulo-256 differences repeatedly copies large byte values. Keep conditional early-match tests for the low ASCII instructions, then use the compact delta checks for the remaining instructions. The executed 390-valid/10-malformed comparison against the historical BF source confirms behavior; timing results are reported separately and are not proof of universal speed. Keep the original BF source under `evidence/history/iteration15`. Do not claim this satisfies the integrated decoder requirement.

## Iteration 17: do not promote oversized in-core filtering

An in-decoder Brainfuck classifier and compactor is functionally demonstrated, and is the clearest route to single-compiler source filtering. We rejected direct promotion because the derived full compiler exceeds its own source capacity by 1,444 instructions. The prototype has regression cases for the 256-record carry and the overflow sentinel; both broke during development. Keep the S2 production source unchanged until a smaller implementation passes native Stage 0–2.

## Iteration 18: trade scratch distance for source size, not silent corruption

The 801-command early candidate reused neighboring count-carry cells and broke the source ceiling despite ordinary examples matching. The accepted 1,045-command experiment explicitly saves and restores both lanes. This saves 620 commands over the verified Iteration 17 approach and preserves the 16,128/16,129 boundary. The instrumented BF seed checks count retention and record retirement; a deleted restoration triggers an actual failure. Promotion is still rejected because 16,952 BF commands cannot self-compile within the existing 16,128-record limit. No change to the authoritative compiler or execution profile.

## Iteration 19 — native source filtering accepted

The unintegrated decoder decision from earlier iterations is **superseded**. The authoritative BF compiler now owns filtering directly, preserves a 16,128-command source ceiling, and self-compiles natively through Stage 2. The validated 1,045-command in-core compactor fits after 39 fixed literal runs were replaced with short Brainfuck loops saving 2,093 instructions. The resulting source is **15,559 bytes** with **14,859 commands**. The resulting Linux ELF is **475,703 bytes**. Historic decisions and measurements above are retained for provenance, not current release status.

## Iteration 21 — Begin Android with an isolated Brainfuck code emitter

Keep the verified Linux S2 bootstrap stable while implementing the first AArch64 encoding and ELF loader contracts in a separate standard Brainfuck program. A partial target emitter can be tested on the Linux host without claiming on-device support. The first prototype accepts only three straight-line BF instructions and emits fixed-format ELF PIE images. Separate linker structure from native execution evidence: the latter is still missing. It would be premature to modify the authoritative compiler before ARM64 code generation and Android loader behavior have execution evidence.

## Documentation D0 — 2026-10-13 Android-first sequencing

Keep Linux native S2 unchanged while Android is completed **before** Windows. Plan 14 engineering iterations for an Android `arm64-v8a` shell compiler (26–39), 6 for Windows x86-64 PE32+ (40–45), and 2 for shared qualification (46–47): **22 baseline**, potentially **28–34** after bounded rework. This is a scheduling estimate, not implementation evidence. "Universal" means ordinary V0 BF across all eight instructions within a documented resource envelope, with the proposed 300,000-command acceptance target, native compiler execution and target-native self-hosting; it does not mean all Android ABIs, APKs, JNI bridges, external APIs or arbitrary program sizes. Track these separately in [`IMPLEMENTATION_ROADMAP.md`](IMPLEMENTATION_ROADMAP.md), [`PLATFORM_ACCEPTANCE.md`](PLATFORM_ACCEPTANCE.md), and planning-only [`../status/ROADMAP.json`](../status/ROADMAP.json). Existing evidence and historical decisions are not retroactively altered.

## Iteration 26 — bounded BF streaming and frozen Android byte contract

Adopt [`ANDROID_COMPILER_PROTOCOL_V1.md`](ANDROID_COMPILER_PROTOCOL_V1.md) as the next-engineering contract. Retain the existing reversible `FF01` and `FF02` raw-byte transport, compiler-owned source parsing, single trailing status byte, and fail-before-install behavior. Android's BF source cannot be read in full into 65,536 compiler-tape cells at the proposed 300,000-command target. Select a bounded **multi-pass BF-owned streaming/byte-spool strategy** for investigation, with explicit multi-byte indexes, bracket-depth limit, overflow failures and compiler-owned long-branch and ELF calculations. An opaque host transport may replay bytes at BF-requested positions but may never parse or patch native code. A naive multi-pass O(n²) relocator is a documented performance risk, not a resolved design. Compiler self-hosting on Android remains absent.

The frozen contract is backed by a new **Linux-hosted execution test** of the eight existing BF stages and source-wire behavior; see [`../evidence/iteration26_contract.json`](../evidence/iteration26_contract.json). No existing BF source, Android ELF or baseline hashes were changed. Two Linux-native self-compilations were byte-identical; the cold seed Stage 0 and full tape audit were not rerun. **Do not promote** this contract to Android native compiler maturity.

## Iteration 27 — byte streaming and wide count are BF owned

A second scanner exists at [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf) as **ordinary Brainfuck**, not a generated high-level source language. Keep the original `stream_filter.bf` available because the downstream Android emitter is still ten-command bounded. The new scanner increments a 24-bit count only when the BF filter emits a recognized instruction, detects overflow and malformed FF framing, and appends a count/status trailer. The optional `--scanner` transport discards that trailer before feeding the existing **BF-only** bracket and ELF stages. This proves large input scanning and a non-disruptive adapter, **not general Android code generation or on-device compilation**. Evidence: [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json) and [`../evidence/iteration27_scan_integration.json`](../evidence/iteration27_scan_integration.json).

## Iteration 28 — BF matching before target encoding

Preserve the canonical Linux compiler and the ten-slot Android backend. A separate BF parser now produces 24-bit bracket positions and an eight-bit nesting depth. Another BF program walks a five-cell-per-frame stack and emits matching positions. This eliminates host-side pairing in the experimental stage without pretending that its records feed the existing AArch64 relocator. The relocation and dynamic ELF gates remain open. See [the Iteration 28 report](ITERATION28_REPORT.md).

## Iteration 28 follow-up — use a fixed long conditional branch veneer

Instead of widening `CBZ`/`CBNZ` itself, retain the 48-byte AArch64 slot and use `LDRB` followed by the *inverse* conditional branch that skips a plain 26-bit `B`. This keeps slot arithmetic straightforward and covers the 300,000-command source target without a target-specific assembler. Standard BF computes both signed displacements from 24-bit bracket pair fields. The short-range encoder remains the production ten-slot path until a BF-native dynamic patcher consumes the new records. Explicitly reject pair separations beyond **2,796,201** rather than wrapping machine branch bits. Evidence: [`../evidence/iteration28_wide_branch_encoding.json`](../evidence/iteration28_wide_branch_encoding.json).

# Handoff — Iteration 16, 2026-10-12

## The compiler

`compiler/core.bf`: **16,016** raw bytes, containing **15,907** original BF instructions and 109 ignored annotation bytes. The hash-locked notes use filtered instruction offsets. There are **112** decoded source bytes left before the self-compilation input ceiling.

## What changed

The fixed **524,280** zero bytes at the end of every ELF are gone. Brainfuck scans its four-cell-per-byte input buffer, calculates `215 + 32 * input_bytes` across three wrapping byte cells, and writes those bytes directly into ELF `p_filesz`. The emitted file ends after native `exit(0)`. `p_memsz` is still 524,288 bytes so the kernel maps enough executable address space for the bounded maximum.

The first build failed invalid-bracket acceptance: I had replaced the compiler's real trailing status byte with a literal zero. Fixed. A second bug let oversized/framing-error input lose its pending error bit when the new header consumed scratch cells. The flag is now saved and restored around sizing/header generation. Both bugs have executable regression checks. Small detail, if you enjoy accidentally declaring corrupted input valid.

The installed compiler ELF is **512,727 bytes**, versus 1,021,071 bytes in Iteration 8. The independent seeds and native Stages 0–2 generated identical output. Exact hashes live in `evidence/selfhost.json`.

## This iteration: streamed BF filter and protocol validation

`experiments/stream_filter.bf` has **1,031 executable BF commands**, consumes EOF-terminated byte-stuffed compiler input, and outputs only actual BF commands plus a success/error byte. Six malformed escape cases reject. Tests run 189 valid source inputs through the native filter, compare 16 seed executions, and run a test-only chain of BF filter and BF compiler. Comment variants agree at the ELF byte level after filtering; the filtered compiler successfully compiles itself again. This is not a production refactor: the core decoder and original capacity limit are unchanged. See [`STREAM_FILTER.md`](STREAM_FILTER.md). The separate Iteration 13 gate passed; the Iteration 14 release had fourteen gates.

## Previous iteration: safe source annotations

Six concise comment lines now sit in the actual authoritative `.bf` file. `tools/source_check.py` rejects any of the eight command bytes in a declared comment; `tests/verify_source_comments.py` demonstrates unchanged BF execution using two independent seed interpreters. The filtered instruction stream is byte-identical to Iteration 11; native Stage 0–2 still match. User-comment compaction is not installed; the source comments consume output slots.

## Previous iteration: compiler tape traces

The production `core.bf` is unchanged, and Linux S2 must stay green. [`COMPILER_TAPE_AUDIT.md`](COMPILER_TAPE_AUDIT.md) describes a new audit-only C BF interpreter build. It executes the actual compiler source on eight cases, checks the source-buffer lane after decoding and again at termination, logs pointer footprints by phase, and compares every emitted ELF against the production native compiler. An intentionally incorrect source oracle is rejected.

At 16,128 decoded bytes the highest observed tape pointer is cell **64,583**, leaving 952 cells. That is not a proof for all compiler paths. The emitter temporarily mutates source-byte cells before restoring them, and both escaped `00` and `FF` are stored as noncommand `01`. The audit checks those actual contracts, not a prettier story.

The separate 862-command fixed-length BF filter and generated-program pointer invariant audit from Iteration 10 remain in place. Neither is production source compaction, and neither is a formal compiler-memory proof.

## Reproduce

```sh
sh tools/verify_release.sh
```

`tests/verify_emission.py` inspects dynamic ELF lengths and NOP-only comment slots, as well as branch displacements, bounds checks, syscall patterns and W^X segments. `experiments/elf_file_size.bf` is a separate 251-command reference arithmetic routine; it is **not** another authoritative compiler.

## Updated project requirements

The new uploaded `Brainfuck Compiler.md` is mirrored in `docs/PROJECT_REQUIREMENTS.md`. This revision explicitly requires safe inline `.bf` comments and native self-hosting on Windows x86-64 and Android AArch64. Both platforms remain unimplemented; the Linux S2 result still stands. See [`TARGETS.md`](TARGETS.md).

## Next job

First integrate BF-side command filtering and enable safe inline `.bf` comments with comment-independent artifacts while preserving four-cell buffer ownership, accurate ELF byte counts and bracket targets. Do not simply paste either filter experiment into `core.bf`: its 112-byte self-hosting headroom is smaller than the filter. Then tackle the 32-byte slots and capacity ceiling. Prove compiler-internal tape region nonoverlap and add fair C/Rust baselines afterward. The input-limit behavior must not be relabeled as command-only until the Brainfuck parser actually filters it.

Keep docs in [`STYLE.md`](STYLE.md) voice. Keep `PROJECT_REQUIREMENTS.md` unchanged. A new README cannot repair a bad compiler; the tests get that privilege.

## This iteration: executable filtered file workflow

`bootstrap/run_filtered_compiler.py` makes the separate native BF filter usable as an optional file transport stage before the native BF compiler. Neither process contains non-BF compiler logic. Sources with very large ignored sections can be compiled provided their filtered commands fit the old 16,128-byte limit. The adapter authenticates the installed executable hashes and atomically writes results only on success. 28 tests plus CLI negative cases and a long-comment self-host demonstrate the behavior; evidence in `evidence/filtered_adapter.json`. This does **not** alter the compiler decoder or complete the integrated source-filtering objective. That iteration required fourteen release gates; Iteration 15 adds a fifteenth.

## Iteration 15 — filtering contract and bounded transport

Added `tests/verify_filter_integration_contract.py` as the fifteenth release gate. It checks comment bytes placed at individual command boundaries inside nested loops, emitted branch displacements, exact ELF identity against command-only compilation, EOF, wrapping and tape boundary traps. The optional Python transport now caps raw input at 8 MiB and checks filtered-command count before calling the native compiler. Neither change touches authoritative Brainfuck code; the next job remains replacing the decoder with a compiler-owned command filter within the buffer budget. Evidence: `evidence/filter_integration_contract.json`.

## Iteration 16 — smaller lexer, same compiler

`experiments/stream_filter.bf` now has 816 executable commands and emits a 27,959-byte ELF. The previous 1,031-command source is retained in `evidence/history/iteration15/stream_filter.bf` for native historical-equivalence testing. Conditional early-match gates address a command-heavy runtime slowdown observed in an earlier compact candidate; the final source passes the extended comparisons and two nine-pair interleaved filter microbenchmarks. See `docs/STREAM_FILTER.md` and `evidence/stream_filter_equivalence.json`.

The authoritative 15,907-command `compiler/core.bf`, its native ELF and S2 source limit are unchanged. The new sixteenth gate compares 390 valid and 10 malformed streams against the prior BF implementation. Next change remains an in-core decoder refactor with no external compiler logic. Windows and Android support and compiler tape nonoverlap proofs remain open.

## Iteration 17 — compiler decoder patch, still experimental

See [`DECODER_COMPACTION_PROTOTYPE.md`](DECODER_COMPACTION_PROTOTYPE.md). A BF-only insertion at filtered offset 1145 can move ignored bytes out of the compiler source buffer without changing emission. The final test candidate is 1,665 BF instructions and passes 85 compilation equivalence cases, six independent-seed comparisons, malformed transport checks and native program witnesses. Early variants lost one command per 256 and failed the 16,129-command error case; the released experiment does neither. The canonical 16,016-byte source and its 512,727-byte zero-trailing-padding ELF stay unchanged. The experimental derived compiler has 17,572 BF commands and fails self-compilation due to the 16,128 limit. **Do not replace `core.bf` with this oversized patch**. Reduce it or recover at least 1,444 BF source bytes with safety evidence, then rerun the full bootstrap. No Windows/Android claim.

## Iteration 18 — classifier reduction with count lane auditing

The next patch candidate is **1,045 BF instructions** and is tested in `experiments/decoder_compaction_insertion.bf`. Its derived compiler has 16,952 BF instructions, still 824 too large to self-compile. It passes the same 85 native-output comparisons as Iteration 17. Both count lanes are dynamically checked by the independent seed for 89,314 source visits, and a removed-restoration mutation is rejected at the 256th command. Backups are held in remote future scratch and cleared on exit; compaction can retire the next count record, which is a distinct case from retention. Consult `docs/DECODER_COMPACTION_PROTOTYPE.md` and the recorded evidence. The Linux production source and ELF are unchanged. Continue reducing the patch, but do not treat its interpreter Stage 0 test as S2.

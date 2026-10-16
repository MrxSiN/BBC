# Current state — 2026-10-12, Iteration 18

## Actually executed

- `compiler/core.bf` contains **16,016** bytes with **15,907** canonical Brainfuck commands and 109 safe ignored comment bytes. Notes are hash-locked to filtered instruction offsets.
- **S2 self-hosting works.** Two different C BF interpreters agree with native Stages 0–2. Each compiler ELF is **512,727 bytes**. The exact SHA-256s and execution details are in `evidence/selfhost.json`.
- The backend handles all eight BF commands, checked tape pointer movement, byte wrapping, nested loops, EOF-zero input, and Linux I/O. Both byte syscalls retry `EINTR` and report other errors.
- Every generated ELF is exactly **`215 + 32 * decoded_source_bytes`** bytes long. Its RX `p_filesz` matches that count; `p_memsz` stays **524,288** bytes. The separate RW tape is **65,536** bytes. **Fixed trailing padding: 0 bytes.**
- Production verification still passes: 178 base semantic cases, 345 adversarial cases, 32 structural ELF inspections, 11 corruption checks, 10 syscall fault assertions, and 62 checks of a standalone BF file-size arithmetic routine.
- An **816-command standalone BF stream filter** (reduced from 1,031 commands) now accepts the compiler’s byte-stuffed EOF-terminated transport, rejects six malformed-escape cases, and successfully chains through the native BF compiler for comment-invariant artifacts and a filtered native self-hosting cycle. **This is two experimental BF executables, not integrated production compiler filtering.**
- An **862-command standalone Brainfuck input filter** was compiled natively and tested on 135 cases, including all 256 byte values. Twenty-four comparisons with two independent BF seeds agree. **This is an experiment, not a production frontend change.**
- New template-level safety audit: 131,072 abstract guarded pointer transitions, nine executed native witnesses, ten rejected unsafe ELF mutations. These are conditional checks of the generated-program pointer invariant, not compiler-internal tape proof.
- An additional **eight audit-only BF interpreter traces** check compiler source storage and codegen results, including three inputs of 16,128 bytes. The highest observed tape cell is **64,583**; output bytes match the native compiler. This remains dynamic evidence, not a proof of all scratch allocations.
- **Sixteen verification gates** execute from `tools/verify_release.sh`, including the new compiler-tape audit. Their evidence and status matrix are regenerated after passing.
- The uploaded requirements are synchronized in `docs/PROJECT_REQUIREMENTS.md`. Windows x86-64 and Android AArch64 remain unimplemented. Safe inline `.bf` source annotations are implemented, but comment-independent artifacts remain unimplemented.
- The maximum input is **16,128 decoded source bytes** and the maximum bracket depth is **255**. The compiler itself has **112** decoded bytes of source headroom.

- Source-comment linting rejects command bytes in ignored annotations. Ten paired executions across two independent BF interpreters show annotated and stripped compiler source produce identical ELF output for identical compiler input. This is not production user-source comment compaction.

## Still not done

- **Source comments consume capacity in the production compiler.** The separate stream filter can strip them before a test-only compiler chain, but that is not an integrated single-compiler frontend.  The canonical `.bf` file now has six safe ignored comment lines; the complete comment-independent artifact requirement remains incomplete until input filtering preserves identical artifacts. Non-BF bytes produce 32-byte NOP slots; within the raw-byte limit, semantics are unchanged. Long comment-only input can run out of buffer room. The tested standalone BF filter shows the lexical part is possible, but integration and capacity changes remain unfinished.
- Native slots still cost 32 bytes each, including comments. Dynamic `p_filesz` removed the old **524,280** fixed trailing zeros, not per-source-slot waste.
- Nonblocking `EAGAIN` is a reported failure, not an automatic retry. No scheduler or readiness wait.
- There is no integrated optimizer, formal whole-compiler memory-safety proof, native C/Rust performance comparison, bare-metal backend, or working Windows/Android native target.

## Acceptance

**S2 EXECUTED**, stronger but still partial S3 safety evidence. The compiler has an actual Brainfuck-side variable-length ELF header and file emitter. No adapter patches target bytes. Self-hosting, executed semantic tests and independent machine-code inspection agree under the documented bounded profile.

## Iteration 14

A hash-checking optional two-BF-executable file adapter performs true BF-only lexing followed by BF-only native code generation. It passes 28 executed comparisons, source-capacity and failure-preservation checks, and expanded-comment self-hosting. The native `core.bf` and ELF remain unchanged. Single-program integrated filtering is still open; see [`FILTERED_ADAPTER.md`](FILTERED_ADAPTER.md).

## Iteration 15

The optional filtered adapter now rejects more than 8 MiB of raw input at its transport boundary and rejects more than 16,128 filtered bytes before invoking the backend. This is a deliberate external adapter resource cap, not a change in Brainfuck semantics. The new 36-case integration contract compares native artifacts, independently validates branch relocations and slot encodings, and executes comment-interleaved programs, including nested loops, EOF and pointer traps. Five invalid inputs reject. The authoritative BF compiler and its compiled ELF remain unchanged. **Single-BF-program source filtering is still UNIMPLEMENTED.** See [`FILTERED_ADAPTER.md`](FILTERED_ADAPTER.md).

## Iteration 16

Reduced the BF-only streaming filter from 1,031 to **816 executable commands** using cumulative ASCII deltas and conditional checks that stop after matching an instruction. The separate native filter ELF shrank from 34,839 to **27,959 bytes**. The complete 189-case stream suite and 390-case historical/native equivalence suite pass, including 10 malformed transport comparisons. Two non-gating workloads were measured with nine interleaved repetitions per filter; see [`BENCHMARKS.md`](BENCHMARKS.md) and `evidence/stream_filter_equivalence.json`. The authoritative compiler is unchanged, still **S2 EXECUTED on Linux only**, and the filter remains a separate executable.

## Iteration 17

A **1,665-command experimental in-core BF decoder patch** now compacts ignored source before the existing compiler emitter. A derived test copy of the actual compiler passes 85 byte-for-byte comparisons with the native command-only baseline, six alternate-seed comparisons, five malformed-transport rejections and eleven native runtime checks. The key edge cases are byte-count carry every 256 records and the overflow sentinel at 16,129 commands. The derived compiler has 17,572 executable BF instructions, 1,444 above its self-compilation limit. It **rejects compiling itself**, so this patch is not promoted. Production `core.bf`, its zero fixed padding, 16,016-byte raw source size and S2 ELF remain unchanged. The next priority is safe source reduction or decoder redesign sufficient to enable actual Stage 0–2 self-hosting. Evidence: [`../evidence/decoder_compaction_prototype.json`](../evidence/decoder_compaction_prototype.json).

## Iteration 18

Reduced the *experimental* in-core BF compactor from 1,665 to **1,045 instructions** by reusing closer scratch lanes and explicitly preserving two count metadata lanes. The resulting derived compiler is **16,952 instructions**, still **824 beyond** the 16,128 decoded-byte self-compilation limit. Eighty-five native-output comparisons, six alternative-seed comparisons, five malformed transport cases, eleven generated-program executions, and the compiled-self-source rejection pass. The audit-only BF interpreter checked 89,314 decoder visits across those cases. A variant missing a count-lane restoration is detected at the first 256-byte carry. These dynamic checks are not a proof of compiler memory separation. The original experimental BF source is preserved in `evidence/history/iteration17_decoder_compaction_insertion.bf`.

**Authoritative `compiler/core.bf` remains unchanged**, as does its 512,727-byte native compiler ELF and Linux native S2 evidence. Filter integration is still blocked; Windows and Android remain unimplemented.

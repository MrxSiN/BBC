# Shared engineering instructions — prepend to any A–E agent task

You are the implementation engineer for BBC (a compiler implemented in Brainfuck) and XAX (its canonical verified graph/native backend). **Implement the requested optimization**, with the smallest verified change that actually works. Do not stop at a high-level design if local repositories and tooling permit implementation.

## Mandatory first pass

1. Record BBC/XAX HEAD hashes, target environment, working-tree status and baseline commands. Never discard unrelated working-tree changes.
2. Read `BBC/AGENT.md`, `README.md`, `docs/01_BRAINFUCK_PROFILE.md`, `docs/02_BFX_CONTRACT.md`, `docs/06_PERFORMANCE_PLAN.md`, `docs/07_OPTIMIZATION_PROOFS.md`, `docs/17_STREAMING_COMPILATION.md`, `docs/21_UNIFIED_COMPILATION.md`, `docs/25_NATIVE_COMPILE.md`, relevant `.bf.notes.md` files and test/evidence instructions.
3. Read `XAX/AGENT.md`, `docs/09_AI_PROTOCOL.md`, `compiler/integration/bfx/COMPILE.md` and inspect the current canonical importer/lowering/verification graph and relevant tests. Determine actual interfaces and ownership; don't assume undocumented APIs exist.
4. Build a clean baseline before editing. Identify exact source-to-BFX-to-import-to-lower-to-executable flow for O0 and O1, Windows x86-64 and Android ARM64.

## Design guardrails

- BBC executable frontend code must remain only the eight Brainfuck instructions; do not add production parsers, codecs, compiler passes or harnesses in Python/C/etc to BBC. Seed interpreters and external test runners may live **outside** BBC. Follow the separate XAX repository's tooling conventions within XAX.
- Do not invent textual XAX as a source format. Make minimal, workspace-consistent semantic graph edits with freshness/expected-root checks and successful verification. Preserve proof, ownership, borrowed-view initialization/lifetimes/nonaliasing, and provenance.
- Current BFX successes have exact header `42 46 58 00 01 00`, little-endian u32 count and exactly that many bytes; failures are six bytes. The decoder recognizes standard eight BF commands, CLEAR `00`, 7 positive powers `01..07`, 7 negative powers `08..0E`, right powers `0F..15` and left powers `16..1C`. Preserve ID `01` and the only decoder. No format expansion by accident. If a feature truly needs new opcodes, stop and present a narrowly scoped **explicit format migration design**, tests and consumers; do not silently ship a second path.
- Runtime: 65,536 cells (byte wrapping); pointer begins at zero; the entire tape resets each valid call; invalid lengths reject *before* reset; EOF reads 0; output remains capacity-bounded; loops may never terminate; opposite moves cannot generally be cancelled; movement fails at its first tape crossing. On errors, preserve status, timing/order of observable output and last-valid pointer/tape semantics as relevant to the call contract. Fast paths need fallback to exact behavior when a proof/precondition fails.
- Source budget: 1 MiB; unoptimized command budget: 65,536; max balanced nesting 32,768; bounded seed is separate (3,840 commands, depth 255). The streaming coordinator chunks at 32,768. Preserve validation precedence: framing, size, brackets, plus public interface's checks as documented. Do not publish a provisional success.
- O0 must remain a useful correctness/baseline control. O1 must not reject previously supported source sizes. There is no new unsupported optimization flag unless explicitly specified and justified.
- Don't modify pinned historical benchmarks, existing evidence JSON, competitor snapshots or golden binary bytes to force a pass. Document new fixture identity and make new evidence files. Keep build artifacts in ignored build areas.

## Required workflow

1. State a falsifiable hypothesis, identify the dominant cost in existing benchmarks, isolate eligible control-flow regions and establish no-regression proof obligations.
2. Implement a narrowly scoped change; if unsupported, distinguish a real `BLOCKED` reason from work not attempted. Avoid unrelated refactors.
3. Add deterministic positive, negative, wraparound, nested-loop, zero-entry, tape-edge, I/O, output-capacity and repeated-call tests appropriate to the optimization. Test whole-buffer state/guards, not just printed output.
4. Compare O0 vs O1, baseline vs optimized, BFX decoder acceptance/rejection, machine code outputs and full programs, using an independent interpreter/reference outside the production pipeline. Include known nonterminating cases under a finite test-step cap without interpreting the cap as language semantics.
5. Rebuild/verify both target artifacts; distinguish emulator results from execution on a real Windows host and real Android ARM64 hardware. If devices are unavailable, report `BLOCKED` and do not claim target-tested status.
6. Benchmark with pinned code/inputs, paired counterbalanced trials, warmups, distributions or medians plus spread, hashes, host details and raw per-trial samples. Separate frontend, graph import, verification, lowering, packaging, end-to-end build, whole-process execution, warm-call runtime, binary size and memory where measurable. Do not confound Wine launch overhead with generated-code speed.
7. Keep a change only if correct with a defensible net gain. Record negative or inconclusive results honestly.

## What to return

- **Files changed** (BBC vs XAX, exactly where and why), short design, any migration decision.
- **Formal-ish equivalence argument**, explicitly handling first-crossing movement failures and zero-entry loops.
- **Tests:** commands, case counts, expected and observed results, target platforms, hashes, failures, skipped checks.
- **Measurements:** baseline/optimized raw samples, medians, variance, regression counts and full build + runtime + memory + size changes; no fabricated numbers.
- **Status:** `EXECUTED`, `MEASURED`, `PROTOTYPE`, `UNIMPLEMENTED` or `BLOCKED` for each claim.
- **Remaining risks** and smallest next action.

# Historical in-core command compaction prototype — Iterations 17–18

Historical scope: Iterations 17–18. **Superseded by Iteration 19**, where the compactor is integrated and native Stages 0–2 pass. The paragraphs below describe the preserved older compiler, not the current production source.

This experiment is different. `experiments/decoder_compaction_insertion.bf` is now a **1,045-instruction standard Brainfuck block** that runs *inside a derived test copy* of the actual compiler decoder, directly before instruction offset **1145** (the decoder's iteration-closing bracket). No non-Brainfuck code recognizes input commands or generates the ELF.

## How it works

At the insertion point, the previous decoded source byte sits at tape cell `x`; the next byte is at `x+4`, where the pointer rests. The patch classifies the previous byte using the original eight ASCII command values, plus the internal zero sentinel. Accepted commands leave the next byte at `x+4`. Ignored bytes move the next byte back into `x`, erase the orphaned record's count, and leave the pointer at `x`. The decoder then reuses that record on its next pass. Existing source-size arithmetic, 32-byte emission and bracket resolution can stay exactly as they are.

The shortened classifier temporarily uses `x+3` and `x+7` as scratch. Both lanes can contain high-count metadata and must be preserved, not treated as conveniently empty cells. The insertion copies these two values into more distant future scratch cells and restores them after classification. The accumulator and error-sentinel lifetimes are also constrained. The original Iteration 17 patch used `x+1`, `x+5`, `x+13` and `x+17`; it is retained under `evidence/history/iteration17_decoder_compaction_insertion.bf`. Early candidates corrupted the byte-count carry at every 256th source command. A later candidate cleared the end-of-buffer error record and silently accepted an oversized program. The tested patch preserves the count carry and **keeps the zero sentinel** so the original overflow path remains active. `x+9` is reserved near the capacity boundary and is not scratch space.

An audit-only build of the independent interpreter checks the two count lanes around every executed insertion and confirms that both temporary backup lanes are cleared afterward. Reclaimed records may retire their associated count metadata. An intentionally mutated variant that omits one restoration fails the audit on the 256th command. These are dynamic execution checks, not a formal nonoverlap proof.

The test builds a derived Brainfuck source by inserting the experimental block at the hash-checked offset. It runs that source under the independent C Brainfuck seed, compares the complete output/status byte stream against the production native compiler compiling the *stripped* command stream, inspects representative ELF artifacts, and executes selected binaries against the semantic reference. Six cases additionally use the alternate independently written seed.

Run:

```sh
python3 tests/verify_decoder_compaction_prototype.py
```

## Executed results

- **85** interpreter-executed prototype compilations agree byte-for-byte with direct command-only native compilation, including the full annotated `core.bf` source, nested loops, wrapping, raw NUL/FF source bytes, rejected brackets, and a raw input larger than 16,128 bytes whose compacted command stream fits.
- **6** alternate-seed comparisons agree; **5** malformed byte-stuffed transports reject.
- **11** compiled programs execute and match the semantic oracle, including one tape-boundary trap.
- **16,128** source commands succeed; **16,129** are rejected without producing a partial executable.
- **85** cases also exercise the count-lane audit, covering **89,314** decoded visits in total; one missing-restoration mutation is detected.
- The derived compiler correctly **rejects compiling its own full patched source**. That is the blocker, not a milestone pass.

Exact cases and source/binary hashes are in [`../evidence/decoder_compaction_prototype.json`](../evidence/decoder_compaction_prototype.json).

## Not yet a release

The revised derived prototype has **16,952 Brainfuck commands**. The current compiler can accept only **16,128 decoded source bytes**, so self-compiling that patch is impossible without shrinking or redesigning the implementation. It exceeds the limit by **824 instructions**, even after removing all ignored comments. The authoritative `compiler/core.bf` and its 512,727-byte ELF remain unchanged; the prototype does not have native Stage 1–2 evidence and is not installed.

The Iteration 17 patch had 1,665 instructions; Iteration 18 saves **620 instructions (37.2%)**, without changing production code. The experimental compiler remains too large for its own input.

Next: reduce classifier cost further or free source capacity while preserving the overflow/carry cells and full S2 bootstrap. Do not silently promote this experiment, raise the tape limit without a new semantic profile, or let Python perform the filtering instead.

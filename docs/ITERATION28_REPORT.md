# Iteration 28 report — wide Brainfuck bracket pairing, partial gate

**Date:** 2026-10-13. **Classification:** PARTIAL. **Next task:** BF-owned AArch64 branch displacement encoding and relocation using the wide pair records; dynamic ELF is still absent.

## Implemented

- Added [`../experiments/android_wide_bracket_metadata.bf`](../experiments/android_wide_bracket_metadata.bf): 2,524 BF commands. Parses filtered commands, checks bracket balance, emits 24-bit positions and 8-bit depth; rejects depth over 255 and instrumented 24-bit count overflow.
- Added [`../experiments/android_wide_bracket_pairs.bf`](../experiments/android_wide_bracket_pairs.bf): 1,707 BF commands. Holds opening positions in a bounded five-cell-per-frame tape stack, emits matched opening/closing positions without foreign matching logic.
- Added optional `--wide-brackets` to [`../bootstrap/run_android_loops.py`](../bootstrap/run_android_loops.py), usable together with `--scanner`. The host only runs BF binaries, checks status/provenance and places existing fixed-size output; it does not compute pairs, relocations or machine code. The ten-command backend remains the actual emitter.
- Added [`../tests/verify_android_wide_brackets.py`](../tests/verify_android_wide_brackets.py) and recorded executable tests in [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json).

## Evidence

- **421** valid command streams produced *exact* metadata and matched-pair bytes against the independent test oracle, including command offsets beyond 65,535 and through 300,002 commands.
- **123** invalid streams rejected with nonzero output statuses. Nesting depth **255** accepted and **256** rejected. Instrumented 24-bit position overflow returned status **02**.
- **16** comparisons across independent standard-BF interpreters agreed with Linux-native execution.
- **8** existing ten-slot Android ELF outputs remained byte-identical with both BF metadata passes enabled. CLI verification also preserved the previous artifact on failure and installed the accepted image atomically.
- Native BF executables and source hashes are recorded in the evidence JSON and stage notes. Comments were stripped in test without changing output ELF bytes.

## Safety and limitations

The metadata parser uses cells 0–13 and the pairing stage has a five-cell frame stack through cell 1306 at maximum depth. The pair stage relies on **trusted metadata from the upstream BF parser**, rather than independently validating deliberately corrupted record fields. An invalid final status invalidates any prior output. Neither stage uses general memory outside its defined V0 regions in the tested execution paths; no formal full-program compiler-tape proof is claimed.

The existing `compiler/core.bf` and its generated Linux native ELF are unchanged, preserving the archive's Linux S2 proof. A **fresh Linux native Stage 1→2** self-compilation passed with byte-identical 475,703-byte ELF output at both stages; see [`../evidence/iteration28_linux_native_replay.json`](../evidence/iteration28_linux_native_replay.json). The independent cold Stage 0, full release audit and Android on-device tests **were not rerun in this iteration**. New code runs as Linux-native BF-generated stages; no AArch64 compiler executable or Android-native self-hosting exists. No runtime comparison against optimized C/Rust was conducted. The old Android source-to-native emission cap remains **10 commands**.

## Next priority

Convert BF-owned 24-bit bracket *pairs* into branch displacement records, including long-range AArch64 jump encoding beyond `CBZ/CBNZ imm19`. Feed those records into a BF-only dynamic output emitter and execute the resulting native programs on Android before advancing to a complete compiler claim.

## Follow-up — BF-owned AArch64 wide branch words (Linux-executed)

A new **13,985-command standard Brainfuck** stage, [`android_wide_branch_encoding.bf`](../experiments/android_wide_branch_encoding.bf), consumes 24-bit bracket position pairs and emits actual 32-bit `B` machine instruction words for forward and reverse loop jumps. A two-instruction inverted conditional veneer avoids the ±1 MiB `CBZ`/`CBNZ` immediate limit. The stage checks 26-bit `B` reach, accepts differences through **2,796,201 source commands**, and rejects longer ones with status `04`. Its own Linux native executable is **447,735 bytes**. See [protocol and tape notes](../experiments/android_wide_branch_encoding.bf.notes.md) and [execution evidence](../evidence/iteration28_wide_branch_encoding.json).

The dedicated test passed **171 valid position pairs**, **34 multi-record cases**, **six failure/propagation cases**, **eight real BF metadata/pair/encoder cases**, **four independent BF seed checks**, and **six byte-identical legacy Android ELFs** with the opt-in `--scanner --wide-branches` path. A **300,000-command input** was tested through the metadata, pairing and encoding stages. These are record-generation tests running **on Linux**, not Android ELF generation for 300,000 commands. The existing Android emitter and relocator still accept no more than **ten commands**; no native Android compiler was created. An attempted re-run of the older wide-bracket suite did not finish within the tool limit and is **NOT PASSED in this follow-up**; the original Iteration 28 evidence remains historical. Dynamic ELF layout and long-branch patching remain open. The canonical Linux `core.bf` source and compiler ELF remain unchanged; a fresh Linux self-hosting cycle was not re-executed during this follow-up.

## Follow-up regression snapshot

The follow-up local validation manifest is [`../evidence/iteration28_followup_validation.json`](../evidence/iteration28_followup_validation.json). The dedicated wide branch suite, I26 Android byte protocol suite, source scanner integration, original 166-image Android loop suite, safe-comment suite and documentation checks all **PASSED**. The CLI installed a valid legacy image and preserved it on rejection with `--wide-branches`. Canonical Linux compiler source and ELF digests still match the historical self-hosting evidence; that hash match **does not replace a fresh self-compilation replay**. The separate prior wide-bracket full-suite retest hit a 200-second execution ceiling and remains **INCONCLUSIVE** for this follow-up. No new on-device execution was performed.

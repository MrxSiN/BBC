# Iteration 57 callable memory safety checkpoint

The new opt-in AArch64 callable linear lane checks each pointer movement against caller-provided tape capacity and traps with status 3, while byte arithmetic wraps modulo 256. The 240-case simulator suite checks pointer bounds, EOF input, output buffers and tape updates. This is **executed testing, not formal proof**. Loops, host-ABI contract verification on Android hardware, and BF-controlled relocation safety are still open. [Evidence](../evidence/iteration57_dynamic_callable_linear.json).

---

# Memory safety

**Brainfuck has no Rust ownership system.** The useful safety contract here is smaller: generated BF pointer accesses cannot escape a fixed 65,536-byte tape, and cell arithmetic wraps in one byte.

Native `>` checks against the upper tape boundary; `<` checks against the base. An illegal move immediately exits(2). Read and write operate on the current cell; separate RX code and RW tape segments avoid deliberately writable executable memory.

`tests/verify_emission.py` checks every fixed native slot in sampled ELF files, the executable/tape permissions, exact `p_filesz`, bounds guards and loop targets. `tests/verify_adversarial.py` compares additional executed programs with a reference BF interpreter, including boundary traps and malformed inputs. The counts and hashes are in `evidence/`.

`tests/verify_tape_safety.py` additionally audits the guarded pointer transition at every one of 65,536 tape positions in both directions, verifies the allowed templates, runs nine native witnesses and rejects ten corrupted artifacts. The relevant invariant is `0x600000 <= r12 < 0x610000`, with `r13` and `r14` holding the bounds. It applies to **generated tape accesses conditional on verified native templates**, not a formal proof of the compiler itself. Full reasoning and assumptions are in [`SAFETY_AUDIT.md`](SAFETY_AUDIT.md).

The new file-size scanner uses three byte counters over the four-cell source stride. It preserves the pending input-error bit across the header-writing phase; losing that bit caused oversized source to appear successful in an early failed build. There are regression tests now. Compiler-internal tape lifetime and nonoverlap still need a stronger proof; passing tests are not a substitute.

Do not remove runtime bounds checks based on a favorable benchmark. Prove the affected pointer range first, including intermediate movement and the exact trap order.

## Header writer proof boundary — Iteration 20

[`HEADER_SCRATCH_SAFETY.md`](HEADER_SCRATCH_SAFETY.md) gives a conditional static proof for BF offsets 2848 to 4277: each of the 45 loops preserves pointer position, the 39 scratch-counter loops clear cell 61, and no header operation reaches outside cells 60 through 71. This proof assumes the incoming pointer is 60 and scratch cell 61 is zero. The audit-only interpreter witnesses those conditions in eight compilation cases. It is **not** a proof that all decoder paths establish the preconditions or that source records never overlap other compiler metadata.

## Iteration 27 scanner evidence boundary

The experimental [`../experiments/android_source_scan.bf`](../experiments/android_source_scan.bf) uses tape cells **0–14**: legacy streaming filter state 0–6, one emit marker at 7, a three-byte counter at 8–10, zero-check and backup scratch at 11–13 and an overflow sentinel at 14. Tests executed the 256/65,536 carry boundaries and a separately derived source with preloaded count `0xFFFFFF` that returned nonzero status on the next command. This is **not** a proof of compiler-wide cell ownership or safety for future general Android AArch64 codegen. Native Android did not run this new scanner; refer to [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json).

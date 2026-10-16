# Iteration 29 — larger bounded AArch64 ELF path (partial)

> **Later follow-up:** Bounded BF-owned wide loop patching is now executed. The linear-only limitations below describe the earlier Iteration 29 snapshot. See [`ITERATION29_LOOP_FOLLOWUP.md`](ITERATION29_LOOP_FOLLOWUP.md) for the newer evidence.

**Date:** 2026-10-13. **Classification:** EXECUTED Linux-native Brainfuck code generation with AArch64 instruction-simulator verification; **not** Android-device execution. **Milestone:** PARTIAL.

## Implemented

- `experiments/android_wide_slot_emitter.bf`: standard BF-owned 48-byte instruction slots for all eight commands, three-byte count, invalid-input and unrelocated-bracket statuses. Valid runnable slots currently require **no brackets**.
- `experiments/android_bounded_elf_wrapper.bf`: BF-owned extension of the historical fixed 4,192-byte ELF image to **74 instruction slots**, with native NOP fill, entry, exit, loader metadata and dynamic table all emitted from BF.
- `bootstrap/run_android_extended.py`: transport-only scanner/slot/ELF composition with strict framed-count/hash checks and atomic output replacement. **No Python instruction selection, binary emission or relocation.**
- Independent differential tests and machine-readable evidence at `evidence/iteration29_extended_slots.json`.

## Verification

The fresh test `tests/verify_android_extended_slots.py` passed **85** independent BF source cases on the AArch64 instruction simulator at **two load biases each**, including 58 expected deterministic pointer traps, 13 old-slot prefix parity comparisons, successful 74-command linear programs, wide-counter cases through 1,024 slots, six independent standard-BF interpreter checks, and rejection of six bracketed cases, three over-limit sources and three oversized wrapper frames. It confirmed both newly generated ELF stage binaries against exact commented and stripped BF source compilation using the canonical Linux-native BF compiler. The adapter preserved an existing artifact when rejecting input and successfully replaced it on a valid input.

Test cases use an independent reference Brainfuck interpreter, historical BF-owned AArch64 templates, the existing ELF structure, 6 independent BF-seed executions and CPU instruction simulation. A 74-command example additionally passed external `readelf -W -l` inspection (ELF64 AArch64 PIE, five headers, 16 KiB LOAD alignment). **No Android device or AArch64 process ran this iteration.** The 74-slot emission is real BF-origin machine code, but the ELF is still fixed-size. It is not a tested 300,000-command compiler.

## Unchanged and unverified

The canonical Linux source and executable have not been modified. This iteration reran Linux native Stage 1→2: both native recompilations reproduced the installed compiler ELF byte-for-byte. An independent cold Stage 0 was **not** rerun. Historical Linux bootstrap evidence is preserved and no independent cold-bootstrap proof is claimed from the new stage test. Fresh replay evidence: [`../evidence/iteration29_linux_native_replay.json`](../evidence/iteration29_linux_native_replay.json). The existing ten-slot loop-capable pipeline is retained separately. The wide matched-bracket and 26-bit branch-word stages remain **disconnected** from runnable extended images. Windows PE, Android-native compiler execution, Android-native self-compilation, APK integration and Android OS/device tests remain unimplemented or unverified.

## Next gate

Integrate BF-owned wide bracket pairing and machine relocation **into a runnable extended ELF**, then remove the 74-command and 4,192-byte output ceilings with a general BF-owned dynamic ELF layout. Rerun the full Linux bootstrap and Android-on-device gates when the respective environments are available. The Android-first and Windows-second roadmap continues unchanged.

## Source compliance and platform release gate

| Item | Executed result |
|---|---|
| BF source purity | Both new stages contain only eight executable BF instructions; comment stripping gives byte-identical stage binaries |
| Extended slot BF instructions | 16,075; native Linux ELF 514,615 bytes |
| Bounded ELF wrapper BF instructions | 8,531; native Linux ELF 273,207 bytes |
| AArch64 linear images | 85 source cases × 2 load biases, including 58 trapped boundary cases |
| Independent Brainfuck seeds | 6 native-vs-interpreted record comparisons |
| Previous Android branch pipeline | 166 ELF compilations, 11 intentional rejections, 8 independent seed checks passed |
| Prior Android source scanner integration | 9 byte-identical images, 4 rejected inputs, and atomic CLI check passed |
| Linux native self-compilation | Stages 1 and 2 freshly byte-identical; independent cold Stage 0 not rerun |
| New Android hardware/OS executions | **Not run** |
| Windows target | **Not implemented** |
| 300,000 BF command compilation | **Not supported** by this ELF path |

The wide slot stage has only **53 executable BF instructions of headroom** under the current Linux compiler's per-input cap of 16,128; future changes may need a staged composition instead of growing this one file. This is a tooling and compiler-capacity blocker, not a semantic extension to Brainfuck.

The 74-command ELF demonstration SHA-256 is `2c095d047e9ae3430171a04073b169bf88c12de14566f3f98ff08518946654d1`. The immutable canonical Linux compiler source is `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`, and its ELF is `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8`.

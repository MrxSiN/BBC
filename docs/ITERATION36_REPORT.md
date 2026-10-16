# Iteration 36 — Verified 2,000-command Android loop relocation

**Classification:** Linux-native execution of standard-Brainfuck compiler stages and Linux-hosted AArch64 instruction simulation. **Not Android-device execution, not Android-native self-hosting.** The larger Android compilation milestone remains partial.

## Implemented

The existing [two-byte Brainfuck slot patcher](../experiments/android_wide_slot_patch_512.bf) was tested beyond its former 512-command envelope. Its loop-counter operations and patch table proved usable up to 2,000 slots in the currently configured 65,536-cell compiler tape, without changing that Brainfuck implementation. The opt-in [transport adapter](../bootstrap/run_android_extended.py) now selects the same BF-owned patcher for the six-class `--multiclass --tape-relocated --loops` path. The existing BF source scanner, 24-bit bracket matcher, wide branch encoder, slot emitter, ELF relayout, and AArch64 tape rebase continue to perform the compiler logic. Python validates framing, selected limits, provenance, and atomic file placement but does not generate AArch64 instructions or calculate branch relocations.

Run:

```sh
python3 bootstrap/run_android_extended.py examples/android_2000_loop_demo.bf /tmp/android_2000_loop.elf --multiclass --tape-relocated --loops
readelf -Wl /tmp/android_2000_loop.elf
```

The sample contains exactly 2,000 commands, including a transfer loop, and outputs hex `c8` in the Linux-hosted AArch64 simulator. The sample ELF is 98,400 bytes, with distinct RX and RW load segments and the writable tape rebased to the aligned address `0x18060`.

## Tested gates

- Focused [test suite](../tests/verify_android_wide_loops_2000.py): **39** source programs, **164** independently checked bracket pairs, **78** simulator executions at two load addresses; **31** programs above the previous 1,024-loop ceiling; **24** cases using rebased tape placement; one expected pointer trap.
- **Seven** expected rejections, including oversized/malformed sources and unchanged nonrelocated `--multiclass` limits; CLI output preservation on rejection.
- `readelf` accepts the large PIE header and load structure. The compiled BF patcher reproduced its previous installed native ELF from annotated and filtered source, and unchanged source/native hashes match the earlier evidence.
- Iteration 35 tape-rebase regression passed again: **34** programs and **68** simulated executions. Its old rejection fixture was adjusted because a 1,025-command loop source is now valid in the opted-in relocated mode. The historical Iteration 35 evidence was preserved.
- Fresh native Linux self-compilation Stage 1 → Stage 2 each regenerated the unchanged **475,703-byte** compiler byte-for-byte. See [Linux replay](../evidence/iteration36_linux_replay.json). Independent cold Stage 0 was not rerun.
- The independent 2,000-slot Brainfuck seed interpreter exited with a **75-million-step execution cap** (inconclusive). The longer legacy 512-slot full-suite replay also timed out (inconclusive). No passing claim is assigned to those attempts.

## Source and platform status

The authoritative Linux compiler source [`core.bf`](../compiler/core.bf) and all BF-owned backend implementations are unchanged. The implementation change is **a verified larger bound and integration**, not a newly invented machine-code engine. There are no new executable Brainfuck instructions and no Python compiler logic in the production path. The sample is **simulator-verified**, not Android-loader-verified. The earlier ten-command Android-device evidence is historical, not evidence for this 2,000-command path. Windows PE32+ remains unimplemented.

## Limits and next priority

The current bounded compilation contract is **2,000 linear or loop-containing commands with `--multiclass --tape-relocated --loops`**, with 255 maximum bracket nesting and 65,536-cell zeroed tape. Legacy writer modes retain their own limits. The 300,000-command generated-artifact goal, Android loader/device testing, native Android compiler execution and target-side S2 are still open. More extensive hostile-record validation and a complete compiler-tape safety proof remain open. The original 22-iteration roadmap remains a planning estimate, not a guaranteed remaining count.

**Next:** run representative large executables under an actual supported Android loader, then design further BF-owned ELF layout and relocation scaling without exceeding the tape or branch contracts. Native Android compiler self-hosting is the required acceptance gate before Windows begins.

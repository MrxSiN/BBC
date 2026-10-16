# Iteration 29 follow-up — wide AArch64 loop relocation in a bounded ELF

## Implemented

A new **2,389-instruction standard Brainfuck** stage, [`../experiments/android_wide_slot_patch.bf`](../experiments/android_wide_slot_patch.bf), consumes position-indexed AArch64 branch words from the existing BF-native wide matcher and encoder, and replaces the branch placeholders in the existing 48-byte BF-emitted AArch64 slots. All instruction selection, branch displacement calculation, slot patching, and ELF construction remain in `.bf`; the Python CLI only transports checked byte streams and atomically installs the final image.

`bootstrap/run_android_extended.py --loops <source> <output>` now enables the path. Without the opt-in flag, the previously verified linear-only path continues to reject brackets. The final BF ELF wrapper has **74 slots in a fixed 4,192-byte ELF PIE**. Programs with nested, sequential, or widely separated loops now run in the project AArch64 instruction emulator with complete eight-command semantics **for the tested cases**, but **not** yet on a real Android device with this new pipeline.

## Fresh verification

See [`../evidence/iteration29_wide_slot_patch.json`](../evidence/iteration29_wide_slot_patch.json). The new dedicated test includes:

- **85** programs simulated at **two different load addresses each**, including zero-trip loops, transfers, nested and sequential loops, pointer errors, and long branch spans within the bounded 74-slot layout.
- **390** bracket pairs independently checked for their final encoded native `B` target words.
- **8** invalid-bracket or over-limit sources rejected; **4** native-vs-independent BF seed execution comparisons passed.
- Unbranched programs match the original extended linear ELF path byte for byte, and an unsuccessful CLI request preserves the existing output.
- The new native Linux stage built from commented and filtered `.bf` source produced byte-identical ELF bytes.
- The prior extended linear 85-program AArch64 regression suite, V1 Android contract test, source-comment suite, and documentation checker passed.

These are **Linux native BF compilation-stage executions and instruction-level AArch64 simulations**. No new Android-device run, independent cold bootstrap, or native Android compiler self-hosting is claimed. **Fresh native Linux Stage 1 and Stage 2 recompilations** of the unchanged canonical compiler both yielded the installed 475,703-byte ELF byte for byte ([native replay evidence](../evidence/iteration29_loop_linux_selfhost_replay.json)). `readelf` accepted the new demonstration AArch64 PIE ELF layout, but loader inspection does not prove Android execution. The 300,000-command acceptance gate remains open.

## Open gates

1. Dynamic AArch64 ELF image sizing and code/tape placement; remove the 74-slot wrapper and its NOP padding without moving code generation into the host adapter.
2. Relocation-stage defensive validation for untrusted length/position data, compiler-owned bounded resources and large source streams.
3. Actual Android loader execution and native self-compilation. Windows begins afterward.

**Iteration 29 status: PARTIAL.** The loop relocation subgate is executed on Linux; dynamic ELF layout and Android target execution are unverified. The 22-iteration baseline remains an estimate, not accomplished work.

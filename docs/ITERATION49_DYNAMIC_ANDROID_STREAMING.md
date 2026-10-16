# Iteration 49 — dynamic Android compiler stages

## Delivered

The standard-Brainfuck AArch64 **linear slot emitter** and a generic byte-framing/atomic-output transport now stream source and output without preallocating a slot table or enforcing a fixed command count. A caller-specified resource quota can stop output deterministically, leaving an existing artifact unchanged.

The source retains exactly eight executable Brainfuck instructions and validated ignored comments. It filters ignored raw source characters, accepts arbitrary raw bytes (including NUL), and rejects `[` and `]` until BF-owned relocation integration is complete. The new source has **15,805 instructions**, and is independently compilable using the unchanged Linux-native BF compiler. It emits exactly the older BF stage's 48-byte templates for all six linear instructions.

## Executed checks

- 132 differential program cases, including comment and binary input text
- Four independent Brainfuck seed interpreter comparisons
- Six unsupported-bracket rejection cases
- A real source with **300,001** linear BF commands and **14,400,048** generated AArch64 machine-code bytes (raw slots)
- Atomic preservation on bracket rejection and caller-configured output exhaustion
- Native Linux reproduction from commented and filtered `.bf` source
- Repeated native slot byte comparisons against a previously established BF-owned emitter

## Regression and provenance

- Fresh Linux native self-compilation from Stage 1 to Stage 2 reproduced the unchanged installed 475,703-byte compiler byte for byte
- Android V1 source and executable contract checks passed
- All eleven Android application policy records remain validated but **not compiled**
- Source comment and documentation consistency checks passed
- No new Android hardware test was performed; the separate archived bounded Android S2 remains historical evidence

## Exclusions

No runnable new Android ELF was generated or loaded. The 100M native output target, full eight-command dynamic backend, dynamic bracket stack, scalable native branch relocation, `ET_DYN` builder, Android JNI shared libraries, all 11 app policies, and native 100M self-hosting are **NOT YET IMPLEMENTED**. The separate 100M source scanner and 32-bit bracket pairing tests remain unchanged. The previous complete Android ELF pipeline remains 2,719-command bounded. This iteration changes *streaming machine-code emission* only, not full native compilation.

## Next engineering gate

Wire the streaming source-to-code positions into BF-owned loop matching and relocations. Replace rigid 48-byte slots with compact encodings and BF-owned 64-bit ELF offset/layout, then compile the original GmailHideAds, TwitterHideAds and ThreadsHideAds policies and perform target-side APK/JNI parity testing. Source length should be governed by available resources and correct address arithmetic, not a release-specific command-count ladder.

See [the dynamic stage contract](../experiments/android_streaming_linear_slots.bf.notes.md) and [machine evidence](../evidence/iteration49_android_dynamic_stream.json).

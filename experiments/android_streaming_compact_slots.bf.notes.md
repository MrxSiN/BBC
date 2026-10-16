# Compact AArch64 raw code stage — Iteration 50

Authoritative stage: [`android_streaming_compact_slots.bf`](android_streaming_compact_slots.bf). Only the eight standard Brainfuck operations execute. The adjacent source authoring Python script is development-only and does not run during compilation.

- Source SHA-256: `e0815353994c2db4b758d024055b95424495dc4e2ed71fbd242ada961e52c900`.
- Filtered BF SHA-256: `214af28340aa79e83e4b630c8dce4daa13de088094fbd7048c44c617d535bb90`.
- Executable BF instructions: **5,764**.
- Linux-native BF stage: [`../build/android_streaming_compact_slots_x86_64_linux.elf`](../build/android_streaming_compact_slots_x86_64_linux.elf) — **184,663 bytes**, SHA-256 `89f5761995e32f083c8ef3391a059d10d822d7c476143fc28338c253f94aa3c0`.

## Interface and verification boundary

A losslessly framed raw-source transport sends presence marker and original source byte to the Brainfuck program. The BF stage classifies six linear instructions and writes length-prefixed raw AArch64 code bytes. It rejects brackets; its output is **not** a loadable ELF or a full eight-instruction compiler. Per-instruction code lengths are 12 bytes for arithmetic, 28 bytes for pointer movement, 40 bytes for output and 48 bytes for input. The existing BF-owned AArch64 slot sequences remain byte-identical after removal of trailing NOP padding. The host copies opaque code bytes into an atomic file and enforces optional resource quotas. At 1,000,000 consecutive additions, output is 12,000,000 bytes; this is not an optimization of repeated additions and does not prove practical compilation of arbitrary mixed-source or original application BF programs. Run `python3 tests/verify_android_compact_stream.py`.

**Non-claims:** no new Android loader execution, no JNI-loaded shared library, no general dynamic ELF, no long-distance native branch relocation, no original application policy compilation, and no full 100-million-command executable. Linux-native verification and test-oracle AArch64 simulation are labeled separately. See [Iteration 50 report](../docs/ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) and the corresponding `evidence/iteration50_*.json` reports.

# Android streaming linear AArch64 native slot stage

**Implementation:** `android_streaming_linear_slots.bf` — 15,805 standard Brainfuck instructions.

**Source SHA256:** `d4609f8c691608b48b6c54a3c933e9331502dfcc9e65e84d33d4bf809b179d5c`. **Filtered SHA256:** `f20aea487a1c08190978d0604cbf168313735e7cd1c4045997e4a54500ba0c0c`. **Native Linux stage SHA256:** `80f55180ce8aacd583ea095f6dfc71abe5efed2f4d233673cc26fab2a67b69ab`.

## Dynamic input and output

Input is raw source bytes, including ignored characters and binary zero. The transport sends two bytes per raw byte: a presence marker of one followed by the unchanged source byte. A final zero marker ends the input. Brainfuck performs every instruction test. The host does not filter, parse, optimize, or encode instructions.

For each linear BF operation (`+`, `-`, `<`, `>`, `,`, `.`), the BF stage emits the marker byte one and exactly 48 AArch64 code bytes. These templates match the preceding Brainfuck-owned wide slot emitter. An ignored source byte emits nothing. The final record is two zero bytes: terminator and success status. Brackets are rejected using nonzero status one. The transport places native slot bytes into an atomically committed output file; it never repairs or generates AArch64 instructions.

No command count, source table size, or slot-count bound is compiled into the new Brainfuck program. Its scratch state occupies a few fixed cells. File size grows as the stage emits bytes. The user may set an output-byte resource cap, but the default transport has no explicit source-count or output-byte cap.

## Limits

This emits **raw AArch64 machine-code slots, not a runnable Android ELF or JNI shared library**. It currently handles only linear operations. Existing loop pairing remains separate, the 255-depth pairing limit remains, and the existing complete AArch64 ELF generation path is still limited to 2,719 commands. Streaming source bytes is not enough to support arbitrary loop relocation, address layout, or Android application integration.

One command currently produces 48 bytes, so 100 million such commands would generate **4,800,000,000 bytes** before headers, relocations or tape data. The practical final compiler requires compact IR, optimization, long-branch veneers and 64-bit file layout. No finite machine can promise literally unlimited memory, addresses or disk space. Resource exhaustion must be diagnosed deterministically.

## Reproduction

`python3 tests/verify_android_dynamic_linear_stream.py`

`python3 bootstrap/android_dynamic_linear_transport.py example.bf -o native-slots.bin`

The test reproduces the stage with the canonical self-hosted Linux compiler from both commented and filtered source, validates 132 programs against the earlier BF-owned slot bytes, and verifies a 300,001-command linear source producing 14,400,048 native code bytes, with no native image or Android device execution claimed. Evidence: [Iteration 49](../evidence/iteration49_android_dynamic_stream.json).

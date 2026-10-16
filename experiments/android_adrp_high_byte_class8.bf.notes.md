# Android eight page class carry correction

The authoritative [standard Brainfuck stage](android_adrp_high_byte_class8.bf) operates on a **trusted BF-generated** AArch64 ELF PIE. The adapter calls it only for **2,379 through 2,719 executable instructions**, where the RX segment occupies less than `0x20000` bytes and the next aligned RW tape segment starts at `0x20000`. The complete input ELF is exactly **131,168 bytes**.

The preceding BF tape-rebase stage handles six size classes. In the eighth class it drops three carries: the third byte of RX `p_filesz` (offset `0xd2`), RX `p_memsz` (offset `0xda`), and the second byte of startup `ADRP x20` (offset `0x201`). The new BF program consumes all 131,168 bytes and replaces only these three bytes with `0x01`. It emits the corrected ELF followed by two zero status bytes. All other bytes, including literal zero values, pass unchanged. The host checks record sizes and preconditions but does **not** patch ELF headers or generate machine instructions.

The stage uses standard Brainfuck `,` and `.` to copy the first 514 bytes, then two counted loops of 255 × 256 bytes and a final 94 bytes. Source comments contain no executable Brainfuck instructions. It assumes exact upstream framing and is **not** a standalone validator for untrusted truncated ELF input.

For this class, the expected AArch64 startup encoding becomes `14 01 00 90`, describing `ADRP x20` to the writable segment at RVA `0x20000`. Both RX length fields carry `0x01` into their third byte. The earlier `0x1c000` tape class and all preexisting ELF instruction slots remain unchanged. The next class begins at 2,720 commands and is intentionally rejected; the current writer, tape rebasing, and checked relocation contract have not been validated above this bound.

Execute `python3 tests/verify_android_class8_2719.py`. The test recompiles both annotated and filtered source with the Linux-native self-hosted BF compiler, compares against an independent BF interpreter, checks exact ELF headers/branch targets, and simulates generated AArch64 programs at two different image load addresses. Real Android-device execution is **not** rerun and the 300,000-command goal is **not** achieved.

## Source integrity

Source SHA-256: `841dbe8a2f67758f9ab5b9c61e3a5b3c652a024933fafa4e7c03440fbd2591f0`. Filtered instruction SHA-256: `9353049f111ecbfe488ea76ce3f7a4159c02b568b7c7d41b6987ebc6629fb9fd`. Linux-native BF stage SHA-256: `36bd1b9014628349b72d29d9e88f133b3c952aa1046cc9b34a8abef3c957a489`. This stage contains **2,787** executable Brainfuck instructions.

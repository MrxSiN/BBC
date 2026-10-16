# A standard Brainfuck 32 bit pairing stage with a bounded 255 frame stack and deterministic reject statuses

Iteration 48 Linux native executed evidence is [here](../evidence/iteration48_android_100m_pairing.json).

Source SHA-256: `edffda9342c8a69384701edba697dc488ec3ba4dd09044b81ee38fd1258b4905`  
Filtered instruction SHA-256: `c2db5ff4804cbdbef368ed0c73480c10fe9a31286db86d75c6c6d6a88c5346e5`  
Compiled ELF SHA-256: `deded49433bfd80d24cfa03d7d93395bfdd41593e7d11a5a82ec0402f78e5004`  
Instruction count: **2,017**.

## Protocol

The framed scanner accepts the generic run transport from Iteration 47 and emits zero or more five byte bracket occurrence records consisting of the bracket byte and unsigned 32 bit zero based command offset. It then emits a zero marker and the original nine byte count depth status trailer. It is a separate opt in Brainfuck source; the original scanner and its unchanged nine byte footer remain available.

The pairing stage accepts that framed scanner output and emits a nine byte record for each closing bracket: closing tag followed by the matching unsigned 32 bit opening and closing command positions. Output ends with zero marker and status byte. Status zero means balanced, status one means malformed or unmatched, status three means nesting stack overflow. This stage uses tape cells only up to the documented fixed stack region; maximum supported simultaneous nesting is 255. The host transport does not identify Brainfuck commands, match brackets or compute source offsets.

## Evidence and limits

The test suite verified 146 valid and 27 invalid streams, 173 parity cases against the original scanner, six comparisons against independent Brainfuck interpreters, and a real 100,000,002 byte file containing a loop around 100 million increments. Nesting depth 255 passed; depth 256 was rejected. Source compression makes a uniform run small and does not imply adequate throughput for diverse 100 MB programs. No AArch64 instruction encoding, executable ELF construction, JNI shared library, Android device execution or native self hosting was performed by these two stages.

Reproduce with `python3 tests/verify_android_100m_bracket_pairs.py` from the repository root.

# A standard Brainfuck 32 bit source event emitter with a zero byte separating bracket events from the nine byte trailer

Iteration 48 Linux native executed evidence is [here](../evidence/iteration48_android_100m_pairing.json).

Source SHA-256: `c0bc82ae62d5f880164aa54a4f200e5b9b84c5f678f3619b52fd06c3dad9a13b`  
Filtered instruction SHA-256: `667ee7bc37b40495682b0b44788d64e79d2e8b2c7a13e56f5ead10ee899335fd`  
Compiled ELF SHA-256: `d7e91ed30150b1f9047035a1164bc4fcec1cb659f24a1d3b5d490303ab1d515c`  
Instruction count: **14,886**.

## Protocol

The framed scanner accepts the generic run transport from Iteration 47 and emits zero or more five byte bracket occurrence records consisting of the bracket byte and unsigned 32 bit zero based command offset. It then emits a zero marker and the original nine byte count depth status trailer. It is a separate opt in Brainfuck source; the original scanner and its unchanged nine byte footer remain available.

The pairing stage accepts that framed scanner output and emits a nine byte record for each closing bracket: closing tag followed by the matching unsigned 32 bit opening and closing command positions. Output ends with zero marker and status byte. Status zero means balanced, status one means malformed or unmatched, status three means nesting stack overflow. This stage uses tape cells only up to the documented fixed stack region; maximum supported simultaneous nesting is 255. The host transport does not identify Brainfuck commands, match brackets or compute source offsets.

## Evidence and limits

The test suite verified 146 valid and 27 invalid streams, 173 parity cases against the original scanner, six comparisons against independent Brainfuck interpreters, and a real 100,000,002 byte file containing a loop around 100 million increments. Nesting depth 255 passed; depth 256 was rejected. Source compression makes a uniform run small and does not imply adequate throughput for diverse 100 MB programs. No AArch64 instruction encoding, executable ELF construction, JNI shared library, Android device execution or native self hosting was performed by these two stages.

Reproduce with `python3 tests/verify_android_100m_bracket_pairs.py` from the repository root.

# android_compact_native_offset_ledger51 stage contract — Iteration 51

The standard BF stage reads framed source bytes, calculates 64-bit native word offsets with sixteen base-sixteen digits, emits bracket event positions, and tracks total code length. Its word-count scratch cell is outside the sixteen-digit ledger, correcting the prior experimental overlap.

Source SHA-256: `e52f7bdfd90bebbfe494f28a25b8e69ed2b88e89c955c5445b8d10cf10713b76`

Filtered instruction SHA-256: `29039c0ed0ba96d69e786e02c7edeeb8f23e1c6ccb1ce5df7a1d0d1d1db1951f`

Linux-native stage SHA-256: `45f63a54cb9a386719aa22331780e88d34ccd594195da3163627fbcc934a2862`

The source uses only the eight standard Brainfuck commands. Runtime Python tools act only as raw-byte framing and opaque output/stack storage, not instruction encoders or semantic compilers. **This is not an Android-loadable ELF.** Full AArch64 branch displacement encoding, patching, long-branch handling, and dynamic ELF layout are outstanding.

Run `python3 tests/verify_android_compact_reloc_stream.py`.

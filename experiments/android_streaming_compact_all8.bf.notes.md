# android_streaming_compact_all8 stage contract — Iteration 51

The standard BF stage emits compact native bytes for all eight Brainfuck commands. Bracket slots contain unresolved AArch64 direct branch words.

Source SHA-256: `af6cb5e40bcac60266d89ff1f4b59ba89e25bea2f625b4d04204163b932b2de5`

Filtered instruction SHA-256: `ccf85625cb520b73554f661c1fa30d0032de7a4fe0c942f709ed085d945579e3`

Linux-native stage SHA-256: `ca890fe15b6d26687dff51a9736c2d707d7964397ce3b1886b62d110b3df8d90`

The source uses only the eight standard Brainfuck commands. Runtime Python tools act only as raw-byte framing and opaque output/stack storage, not instruction encoders or semantic compilers. **This is not an Android-loadable ELF.** Full AArch64 branch displacement encoding, patching, long-branch handling, and dynamic ELF layout are outstanding.

Run `python3 tests/verify_android_compact_reloc_stream.py`.

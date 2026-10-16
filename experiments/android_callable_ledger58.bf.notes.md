# android_callable_ledger58 — source and ABI notes

This **authoritative standard Brainfuck** code is generated at development time by `tools/author_android_dynamic_callable58.py`. At production compilation time, only the compiled native BF stage classifies source bytes and emits/counts machine words. The author tool is not invoked by the transport.

- Source SHA-256: `78bc940b7e9e2ef9b10a3babf497464589c9db1b81a4a24a9f49934eb3ab1210`
- Filtered standard BF instructions: **10,978**
- Linux native BF stage SHA-256: `8f58cb7bda28e02d3df725884ae4e2689cfac99187a1e4f9fbb0b7c2348cf8fd`
- Stage executable: `build/iteration58_dynamic/android_callable_ledger58.elf`
- Input wire: repeated `(present=1, raw byte)` pairs; `present=0` ends the source.
- Output wire: `(tag=1 or 2, little-endian uint64 word offset)` for each bracket, then tag three plus final word offset and two status bytes.

No Brainfuck source extension, host-native assembler, or foreign-language optimizer is used in compilation. The compiler's BF tape must be allocated and initialized under the project's normative execution model. Long-range bracket pairing and relocation are provided by the existing BF-owned, disk-backed stages.

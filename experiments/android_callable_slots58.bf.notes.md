# android_callable_slots58 — source and ABI notes

This **authoritative standard Brainfuck** code is generated at development time by `tools/author_android_dynamic_callable58.py`. At production compilation time, only the compiled native BF stage classifies source bytes and emits/counts machine words. The author tool is not invoked by the transport.

- Source SHA-256: `ea7c8259237a33ea58b34badcbe2f91f562907033af3cfec08f2d6c382e9d5aa`
- Filtered standard BF instructions: **7,346**
- Linux native BF stage SHA-256: `b497f422420c923f8347bf18ef6d297513f9d72b7523ddbf676fa9095ee68436`
- Stage executable: `build/iteration58_dynamic/android_callable_slots58.elf`
- Input wire: repeated `(present=1, raw byte)` pairs; `present=0` ends the source.
- Output wire: `(tag=1, length, machine-code bytes)` per emitted source instruction, then zero tag and status zero.

No Brainfuck source extension, host-native assembler, or foreign-language optimizer is used in compilation. The compiler's BF tape must be allocated and initialized under the project's normative execution model. Long-range bracket pairing and relocation are provided by the existing BF-owned, disk-backed stages.

# Android 100 million command source analyzer — Iteration 47

**Evidence:** [executed Linux native BF stage](../evidence/iteration47_android_100m_source.json). Source SHA-256: `a3dc8fbd24be8f9c7f30e589e77cef8a75d624a5a899c7cc0f73080bd41b8177`. Filtered instruction SHA-256: `ea8dbff663cb607ad33e878fc52d2d5f5076c4c3c480605ba5948cf61297914c`. **14,880 original Brainfuck instructions**. This is one directly executable `.bf` program, compiled by the existing self-hosted Linux BF compiler. No Python/C optimizer or machine-code generator participates in this stage.

## What is now executable

The BF parser correctly counts source instructions with **unsigned 32-bit offsets**, tracks bracket depth, reports unmatched brackets, detects command-counter overflow, and optionally emits `[` and `]` events with 32-bit *zero-based* source positions. It consumes original source bytes via a **generic run-length byte transport**, not a pre-parsed BF instruction stream. Source recognition, bracket classification, address arithmetic, and event emission remain inside Brainfuck.

The Python transport only groups identical bytes, independently of their values: it sends a one-byte mode (0 for count-only, 1 for bracket events), zero or more 5-byte records (`uint32_le repeat_count`, `uint8 raw_byte`), then a zero `uint32_le` terminator. All raw bytes, including NUL and FF, are representable. Only the BF stage knows which eight bytes are commands. The adapter enforces an explicit 200,000,000-raw-byte maximum by default, validates transport framing, and spools data to temporary files. For event mode, a separate output-volume cap applies.

The BF response is zero or more event records (`[` or `]`, `uint32_le command_offset`) followed by a nine-byte trailer: `uint32_le filtered_command_count`, `uint32_le remaining_depth`, `uint8 status`. Status 0 = balanced; 1 = unmatched bracket or depth underflow; 2 = counter overflow. A nonzero status invalidates the result. **Transport compression never counts or skips Brainfuck instructions itself.**

## Evidence and limitations

- A real **100,000,000-byte** source file containing 100,000,000 `+` commands was read, generically compressed, then counted by the native BF stage. This is a real raw-file transport test; the stage processes its lossless RLE representation rather than executing 100 million per-byte interpreter steps.
- BF-owned position records for a loop spanning **100,000,000 commands** were emitted and checked. A 50-million-open/50-million-close repeated-bracket case and 32-bit counter overflow were checked in count mode.
- Independent seed BF interpreters matched the Linux native stage for a small representative source. The full byte stream is tested for comments, ignored bytes, nested loops, malformed loops, and frame parity.
- Tape memory is bounded to cells 0 through 33. The output stream may still grow linearly with the number of bracket events. The source stage does **not** construct bracket pairing, branch relocations, executable code, ELF shared libraries, or Android APKs.
- The existing Android AArch64 ELF codegen remains **2,719 executable commands**, and the separately verified Android-native compiler has a **16,128-command input ceiling**. This new source stage is not integrated into either production compilation path. It is not Android-device executed, nor evidence of 100-million-command native compilation.
- A compressed run of identical instructions is cheap; arbitrary byte mixes can generate nearly one record per byte and still require bounded disk and computation. Runtime for complex 100M programs and generated native output has not been measured.

## Reproduce

```sh
python3 tests/verify_android_100m_source_capacity.py
python3 bootstrap/android_100m_transport.py path/to/program.bf --bracket-positions
python3 tools/check_docs.py
```

**Next engineering requirement:** Replace fixed 48-byte AArch64 slots with a compact BF-owned streaming IR, 32-bit bracket pairing and relocation, a size-safe ELF/ET_DYN writer, and a byte-stream host ABI. Demonstrate actual executable output for all eleven original application policy files, then a genuinely compiled and executed 100-million-command unit. Do not mark the compiler universal based only on this scan.

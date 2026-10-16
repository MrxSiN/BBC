# File backed dynamic bracket stage — Iteration 50

Authoritative stage: [`android_dynamic_stack_pairs.bf`](android_dynamic_stack_pairs.bf). Only the eight standard Brainfuck operations execute. The adjacent source authoring Python script is development-only and does not run during compilation.

- Source SHA-256: `0b4df823b41fdf56a39d87a88e71aad364f075ba3467f559594be8e7f3e1ed25`.
- Filtered BF SHA-256: `b516666cfa4b3adc2ab8043fa28c9dd4d6b1314fb7b1b1ba3db85814715a5dc1`.
- Executable BF instructions: **1,576**.
- Linux-native BF stage: [`../build/android_dynamic_stack_pairs_x86_64_linux.elf`](../build/android_dynamic_stack_pairs_x86_64_linux.elf) — **50,647 bytes**, SHA-256 `6d24f15c70019ee88f035711175a9f784d2f01f7cd2d68f08173642b73e757ae`.

## Interface and verification boundary

The BF stage is a byte-level protocol client of a generic file-backed LIFO that stores eight-byte values. Brainfuck owns requests to fetch the next event, push an opening position, pop at a closing position, check stack emptiness, emit matched records, and reject malformed nesting. The host provides generic expanding file storage; it neither recognizes Brainfuck brackets nor chooses pairings. This stage requires the file-backed host protocol and is not a standalone one-shot byte filter. The stack has no fixed depth table; exhaustion of disk, address space or time remains possible. The source-level integration still uses the earlier 32-bit BF scanner, so **64-bit pair records do not establish 64-bit source scanning**. Run `python3 tests/verify_android_dynamic_stack.py`.

**Non-claims:** no new Android loader execution, no JNI-loaded shared library, no general dynamic ELF, no long-distance native branch relocation, no original application policy compilation, and no full 100-million-command executable. Linux-native verification and test-oracle AArch64 simulation are labeled separately. See [Iteration 50 report](../docs/ITERATION50_DYNAMIC_ANDROID_PROGRESS.md) and the corresponding `evidence/iteration50_*.json` reports.

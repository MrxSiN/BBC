# Iteration 51 — compact Android native code and dynamic bracket coordinates

## Result

**Integrated but still not a loadable Android executable.** Two new standard-Brainfuck stages produce compact AArch64 code for all eight BF instructions and accurate 64-bit native *word* positions for brackets. The existing standard-BF file-backed stack matcher consumes the bracket events and emits matched pair records. The new transport composes these BF stages and atomically writes a ZIP bundle containing `code.bin`, `pairs.bin`, and `manifest.json`. The branch machine words inside `code.bin` remain placeholders.

### Source ownership

- `experiments/android_streaming_compact_all8.bf`: 6,289 Brainfuck commands, compact native instruction templates for eight BF opcodes; each bracket occupies three 4-byte AArch64 words and requires relocation.
- `experiments/android_compact_native_offset_ledger51.bf`: 10,968 BF commands, native 64-bit **word** offset accounting over variable-length instructions. A bug in the earlier experimental ledger was corrected: its instruction-length scratch no longer aliases a counter digit.
- `experiments/android_dynamic_stack_pairs.bf`: unchanged dynamic bracket pairing; the host stores only generic opaque 8-byte stack words in an expandable file.
- `bootstrap/android_compact_reloc_stream.py`: host transport, source byte framing, opaque file writes, length consistency checks, quota/atomic ZIP placement; does not parse BF source or produce machine instructions, branch displacements or ELF headers.

### Executed verification

`python3 tests/verify_android_compact_reloc_stream.py` passed **86 accepted source cases**, including **7,502 executable commands** in one test, **1,025 levels** of bracket nesting, **1,901 matched pairs**, **five atomic rejection cases**, and **four independent Brainfuck seed interpreter stage comparisons**. The native Linux BF compiler reproduced both new stage binaries from canonical and filtered source. Code bytes were compared with the established BF-owned AArch64 templates; paired offsets were compared with an independent test-only source oracle. These are **unrelocated code comparisons**, not execution of the looped native code.

The new integrated route does not impose a fixed source-command slot tier. It still inherits the 64-bit native-word address range, an AArch64 direct `B` immediate reach constraint after patching, available disk/RAM/time, and pending machine-code relocation/ELF generation.

### Explicit non-acceptance

- No branch bytes patched by the BF pipeline, no loadable ELF or Android shared library produced by the new route.
- No AArch64 simulator/Android loader execution of the *new* looped code. The existing completed ELF route remains verified only through **2,719 commands**.
- None of the original 11 GmailHideAds/TwitterHideAds/ThreadsHideAds policies have been compiled by the new integrated route; no APK or JNI parity acceptance.
- Linux self-hosting remains unchanged; archived Android bounded native S2 is not universal compilation.

### Next implementation gate

Produce a compact AArch64 signed branch encoder stage within the **16,128-BF-command native compiler input limit**. It must consume matched native code offsets, reject out-of-reach direct branches, and emit patch words and locations as BF output. Then compose BF-owned dynamic ELF headers and startup/tape page placement; test on AArch64, compile original app BF files, and integrate JNI/APK/device tests.

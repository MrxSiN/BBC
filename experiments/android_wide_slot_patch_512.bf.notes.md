# Android 512-slot native BF branch patcher — Iteration 33

**Later verification (Iteration 36):** The same, unchanged standard-BF two-byte walker is now independently tested in the opt-in six-class `--multiclass --tape-relocated --loops` pipeline through **2,000 commands**. The original 512-command notes below are historical for Iteration 33; do not read them as the latest cap of this new mode. See [Iteration 36 report](../docs/ITERATION36_REPORT.md) and [evidence](../evidence/iteration36_wide_loops_2000.json). Other modes still have their original limits.

**Authoritative BF source:** [`android_wide_slot_patch_512.bf`](android_wide_slot_patch_512.bf). The six comment lines contain no executable BF characters, and the remaining source is ordinary eight-instruction Brainfuck. This stage does not use a high-level language, assembler, external linker or Python branch patching.

**Source SHA-256:** `2c31051982a0b9d030594d22392a2b71afbbfd610f29a1c845dea679f128b575`.
**Filtered instruction SHA-256:** `ee02e665a91488d2d87462b9423d2efe36bd2d84f8487d45339770443eaf9966`.
**Linux native ELF SHA-256:** `3f7902ea5dffd9673893f9fdadfa284ae51c872dd8abc9b10e8dc7bd8a5ab32a`.
**Size:** 2,848 BF instructions; 91,351 bytes of compiled Linux ELF.

## Wire contract

Input: `count16LE | records15 | 00 00 | 48*count native AArch64 slot bytes`. The verified upstream BF stages generate each 15-byte `] | opening_position24LE | closing_position24LE | opening_B32LE | closing_B32LE` record, and the BF slot emitter generates 48 machine-code bytes per BF instruction. This stage inserts each encoded branch word at slot offsets 8–11 and outputs `48*count` patched bytes followed by `00 00` status. The adapter validates count/frame lengths, upstream statuses, source bounds, hashes, and atomic file placement.

The table starts at tape cell 48. Each of its 513 addressable rows uses 12 cells: two moving position-counter bytes, one return sentinel, a patch-present flag, four machine-word bytes, a walking flag, an output continuation marker, and two scratch cells. One-based position counters travel between rows using only Brainfuck operations. The walk decrements low byte with an explicit high-byte borrow, so indices 256 through 512 do not wrap to their first-byte residues. Only reached rows are marked; an extra walk to `count + 1` terminates output streaming without preinitializing 512 table markers.

The branch records are applied directly in BF. During output, the patch flag replaces template bytes 8–11 and leaves the other 44 bytes of each slot unchanged. The page-class ELF writer then creates a 16,480-byte file for 0–330 commands or 32,864 bytes for 331–512 commands. No host-specific code or relocations are inserted by the Python adapter.

## Boundaries

The standalone stage trusts the preceding BF matcher/encoder and validated transport. It is **not an adversarial raw-record parser**; for example, direct forged records with zero or out-of-bounds positions are outside its contract. Stage slots and indices remain bounded to 512; source nesting is bounded to 255 in the BF-owned matcher, and the overall source limit is not 300,000. `--dynamic --loops` still caps at 255; the default fixed writer remains at 74. This new stage is selected only for `--page-class --loops` when command count exceeds 255.

The generated native images have been **simulated on Linux**, inspected structurally, and tested against a reference interpreter. Neither these images nor the compiler were executed on Android during this iteration. Android-native self-hosting and Windows PE32+ remain unimplemented.

Run `python3 tests/verify_android_wide_slot_512.py`; evidence is [`../evidence/iteration33_wide_slot_patch_512.json`](../evidence/iteration33_wide_slot_patch_512.json), and the engineering report is [`../docs/ITERATION33_REPORT.md`](../docs/ITERATION33_REPORT.md).

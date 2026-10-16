# Android 255-slot BF relocation patcher — Iteration 32

**Source SHA-256:** `8dc71763182990b482414fe142d8cba48073d01eede19c0876a09b29abdcf54e`. **Filtered instruction SHA-256:** `3fc2cf5397bf255a0d8eace355ec7132c9e68ada8ad40d46c0e4cf79b44a5cd3`. **Linux-native ELF SHA-256:** `97465721a2630cb549ef80371008003a443b8817a2bb487eeb70bb96a54db7c8`. The source contains **6,009 standard Brainfuck instructions** and the Linux-native binary is **192,503 bytes**.

## Why this exists

The preceding BF-native branch patcher reserved only 74 slot records. This variant extends that same verified tape layout to **255 slots**, using the original seven-to-fifteen-byte BF matching and branch encoding records. The canonical Linux `compiler/core.bf` has not been changed.

This is a separate executable Brainfuck stage, not an assembly file or host-language code generator. It receives **one count byte**, zero-terminated encoded 15-byte bracket records, and exactly `count × 48` AArch64 template bytes. It writes the patched 48-byte slots followed by two zero status bytes. Each loop patch occupies bytes 8–11 of the opening or closing 48-byte slot. All native instruction words are calculated in the upstream BF encoder and inserted by this BF program.

## Limit and trust boundary

The value 255 is a hard bound, not a source-size milestone. The adapter verifies source filtering, bracket metadata and pair output, status bytes, the total slot count and stage hashes. The patcher directly trusts those stages and is **not** a standalone arbitrary-blob validator. Position bytes above the first are ignored by this bounded variant; **any source containing loops above 255 commands is rejected before patching**. Do not feed raw untrusted patch records directly into it.

Select `--dynamic --loops` or `--page-class --loops` in `bootstrap/run_android_extended.py`. The old default `--loops` path still uses the 74-slot ELF writer and 74-slot patcher. With `--page-class`, linear sources may have 512 commands; loop sources may have only 255. The boundary at 330→331 is proven only for linear programs, **not loop-containing programs**.

## Verification

Run `python3 tests/verify_android_wide_slot_255.py`. The current evidence has **68** reference-checked programs, **1,524** bracket pairs, **136** AArch64 simulator runs at two image biases, **5** expected malformed/oversized rejections, and **4** comparisons against two separately compiled Brainfuck interpreters. The commented and stripped BF code build the same Linux-native stage. Atomic failed-input handling is covered. Proof artifacts: [`../evidence/iteration32_wide_slot_patch_255.json`](../evidence/iteration32_wide_slot_patch_255.json) and [Iteration 32 report](../docs/ITERATION32_REPORT.md).

No current Android device execution, native Android compiler execution, Android S2 self-hosting, or 300,000-command program compilation has been demonstrated by this stage.

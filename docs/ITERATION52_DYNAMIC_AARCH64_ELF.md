# Iteration 52 — complete dynamically sized AArch64 ELF pipeline

## Result and execution boundary

A Linux-hosted, multi-process pipeline of **standard eight-command Brainfuck programs** now generates complete freestanding AArch64 **ET_DYN PIE ELF** files with eight-instruction source semantics and loop relocation. Unlike the earlier fixed 2,719-command ELF pipeline, this path streams compact code, stores bracket-pair records on disk, and grows the executable segment as required. The host only frames raw bytes, stores opaque four-byte native words at BF-supplied indices, copies BF-emitted code/headers, and writes fixed-layout zero padding. Runtime source classification, native AArch64 machine words, 64-bit offsets, bracket matching, branch displacements and ELF field values are BF-owned. It is **not** an Android DSO/JNI compiler, not an APK builder, and was **not executed by an Android kernel/loader**.

Verification: [`../tests/verify_android_compact_dynamic_elf52.py`](../tests/verify_android_compact_dynamic_elf52.py) checked 55 generated programs by two-bias AArch64 instruction-level simulation (110 runs), including 1,165 BF-matched bracket pairs, 29 expected tape traps and four atomic rejections. Native Linux compilation reproduced all six new BF stages from full and filtered source. [`../evidence/iteration52_android_dynamic_elf_tests.json`](../evidence/iteration52_android_dynamic_elf_tests.json).

A separate **synthetic**, not upstream-application, source with **296,307** commands and one enclosing loop compiled into a **3,686,784-byte** ELF in about 9.27 seconds. `readelf -Wl` passed. The synthetic source has the same instruction count as the largest surveyed ThreadsHideAds policy but is not its actual implementation. [`../evidence/iteration52_large_synthetic.json`](../evidence/iteration52_large_synthetic.json). This large ELF was structurally inspected, not simulated or executed on Android.

## BF stage contracts

| Standard BF source | Inputs and outputs | Host restrictions |
| --- | --- | --- |
| `android_streaming_compact_all8.bf` (I51) | Framed raw source to variable-length AArch64 instruction records | No source opcode interpretation |
| `android_compact_native_offset_ledger51.bf` (I51) | Same input to BF-owned 64-bit native word positions | Cross-check exact code length |
| `android_dynamic_stack_pairs.bf` (I50) | BF-controlled file-backed opening/closing stack | Opaque 8-byte push/pop storage |
| `android_compact_span64_52.bf` | 64-bit closing minus opening native word position; rejects borrow | Bytes forwarded between stages |
| `android_compact_branch_words52.bf` | Span to two signed AArch64 B words; enforces direct branch range | No host displacement calculation |
| `android_compact_patch_indices52.bf` | BF-owned bracket word index plus two and branch word records | Generic four-byte indexed storage at BF indices |
| `android_compact_elf_word_plus7_52.bf` | 64-bit native word count plus seven startup/exit words | Pass unchanged BF ledger size |
| `android_compact_elf_words_to_bytes52.bf` | 64-bit length times four; overflow rejection | No host field arithmetic |
| `android_compact_elf_header52.bf` | BF-generated ELF64 header, three program headers, startup and exit words | Copy and fixed zero gap only |

All six new stages have fewer than 16,128 BF instructions and compile with the unchanged canonical Linux BF compiler. Python source-authoring tools are development-only; the emitted BF stages, not Python, own all relevant compilation decisions at runtime.

Run `python3 tests/verify_android_compact_dynamic_elf52.py`. Compile an ELF with `python3 bootstrap/android_compact_dynamic_elf52.py input.bf -o output.elf`.

## Image contract

* ELF64 little-endian, AArch64 `ET_DYN`, entry RVA `0x20000`.
* Three `PT_LOAD` segments: read-only ELF headers at RVA 0; 65,536-byte zero-initialized writable tape at RVA `0x4000`; variable-length RX code at RVA/file offset `0x20000`.
* BF-generated four-word position-independent startup loads the constant tape page using a backward `ADRP`, sets X19 as the tape pointer, then enters compact code. BF-generated three-word Linux syscall exit sequence follows the user code.
* Source `><+-.,[]` semantics: 8-bit wrap, EOF-zero, pointer trap, binary Linux/Android syscall I/O, balanced loops. Host stdout is only compiler-process transport; generated ELF syscalls execute separately.
* Bracket slot comprises LDRB, conditional short skip, unconditional AArch64 B. BF-generated signed-26-bit direct-branch records patch the third instruction of each bracket slot.

## Outstanding acceptance gates

* A direct AArch64 `B` is limited to signed 26-bit **instruction-word** displacements. Out-of-range loops are rejected; **long-distance veneers are not implemented**. The pipeline is therefore resource-scaled but not unrestricted for every possible 100-million-command program.
* The 64-bit word ledger still has a representational ceiling. Resource exhaustion and caller quotas reject atomically. Compiler-stage sources remain subject to the 16,128-command canonical compiler limit, although user input is streamed independently.
* `ET_DYN` freestanding layout has passed `readelf` and Linux-hosted AArch64 instruction simulation, **not** actual Android loader acceptance, Android page/security policy compatibility, shared library linking, or the original eleven application BF policies.
* JNI/host frame semantics, persistent per-program tape (Threads core), callbacks, all original app program sources, parity tests, actual APK builds and native self-hosting with the new backend are pending.

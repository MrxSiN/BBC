# Brainfuck ELF PIE file size classes — Iteration 31 partial

**Authoritative experimental implementation:** [`android_page_class_elf_wrapper.bf`](android_page_class_elf_wrapper.bf). The source contains 9,909 executable Brainfuck instructions and safe ignored comments. Source SHA-256 `c583db5ed4a8ffe59145f51a049ba68f8029e27902dc232e250cba9c6e54509e`; filtered stream SHA-256 `e3b68890a5b8eaf710a09e217a408136afd5c842a5580a42a1ea5eb7e9382055`. The BF-compiled Linux executable is 317,303 bytes with SHA-256 `8bbb7be64b55fb385fd106d5370502f6a922560a8626abc459a9a50b221019e9`.

## Wire contract and tape layout

Input: **two-byte little-endian command count** in the documented bounded range `0..512`, followed by exactly 48 AArch64 machine-code bytes for each command. Upstream BF slot generation owns native instruction encoding. Output: a complete ELF PIE followed by the two zero-byte success-frame bytes. The adapter checks lengths and provenance. The BF writer generates the ELF header, segment records, static startup, calculated sizes, padding, exit code, and dynamic records. It does not parse source or apply branch relocations.

Internal tape cells 0–1 own the incoming two-byte count; 2–3 hold the calculated RX size; 4 holds a temporary size-class flag; 5 holds the writable segment file-offset high byte; 8 holds the input-byte scratch cell; 9 holds the output accumulator; cells 10–18 are bounded counters and scratch. The writer never buffers an entire ELF image in its tape. It consumes exactly the count announced by a trusted transport, including zero bytes in code slots. Because Brainfuck EOF is zero, **this standalone stage does not reliably reject a truncated, adversarial slot stream**. The host adapter must validate the slot frame.

## Layout and size thresholds

| Command count | RX bytes | RW file offset | RW virtual address | Total ELF bytes |
|---|---|---|---|---|
| 0–330 | `0x220 + 48n` | `0x4000` | `0x10000` | 16,480 |
| 331–512 | `0x220 + 48n` | `0x8000` | `0x10000` | 32,864 |

RX is read/execute; the separate tape-bearing `PT_LOAD` is read/write, **not executable**. The tape begins at virtual address `0x10060` and holds 65,536 zero-initialized cells. File and segment alignment is 16 KiB. The entrypoint at virtual address `0x200` uses AArch64 ADRP targeting the fixed writable page, then adds `0x60`. Its AArch64 word is emitted by the BF writer, not written by Python during compilation. This chosen fixed virtual address safely accommodates the stated range; it does **not** establish a general allocator for larger images.

At 330 commands, RX length is exactly `0x4000`, so the first file class still fits; 331 commands switches to `0x8000`. Calculating this transition and the corresponding padding inside BF is the new functionality. The input source limit of the *orchestrated pipeline* is 512 **linear** commands; the BF-owned existing loop patcher supports **at most 74 commands with brackets**. No larger-loop relocations, Android loader execution, on-Android compiler execution, or on-Android self-hosting are claimed.

## Verification

Run `python3 tests/verify_android_page_class_elf.py`. Evidence is in [`../evidence/iteration31_page_class_elf.json`](../evidence/iteration31_page_class_elf.json). Checks cover native Linux BF compilation from annotated/stripped variants, framing and count boundaries, independent source interpreter comparisons in the AArch64 simulator, multiple load biases, pointer traps, ELF program headers, rejection and output-file preservation. Independent cold Stage 0 and real Android loader execution are not included.

Python here is a testing and byte-transport tool. This `.bf` file and its BF compiled native Linux executable emit all production ELF bytes.

# Brainfuck AArch64 tape rebase and RX length repair — Iteration 35

The authoritative implementation is [`android_tape_rebase.bf`](android_tape_rebase.bf), a standard eight-instruction Brainfuck program. It executes as [`../build/android_tape_rebase_x86_64_linux.elf`](../build/android_tape_rebase_x86_64_linux.elf) after compilation by the existing Linux-native Brainfuck compiler. The Python adapter only transports copies of prior Brainfuck-generated ELF bytes, validates frames and places the output file.

**Source SHA-256:** `8ef1d311478a710bd491687250af1e80f64e893302e4d824004185dc0cd4982f`. **Filtered instruction SHA-256:** `14d034db66ce08d4e8408f5a492141aec20a3b08a6745c27d2544ca7bf472ed3`. **Linux-native ELF SHA-256:** `c9b8e16a2c3f24ff26d92ec65e433ca0199cddf4a2f13fd5fcfcdbbaee88a12d`. Source: **3,061** executable BF instructions. Native build: **98,167** bytes.

## Input and output contract

Input is a four-byte transport prefix copied unchanged from the intermediate ELF at offsets `0xF1`, `0xF2`, `0xD0`, and `0xD1`, followed by the complete intermediate ELF. The first two bytes are the significant part of the writable segment's file offset; the next two are the low bytes of the executable segment size. The adapter verifies the intermediate ELF length and source count before invoking this stage. This stage trusts that upstream validation; it is **not** an independent parser for arbitrary malformed ELF data.

Output is the full rewritten ELF image followed by `00 00` indicating transport success. No assembler, C compiler, host-side machine-code patching or linker is part of the production output path.

## ELF changes performed inside Brainfuck

- Compute the page count from the ELF's 16 KiB-aligned writable segment offset.
- Relocate both address fields in the writable `PT_LOAD` and `PT_DYNAMIC` records to the page-aligned file offset, making RX/RW virtual ranges nonoverlapping.
- Rewrite the low byte of the AArch64 `ADRP x20` instruction at offset `0x200` so that startup points to the relocated writable segment, then adds `0x60` to reach the tape.
- Repair the third size byte of both RX `p_filesz` and `p_memsz` when code reaches 65,536 bytes. The exact 1,354-command boundary is handled separately from later aligned classes.
- Copy all other header, machine code, padding and dynamic data bytes unchanged, using a BF-owned bounded streaming loop.

## Verified limits and layout

The opt-in command is `python3 bootstrap/run_android_extended.py INPUT.bf OUTPUT.elf --multiclass --tape-relocated`. Include `--loops` for bracketed programs **up to 1,024 commands**. The linear path accepts up to **2,000 commands**. This is a bounded partial compiler path; neither the 300,000-command target nor a generalized linker is implemented.

| Command range | File bytes | RW virtual address | Tape starts |
|---|---:|---|---|
| 0–330 | 16,480 | `0x4000` | `0x4060` |
| 331–671 | 32,864 | `0x8000` | `0x8060` |
| 672–1012 | 49,248 | `0xC000` | `0xC060` |
| 1013–1354 | 65,632 | `0x10000` | `0x10060` |
| 1355–1695 | 82,016 | `0x14000` | `0x14060` |
| 1696–2000 | 98,400 | `0x18000` | `0x18060` |

The tape is 65,536 zero-initialized 8-bit cells. Its segment has no execute permission. The calculation assumes a segment alignment of `0x4000` and a known AArch64 startup template. Additional page classes eventually require handling carries to more bytes of `ADRP`, wider executable length arithmetic and a larger slot patcher. A source exceeding the current limits is rejected, not silently truncated.

## Evidence and caveats

Run `python3 tests/verify_android_tape_rebase.py`. Results and hashes are in [`../evidence/iteration35_tape_rebase.json`](../evidence/iteration35_tape_rebase.json). This demonstrates Linux-native execution of the Brainfuck stage, structural ELF inspection and AArch64 instruction simulation at two load biases. It is **not Android loader execution**, APK support or native Android self-hosting. Independent cold Stage 0 was not rerun. A Linux native Stage 1→2 replay is recorded separately.

# Android four class ELF relayout in standard Brainfuck

**Authoritative executable source:** [`android_multiclass_elf_relayout.bf`](android_multiclass_elf_relayout.bf). This is a separate ordinary Brainfuck implementation stage. No Python, C, assembler, or linker writes the final ELF relocation or padding bytes. The existing Linux BF compiler builds its native Linux executable.

Source SHA-256: `d3adcf1e5578f91202f6f19430fb9f8954cac50ce4618834e962a7cc32908d42`  
Filtered instruction SHA-256: `f7d312b0b8daac149dfc40dd4acda23baa21e47018d930fcefdb3e46b812b67b`  
Native Linux ELF SHA-256: `34d599225aa8a1060c20614e98c7f51311826cbfa6f67ff7f992392ba9223955`

## Wire contract and responsibilities

The upstream Brainfuck slot emitter, bracket matcher, branch encoder and 512-name patcher provide machine-code bytes. The BF page-class writer provides a header, AArch64 startup, native slots, exit instructions, and 96 trailing dynamic/tape metadata bytes. The transport validates the upstream frames and passes this relayout stage:

`count16LE | first (0x220 + 48*count) bytes of upstream BF image | final 96 tape/dynamic bytes`

There is no host-side branch encoding or ELF header patching. The relayout stage reads and rewrites the two `p_offset` values, copies every native instruction byte, recalculates page-aligned padding and appends the metadata. It outputs `complete ELF image | 00 00`.

The header patch locations are `0xF1–0xF2` for the writable PT_LOAD offset and `0x129–0x12A` for the PT_DYNAMIC offset. All other header bytes are copied from the Brainfuck writer, including the correctly calculated RX `p_filesz` and startup code. BF computes the number of crossed 16 KiB pages using its own 8-bit tape arithmetic; the adapter's expected-length calculation is a framing assertion, not the ELF generator.

The old BF writer produces a deliberately **non-final staging image** for commands 672 onward. Its fixed RW p_offset and overflowing zero-padding are superseded by this stage. The transport selects only source/generated-code bytes and the BF dynamic trailer, removing the old padding. This framing must be trusted; this standalone BF stage is not a hardened adversarial-input parser. EOF-zero prevents reliable direct truncated-payload detection without additional transport framing.

## Output layout

| BF instructions | RX segment length | Writable segment file offset | Final ELF bytes |
|---|---|---|---|
| 0–330 | `0x220+48n` | `0x4000` | 16,480 |
| 331–671 | `0x220+48n` | `0x8000` | 32,864 |
| 672–1012 | `0x220+48n` | `0xC000` | 49,248 |
| 1013–1024 | `0x220+48n` | `0x10000` | 65,632 |

Each image is an Android-oriented AArch64 ELF PIE with RX and RW `PT_LOAD` segments. The tape remains fixed at virtual address `0x10060`; `0x10000` is its writable segment address. The RX segment ends at `0xC220` for 1024 instructions and cannot overlap the tape. This fixed tape address is **not safe as a general strategy for arbitrary larger programs**; beyond 1354 commands the executable segment can overlap it. The next expansion must move or redesign the tape relocation/entry setup.

## Tape region ownership

Cells 0–1: incoming two-byte command count. Cells 2–3: work countdown. Cells 4–5: current intra-page offset (low byte and 0–63 high-byte residue). Cell 6: page count. Cells 7–10 and 14, 17–18: comparison and copy scratch. Cells 11–12: two significant bytes of the rewritten page-aligned file offset. Cell 13: known zero output. Cell 15: current loop flag. Cell 16: inner offset advance counter. Cell 19: binary I/O byte.

Only BF operations update counters, copy the 48-byte native slots, write padding, and emit the complete artifact. The logic does not store the complete ELF on the BF tape. Program source and bracket nesting remain limited by the upstream stages. This file is the authoritative BF implementation, not a generated intermediate language.

## Verification and exclusions

Run `python3 tests/verify_android_multiclass_elf.py`. The test recompiles the commented and instruction-only BF streams with the existing native Brainfuck compiler, checks alignment and segment headers, compares emitted program bytes against a reference Brainfuck interpreter and Linux-hosted AArch64 simulator at two load bases, checks upstream 512-mode byte parity, invalid inputs, CLI atomicity and the four classes. See [`../evidence/iteration34_multiclass_elf.json`](../evidence/iteration34_multiclass_elf.json).

A separate seed-interpreter attempt on this byte-heavy relayout exceeded a 75-million instruction step limit, so independent seed equivalence is **inconclusive**, not passed. Cold Linux Stage 0, Android device loader execution, Android-native compiler self-hosting, and Windows native compilation are not proven here.

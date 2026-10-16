# Brainfuck native variable length AArch64 RX ELF stage — Iteration 30

**BF source SHA-256:** `1b593252999e6ba140b534f743da21293bb6d3d4b14a05d3e66c494e13f57fe4`. **Filtered instruction SHA-256:** `cc9c5cd7b82963b74b3605f3dd677b743da0a89fba8e2ad7956bbf9726f98bcf`. **BF instructions:** 9,087. **Linux-native ELF SHA-256:** `bffac9783a963502eddc12a34c6e22059c9720db6042bb48526a28736fb96251`. **Native executable:** 290,999 bytes.

## What this actually does

[`android_dynamic_elf_wrapper.bf`](android_dynamic_elf_wrapper.bf) runs as a Linux-native binary produced by the existing standard-Brainfuck compiler. It accepts one byte holding a command count of `0..255` followed by exactly `count × 48` BF-generated AArch64 slot bytes. It emits the complete ELF64 AArch64 PIE image followed by the two-byte `00 00` success frame. Source parsing and all machine instruction templates happen in other `.bf` stages. The Python adapter may check frame lengths and place files but does not calculate headers or machine code.

The BF-owned ELF writer computes the RX `p_filesz` and `p_memsz` as **`0x220 + 48 × count`**, using its own tape counters and carry propagation. This changes the *mapped executable length* for every count. It streams slots, emits a native exit sequence, then writes the required alignment gap and a 96-byte dynamic section. The final on-disk ELF is **16,480 bytes for every supported count**, because the second `PT_LOAD` begins at the next 16 KiB file-aligned offset. The program is therefore **not yet a general variable-file-size backend**.

| ELF part | Offset or address | Meaning |
|---|---|---|
| ELF headers and startup | File `0x000..0x20f` | PIE, AArch64 entry `0x200`, Android linker interpreter |
| Instruction slots | File `0x210..0x210+48n` | Exactly n BF-owned 48-byte slots |
| Exit code | File `0x210+48n..0x21f+48n` | Exit zero syscall followed by AArch64 NOP |
| File alignment gap | Through `0x3fff` | Zeroes, not mapped by the executable load segment |
| RW dynamic entries | File `0x4000..0x405f`, PIE RVA `0x8000` | 96 bytes, ELF `PT_DYNAMIC` |
| BF tape | PIE RVA `0x8060..0x1805f` | 65,536 zeroed RW bytes, non-executable |

The RX segment has `p_align = 0x4000` and the RW segment has `p_align = 0x4000`. The startup `ADRP` targets the new tape page at RVA `0x8000`; the dynamic tags still reference the unchanged ELF RX metadata at RVAs `0x180`, `0x198`, and `0x1a0`. All such bits are emitted by **standard BF**, never by host-side ELF patching during compilation.

## Capacity and trust

- Use `python3 bootstrap/run_android_extended.py source.bf output.elf --dynamic` for 0..255 **linear commands**. `--dynamic --loops` still uses the earlier bounded BF-only patcher for **up to 74 commands containing brackets**. Do not silently use placeholders for longer loops.
- The native slot source has 16,075 instructions, near the Linux compiler's 16,128-instruction limit. This ELF stage is separate rather than extending that source.
- The transport must supply exactly the announced number of bytes; V0 EOF-zero input cannot reliably detect a truncated binary slot stream. The BF stage's `00 00` record reports success only for **trusted correctly framed input**. It is not a standalone hostile-wire validator.
- No 256-plus code images, page-class switching, large-loop relocation, Android OS loader/device execution, or Android-native compiler/self-hosting is established by this stage.

## Evidence

Run `python3 tests/verify_android_dynamic_elf.py`. It compiles annotated and filtered BF source to identical Linux native images; checks **all 256 counts**, 79 independent linear sources, six bounded loop cases and **170 simulator runs at two PIE load bases**. It also checks two independent BF interpreter outputs, six expected rejections, the CLI's atomic output policy and `readelf` program headers. Linux compiler Stages 1–2 are separately recorded in [`../evidence/iteration30_linux_selfhost_replay.json`](../evidence/iteration30_linux_selfhost_replay.json). These results are **EXECUTED on Linux** and **SIMULATED AArch64**, not executed on Android hardware. See [`../evidence/iteration30_dynamic_elf.json`](../evidence/iteration30_dynamic_elf.json).

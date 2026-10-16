# Iteration 30 — aligned Android ELF code length, partial

## Implemented

The new authoritative experimental stage `experiments/android_dynamic_elf_wrapper.bf` contains **9,087 standard Brainfuck instructions**. It emits Android AArch64 ELF PIE headers, variable executable segment lengths, native slots, exit instructions, 16 KiB alignment padding and a separate non-executable 65,536-cell tape. The Linux-native stage binary is **290,999 bytes**, compiled using `compiler/core.bf`'s native self-hosted Linux executable. No other language is used for the production ELF construction or code generation.

`bootstrap/run_android_extended.py --dynamic` now accepts **up to 255 linear commands** compared with the fixed wrapper's 74. The old path is unchanged. `--dynamic --loops` retains **up to 74 loop-capable commands** through the prior BF patcher. Combined larger-source loops are explicitly rejected. `--dynamic` is opt-in and does not alter the old default.

## Verified in this environment

- **79** new linear image source cases; **6** bounded-loop images; **170** AArch64 emulator runs at two simulated load addresses; **62** expected pointer traps.
- **256 of 256** count values validated for calculated RX `p_filesz`, `p_memsz` and trailing file alignment.
- **2** independently implemented Brainfuck interpreter outputs agree with the native BF stage on the tested seed input.
- **6** malformed or unsupported source inputs rejected; failed CLI output install preserves existing file.
- `readelf` parses the PIE and its separate RX/RW loads. The ELF dynamic section remains 96 bytes.
- Previous iteration regression suites passed: 85 extended linear programs, 85 wide-loop programs, 166 historical bounded Android images, Android V1 protocol checks, and source-comment tests.
- Linux native self-compilation Stages **1→2** produced the installed **475,703-byte compiler byte-for-byte** again. No cold Stage 0 was rerun.

## Important limits

The output file still occupies **16,480 bytes for every 0..255 count**, because the ELF load segments must retain the declared 16 KiB alignment. Only the RX **mapped segment length** varies. The next step must handle additional 16 KiB **file-size classes** and BF-owned general relocations beyond 74 commands. The downstream large source capacity target is **300,000 executable commands**, not achieved. **Android device execution of the new image, Android native compiler execution, Android self-hosting, and Windows support remain unimplemented or unverified.**

## Source compliance and dependencies

The compiler core and all ELF/codegen stages remain standard raw Brainfuck. Python is used only for file transport, scaffolding development/tests, reading evidence and independent checks; C programs are independent BF interpreter test seeds. No GCC/LLVM assembler or linker participates in BF-owned production compilation. Host Linux's ELF loader runs the previously BF-compiled native stages. This stage trusts the supplied binary slot length; the adapter enforces framing and maximum supported source capacity.

## Next engineering priority

1. Extend the BF-written ELF planner to change 16 KiB **file offset/virtual address classes** when code grows beyond this window; update startup ADRP from BF values; test count 256 and cross-boundary execution.
2. Extend BF-owned bracket relocation and patching beyond its 74-slot table, with adversarial validation; run larger nested loops.
3. Execute generated images on Android emulator/device, and later build the native Android compiler and self-hosting stages. Windows remains next after Android acceptance.

See [`../evidence/iteration30_dynamic_elf.json`](../evidence/iteration30_dynamic_elf.json), [`../evidence/iteration30_linux_selfhost_replay.json`](../evidence/iteration30_linux_selfhost_replay.json) and [`../experiments/android_dynamic_elf_wrapper.bf.notes.md`](../experiments/android_dynamic_elf_wrapper.bf.notes.md).

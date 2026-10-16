# Iteration 31 — partial Android file size class expansion

**Status: PARTIAL.** A standard Brainfuck ELF writer now creates two aligned AArch64 PIE file-size classes in the Linux-hosted compilation pipeline. It supports **up to 512 linear commands**, compared with 255 in the preceding opt-in writer. Existing loop-capable construction remains capped at **74 commands**, and the Android-device/native-compiler requirements are not yet met. This bounded size-class subtask does not complete Iteration 30 dynamic ELF generality or Iteration 31 Android runtime/I/O acceptance gates in the roadmap.

## Implemented

- `experiments/android_page_class_elf_wrapper.bf`: 9,909 executable BF instructions. Two-byte count, BF arithmetic for the executable segment size, two 16 KiB file layout classes, separate non-executable writable tape, fixed safe tape RVA `0x10060` and stream output of BF-created ELF headers, bytes and padding.
- `build/android_page_class_elf_wrapper_x86_64_linux.elf`: compiled by unchanged Brainfuck-only Linux native compiler, no external machine-code generator. `--page-class` is opt-in in `bootstrap/run_android_extended.py` and checks immutable stage provenance. The old `--dynamic` and default pipeline remain available unchanged.
- Tests: `tests/verify_android_page_class_elf.py` checks the boundary at 330→331, both file lengths, ELF load declarations, simulator behavior under two load bases, bounded loops, malformed inputs and atomic CLI installation.

## Evidence from this execution

- **78 linear** source cases, **4 bounded-loop** source cases, **164 AArch64 simulated executions**, **13 direct count/format checks**, **5 expected rejections**, and independent reference interpreter comparisons.
- `readelf -Wl` accepted sample outputs with 0, 330, 331 and 512 commands. Exact image lengths are **16,480 bytes** through 330 and **32,864 bytes** from 331 to 512.
- Native BF writer compiled from commented and instruction-only sources to identical Linux executables; **two independent C-based BF interpreter seeds** also produced byte-identical empty-program outputs from the source.
- Iteration 30 dynamic ELF suite, Iteration 29 wide-loop and extended slot suites, Android V1 contract, source-comment and documentation checks were rerun successfully.
- Fresh Linux native Stages 1→2 recompiled `compiler/core.bf` byte-for-byte into the installed **475,703-byte** ELF. Independent cold Stage 0 was **not** repeated.

## Known limits

The ELF stage trusts a correctly framed code-slot input; the transport validates it. Full BF-owned relocation beyond 74 commands is still missing. No new generated image was loaded by Android, and the compiler is not Android-native or self-hosted there. Windows remains untouched. The maximum verified generated input is now 512 **linear** commands, not the planned 300,000. The two size classes are a bounded implementation, not general-sized ELF emission. Benchmarks comparing generated programs with optimized C/Rust were not run during this slice.

## Next work

Prioritize BF-only scalable slot relocation and exact loop behavior beyond 74 commands; make file-class/RW-placement selection extend beyond 512 without fixed tape overlap. Test executable images with the Android loader on a device or correctly configured emulator, and continue toward complete native self-hosting. Preserve the Linux and 74-loop regressions.

Evidence: [`../evidence/iteration31_page_class_elf.json`](../evidence/iteration31_page_class_elf.json), [`../evidence/iteration31_linux_selfhost_replay.json`](../evidence/iteration31_linux_selfhost_replay.json) and [`../experiments/android_page_class_elf_wrapper.bf.notes.md`](../experiments/android_page_class_elf_wrapper.bf.notes.md).

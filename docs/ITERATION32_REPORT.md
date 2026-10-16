# Iteration 32 — BF-owned loop patching through 255 commands

**Status: PARTIAL.** This iteration adds the next tested relocation capacity class, not the planned complete Android compiler. The canonical Linux compiler is unchanged. This work is separate from the archived Iteration 31 evidence.

## Implemented

- [`../experiments/android_wide_slot_patch_255.bf`](../experiments/android_wide_slot_patch_255.bf): **6,009** executable standard Brainfuck commands, with comment-safe in-source annotations. Its compiled Linux-native executable is [`../build/android_wide_slot_patch_255_x86_64_linux.elf`](../build/android_wide_slot_patch_255_x86_64_linux.elf), **192,503** bytes.
- [`../bootstrap/run_android_extended.py`](../bootstrap/run_android_extended.py): routes loop-containing sources through the 255-slot patcher only for `--dynamic` and `--page-class`, retaining the legacy 74-slot path by default. The host adapter transports and validates frames; it does not synthesize, relocate or modify AArch64 instructions.
- Existing BF wide metadata, bracket pairing, branch-word encoding, 48-byte slot generation and PIE construction are reused. No foreign compiler or assembler participates in native AArch64 code emission.

## Executed verification

- **68** programs passed against the independent Brainfuck reference, including transfer loops, nested loops, sequential brackets, byte I/O, pointer traps and 255-command boundary inputs.
- **1,524** bracket pairs checked against independently calculated AArch64 unconditional branch words; **136** simulator executions at two load biases matched expected output or pointer trap behavior.
- **4** independent Brainfuck interpreter comparisons, 2 native compiler source-equivalence builds (commented and stripped), **5** rejected unsupported/invalid programs and atomic output preservation passed.
- Existing Iteration 30 dynamic writer, Iteration 31 page-class writer and legacy 74-loop regressions passed in this environment. The 512-linear command path is unchanged.
- Fresh Linux native self-compilation Stages 1 and 2 produced the installed **475,703-byte** compiler byte-for-byte: [`../evidence/iteration32_linux_native_replay.json`](../evidence/iteration32_linux_native_replay.json). Independent cold Stage 0 was not rerun.

A 255-command demonstration is included as [`../build/android_wide_255_loop_demo.bf`](../build/android_wide_255_loop_demo.bf) and a **16,480-byte** [`AArch64 ELF`](../build/android_wide_255_loop_demo_aarch64.elf). It emits two zero bytes in Linux-hosted simulation at two load addresses and passes `readelf` header inspection. This is a generated-program sample, not an Android-native compiler.

## Current target envelope

| Pipeline invocation | With loops | Without loops | ELF size |
|---|---:|---:|---|
| Default `--loops` | 74 | 74 | 4,192 bytes |
| `--dynamic --loops` | **255** | 255 | 16,480 bytes |
| `--page-class --loops` | **255** | 512 | 16,480 or 32,864 bytes (depending on count) |

The 331-command transition is available to *linear* programs only. The largest loop-containing image has 255 commands, so it remains in the first ELF file-size class. The 300,000-command acceptance target is not reached.

## Limitations and next acceptance gate

This is a bounded patcher with a **one-byte input position/count representation** and trusted upstream records. It must be redesigned for two- or three-byte indices, then tested with loop sources crossing the 330→331 ELF file-size transition and 512-command limit. A scalable BF-owned instruction writer and relocation processor are also required for 300,000 commands.

The generated images were executed in Linux-hosted AArch64 instruction simulation and inspected by `readelf`; **they were not run through an Android loader in this iteration**. The BF compiler itself cannot run or self-host on Android yet. Windows PE32+ is not implemented. This is therefore not a completed Android compiler or roadmap Iteration 32 consolidation gate.

## Reproduction

```sh
python3 tests/verify_android_wide_slot_255.py
python3 tests/verify_android_dynamic_elf.py
python3 tests/verify_android_page_class_elf.py
python3 tests/verify_android_extended_loops.py
python3 tests/verify_source_comments.py
python3 tools/check_docs.py
```

Evidence: [`../evidence/iteration32_wide_slot_patch_255.json`](../evidence/iteration32_wide_slot_patch_255.json). Device execution and full release gate are **NOT EXECUTED**.

# Iteration 33 — 512-command Brainfuck loop relocation, partial Android milestone

## Implemented

- Added [`../experiments/android_wide_slot_patch_512.bf`](../experiments/android_wide_slot_patch_512.bf): **2,848 executable standard Brainfuck instructions**, compiled by the installed self-hosted Linux Brainfuck compiler into a **91,351-byte** Linux-native ELF. The 12-cell-per-slot BF table supports two-byte positions through 512, with a travelling count, borrow handling, sentinels, and byte-stream output. There is no C/Python native code generator or host-side relocation patch.
- Updated the opt-in [`../bootstrap/run_android_extended.py`](../bootstrap/run_android_extended.py) transport adapter. With `--page-class --loops`, loop-containing programs now reach **512 commands**, including the 330→331 ELF size-class transition. The default `--loops` path remains 74; `--dynamic --loops` remains 255.
- Retained BF-owned source scanning, 24-bit bracket pairing, signed 26-bit AArch64 branch words, 48-byte slot emission, and both 16 KiB aligned ELF file-size classes. The writer still uses `0x220+48*n` bytes of RX content with a separate RW tape segment.
- Updated historical test rejection fixtures because sources between 256 and 512 commands are now valid in the page-class loop mode. Historical evidence files were not rewritten.

## Executed evidence

- **66** source-program cases, **3,707** independently checked branch-pair relocations, **132** AArch64 simulator executions at two load biases, **44** programs in the 32,864-byte file class, and **1** verified pointer-boundary trap.
- **5** malformed or oversized source rejections, including nesting beyond 255 levels. CLI failed-output atomicity passed. A valid 512-command sample image emitted one zero byte at both simulated biases.
- **4** Brainfuck-interpreter comparisons across two independent seeds, plus native builds from both annotated and instruction-only source, produced byte-identical patch output/binaries. The independent seed comparisons cover short inputs; the wide input behavior is covered by Linux-native BF stage tests and simulator tests.
- `readelf` inspected the larger generated ELF. The prior Iteration 32 255-slot suite and Iteration 31 page-class suite passed with updated rejection cases, preserving their recorded historical evidence.
- Fresh Linux native self-compilation **Stages 1→2** produced the canonical **475,703-byte** compiler byte-for-byte; cold Stage 0 **not rerun**. See [`../evidence/iteration33_linux_native_replay.json`](../evidence/iteration33_linux_native_replay.json).

## Current target envelope

| Invocation | Linear commands | Loop-containing commands | ELF size |
|---|---:|---:|---|
| default `--loops` | 74 | 74 | 4,192 bytes |
| `--dynamic --loops` | 255 | 255 | 16,480 bytes |
| `--page-class --loops` | **512** | **512** | 16,480 bytes through 330; 32,864 bytes thereafter |

The production Linux compiler remains standard BF and unchanged. This project has **not** demonstrated general 300,000-command Android machine-code generation. The BF scanner and bracket matcher have separately processed larger streams, but the integrated Android ELF path is still bounded to 512 commands and 255 nesting levels.

## Known limits

- The new patcher trusts the upstream BF matcher and adapter framing; arbitrary direct malformed patch-record streams are not accepted as safe input. The adapter is transport, not an independent Brainfuck compiler.
- AArch64 execution was simulated in a Linux-hosted instruction engine; **the new Android images were not executed by an Android OS loader**.
- There is still **no Android-native compiler executable**, **no Android-native self-hosting cycle**, and **no Windows PE32+ emitter**.
- The ELF writer only supports two bounded file-size classes, with fixed startup assumptions; source and emitted-code scaling, relocation reach and tape placement need further engineering.
- A full clean cold bootstrap, Android device run, full release suite and formal proof of tape safety were **not executed** in this iteration.

## Reproduction

```sh
python3 tests/verify_android_wide_slot_512.py
python3 tests/verify_android_wide_slot_255.py
python3 tests/verify_android_page_class_elf.py
python3 tests/verify_source_comments.py
python3 tools/check_docs.py
python3 bootstrap/run_android_extended.py build/android_wide_512_loop_demo.bf /tmp/android512.elf --page-class --loops
readelf -Wl /tmp/android512.elf
```

Evidence: [`../evidence/iteration33_wide_slot_patch_512.json`](../evidence/iteration33_wide_slot_patch_512.json). This iteration resolves the **512-command loop and first page-class crossing** implementation slice, **not** the full Android-native compiler milestone.

## Next priority

Extend BF-authored file-layout and branch relocation to multiple aligned page classes and wider instruction counts without moving compiler logic into a non-BF adapter. Then execute representative generated binaries with a real Android loader and work toward native compiler execution and complete native self-compilation. Windows remains after Android S2.

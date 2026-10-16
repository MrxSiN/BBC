# Iteration 45 — Android ELF eighth page class

## Implemented

Returned to the Android target after the Windows Iteration 44 checkpoint. Added [`android_adrp_high_byte_class8.bf`](../experiments/android_adrp_high_byte_class8.bf), a **standard Brainfuck** stage that corrects three bytes in a *trusted* upstream BF-generated AArch64 ELF PIE when the writable segment moves to `0x20000`. At source counts **2,379–2,719**, the previous tape rebase lost one carry in each of `p_filesz`, `p_memsz`, and the `ADRP x20` startup instruction. The stage carries those values, preserves all other bytes, and emits a framed success result.

The transport-only Python adapter selects this stage for the new size class. It does not generate ELF headers, branch words or AArch64 machine instructions. The earlier <=2,378 paths and the 2,000-command sample remain bit-identical. This is a bounded improvement, not a redesigned scalable compiler.

Run the opt-in pipeline:

```sh
python3 bootstrap/run_android_extended.py examples/android_2719_loop_demo.bf build/android_2719_loop_aarch64.elf --multiclass --tape-relocated --loops
```

## Exact acceptance limits

| Property | New status |
|---|---|
| Instructions | All eight standard Brainfuck instructions |
| Max filtered source commands | 2,719 |
| Loop nesting | No more than 255 under the existing BF pair matcher |
| Default tape | 65,536 bytes, pointer checked |
| New ELF class | 131,168 bytes |
| New writable segment RVA | `0x20000` |
| Tape start RVA | `0x20060` |
| New startup word | `0x90000114` (`ADRP x20`) |
| Max raw source transport | 1 MiB |
| Input and output | Raw byte streams, EOF stores zero |
| Platform | Android AArch64 shell ELF PIE, not an APK |

## Verified and not verified

The focused suite passed **35 programs, 70 AArch64 simulator executions, 31 branch pairs, five expected rejections, and two pointer-trap programs**. The independent Brainfuck stage comparison executed 264,907 reference steps. The Linux-native standard-BF generation and AArch64 simulator suite tests the 2,000-command legacy boundary, the 2,037 and 2,378–2,379 ELF class boundaries, nested and long-distance bracket jumps, EOF, binary data, pointer traps, invalid input, and output-file atomicity. Generated images are loaded at two simulated base addresses; ELF segments and start instructions are checked. A second independent BF interpreter compares the new stage's 131,168-byte output with its Linux-native executable.

Evidence: [`../evidence/iteration45_android_class8.json`](../evidence/iteration45_android_class8.json) and [`../tests/verify_android_class8_2719.py`](../tests/verify_android_class8_2719.py). Fresh Linux self-compilation Stages 1 and 2 were byte-identical (475,703 bytes; see [`iteration45_linux_selfhost_replay.json`](../evidence/iteration45_linux_selfhost_replay.json)). Seven larger device acceptance fixtures are prepared but **NOT EXECUTED**, see [Android loader acceptance](ANDROID45_ACCEPTANCE.md). The independent cold Stage 0 was not rerun.

**Not run:** Android device execution of the newly enlarged images, 300,000-command compilation, 300,000-command Android-native self-hosting, APK packaging, and new cross-platform benchmark testing. Historic Android native S2 evidence applies only to the existing bounded native compiler input profile, and is not upgraded by these Linux-hosted tests.

## Next engineering blockers

1. Run the new size-class fixtures on an actual Android arm64 loader and retain exact output/status evidence.
2. Replace fixed 48-byte slot/table scaling with streaming, Brainfuck-owned multi-byte relocation and ELF construction that can reach beyond the current practical tape and two-byte index bounds.
3. Expand the Android-native compiler's documented input capacity beyond 16,128 commands, repeat native on-device self-hosting with the upgraded full compiler, and qualify 300,000-command ordinary source programs.
4. Retain all former Linux, Android and Windows behavior while performing those changes. Do not treat a Python adapter or an external compiler as the authoritative implementation.

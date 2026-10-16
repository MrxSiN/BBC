# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](../docs/ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Current Android BF compiler source — v3 archival audit

The authoritative source is now **14,727 source bytes**, **14,575 Brainfuck instructions**. Source SHA-256: `7dd565fad8860eb9b5be0a4b61f228fa6ba94803d78811bf26dc9c38fe90e17d`. The archived native compiler is **933,008 bytes**, SHA-256 `11782dea43d79697b248f164a1313ef5219e94105023c4456e4aa7ed28f1827c`. Four native stages were reported byte-identical on Pixel 8 Pro. See [current audit](../docs/ANDROID_NATIVE_S2_AUDIT.md). The older counts and hashes below belong to the previous v2 source, not the present source.

---

# Android native compiler notes

Source SHA-256: `b2c92a4d0684381b967fbe6d4df1d730e6d7540ed27f44cd45bac27226babfe5`

Filtered instruction SHA-256: `4eb4d0fefbc51c8adec97a8aab3de8d826aa138af7fdf27d20e41c46d85d7700`

`android_core.bf` is the authoritative Android target compiler. It has **14,584 source bytes**, **14,513 executable BF instructions**, and compiles itself into a **929,040-byte AArch64 executable**. The Linux target remains the unchanged `core.bf`. These are target implementations in the same eight-instruction language, not BF wrappers around another compiler.

The [recorded gate](../evidence/android_native_selfhost_20261013_v2/report.json) executed on Pixel 8 Pro, Android 17/API 37, with 4 KiB pages. Two independent BF interpreter seeds produced identical Stage 0 images. Stage 0 ran natively on Android and compiled the complete source to Stage 1; native Stages 1 and 2 produced Stages 2 and 3. All four images are byte-identical, SHA-256 `50c4d7b1fc206ff4c04ee41e00e279413e54c4d6e1ed4beb6a189e8345d078d3`. Native self-compilation takes about 4.2 seconds in this session. This is **bounded Android-native S2**, plus an additional reproducibility stage.

## Input and ownership

BF offsets **0:2462** reuse the canonical Linux decoder instruction stream verbatim. It accepts byte-stuffed input (`00→FF01`, `FF→FF02`, physical EOF terminates), discards every noninstruction, and retains at most **16,128** BF commands in four-cell records. The native adapter transports this byte stream; it does not filter source or generate code.

The decoder returns at pointer 60. The first retained source byte is at cell 68. Its pending error at cell 69 is moved to global cell 0 before scratch lanes are initialized. Cells 64–67 form the zero sentinel immediately before source records. A bracket-depth scan rejects unmatched brackets and depth 256 **before emitting any ELF bytes**. Nonzero depth is normalized to an error flag, so malformed wire plus 255 unclosed brackets cannot cancel each other by byte overflow.

| Compiler tape region | Role |
|---|---|
| 0 | Pending compiler error; final status |
| 1 | Successful-compilation guard; also temporary byte emitter |
| 2–3 | Global header/constant scratch |
| 10–12 | Three-byte exact ELF size |
| 14–15 | Retained command count |
| 16–23 | File-size arithmetic scratch |
| 64–67 | Source rewind sentinel and carried state |
| 68 + 4i | Retained source instruction i |
| Record lanes 1–3 | Carried depth/count or local scratch, depending on phase |
| Next record's lanes 1–3 | Borrowed scratch during matching/emission |

The canonical decoder's 16,128-command ceiling is retained. The extra record lanes remain below the 65,536-cell compiler tape in the tested maximum-size cases. This map explains the intended ownership; it is not a complete proof of every compiler path. All native BF pointer operations themselves remain guarded by the generated execution profile.

## Native image

Each image is a **freestanding ET_DYN AArch64 ELF** with two `PT_LOAD` headers, no interpreter, libc, dynamic linker or foreign runtime. The first 176 bytes are headers; startup occupies bytes 176–195; source slots begin at byte 196. The final exit sequence is 12 bytes.

```text
ELF bytes = 208 + 64 × retained_command_count
RX: file offset 0, RVA 0, exact file and memory size, read/execute
RW: file offset 0, RVA 0x200000, file size 0, memory size 65536, read/write
Both load alignments: 0x4000
```

The kernel zero-fills the tape. Startup uses PC-relative `ADRP` to establish its base. `x19` is the current pointer, `x20` the base, and `x21` the exclusive end. Every pointer move checks its bound before any subsequent access and exits 2 on failure. Byte arithmetic wraps at the byte store. Input returns zero on EOF; interrupted reads/writes retry with reconstructed arguments. Other input failures exit 4 and output failures exit 3. Normal exit is 0.

At maximum capacity the image is **1,032,400 bytes**, below 1 MiB, safely separated from the 2 MiB tape RVA. The maximum source slot separation also fits signed AArch64 `CBZ/CBNZ imm19`. The positive-capacity fixture spans the full accepted range and ran successfully on Android.

## BF-owned matching

The emitter temporarily zeroes the current bracket's source lane as a rewind marker. A forward/backward record walk carries a two-byte distance and one-byte nesting depth. It restores the bracket after returning to the marker. The branch word has low byte `E9`; BF computes the upper immediate bytes using doubled slot counts, signed negation and borrow. Opening brackets skip through the closing slot; closing brackets return to the body after the opening slot. Native corpus checks independently calculate both words, including maximum-distance and 255-depth fixtures.

Generic slots remain **64 bytes**, including NOP padding. This makes source-size and relocation arithmetic bounded and straightforward; it is not a general optimizer. The separate [compact stage](../experiments/android_compact_optimize.bf.notes.md) only replaces exact, proved small programs. It is itself compiled by this native BF compiler.

## Bootstrap boundary

[The gate runner](../tools/verify_android_native_selfhost.py) executes ordinary BF with the two existing independent seeds, copies bytes over ADB, checks trailing compiler status, and compares artifacts. Native Stages 1–3 execute **the generated Android compiler**, not an interpreter. Host removal of the single trailing status byte is transport framing; no instruction or ELF byte is repaired.

`build/author_android_selfhost.py` is development-only text authoring. It is not imported by the compiler adapter or used in native self-compilation. The saved raw `.bf` files own all runtime parsing, arithmetic, encoding and ELF construction. [The native adapter](../bootstrap/run_android_native.py) verifies source/image hashes, transports opaque streams and atomically places accepted output.

The gate passed **14** independently checked program executions and **7** rejections. It includes binary I/O, EOF, nested loops, depth 255, left/right tape traps, a 2,000-command program, maximum-size branches, malformed transport, depth overflow, and source overflow. The canonical Linux source and its archived S2 evidence are untouched; fresh Linux release gates remain unverified because this Windows environment has no Linux execution runtime. Broader Android/API/ABI coverage and 300,000-command support remain open.

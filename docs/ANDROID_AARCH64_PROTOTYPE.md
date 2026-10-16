# Android AArch64 PIE — bounded Brainfuck prototype

**Current-state notice (2026-10-13):** This is a **chronological prototype record**. Its original "not Android support" and "no Android device execution" claims describe Iterations 21–25 **before** the later 2026-10-12 device tests. The separate BF-owned ten-command pipeline **has subsequently run generated ELF programs on Pixel 8 Pro, Android 17/API 37**; [native optimization evidence](ANDROID_NATIVE_OPTIMIZATION.md) has the details. Android-native compiler execution, self-hosting, scalable sources and general app integration remain **UNIMPLEMENTED**. For planned milestones use [the roadmap](IMPLEMENTATION_ROADMAP.md) and [target matrix](TARGETS.md).

## BF-owned Android optimization — 2026-10-12

Two pure BF stages now fold clear/adjacent transfer loops and eliminate loader,
unused-slot and proven tape-allocation work. The transfer demo improves 4.57x
in same-run elapsed time and 364.10x in simulated native instruction count.
Its 2.3514 ms median narrowly leads the strongest C baseline's 2.3532 ms, but
the 95% interval includes a tie/loss: **surpassing the fastest is not proven**.
1,032 native BF runs and 1,542 BF/C/Rust byte/EOF checks passed.
The ten-command ceiling, Android compiler self-hosting and full applications
remain unresolved. GM's existing optimized policies were measured separately.
See [evidence, proof limits and reproduction](ANDROID_NATIVE_OPTIMIZATION.md).

This is the first Android-targeted code emitter, not Android support. The existing Linux compiler is still the only authoritative self-hosted compiler.

## Build and inspect

Run these commands on a Linux x86-64 host after verifying the original compiler.

```sh
python3 tests/verify_selfhost.py
python3 bootstrap/run_compiler.py experiments/android_aarch64_pie_subset.bf build/android_pie_emitter_linux_x86_64.elf
python3 tests/verify_android_aarch64_subset.py
printf '+++.' > /tmp/a.bf
python3 bootstrap/run_android_subset.py /tmp/a.bf /tmp/aarch64_test.elf
readelf -h -l -d /tmp/aarch64_test.elf
```

The host AArch64 emitter is 15,441 raw Brainfuck instructions plus safe ignored source comments. The existing Brainfuck compiler produces its Linux x86-64 executable; this executable emits AArch64 bytes. No assembler or high-level code generator is on the production route. The Python transport adapter validates the emitted status and source hashes, and atomically installs the image.

## Implemented boundary

- Source subset: `+`, `-`, `.`, `>`, `<`, `,`. Other executable BF symbols yield a nonzero final status. Ignored ASCII bytes work; NUL terminates input, so the source byte protocol is incomplete. At most 10 accepted commands.
- Binary output: **4,192 bytes of ELF64** plus a one-byte transport status. Status zero means the BF emitter accepted the source. Never install failed artifacts.
- ABI/layout: ET_DYN machine AArch64, entry 0x200, PT_INTERP `/system/bin/linker64`, five program headers including PT_DYNAMIC. RX segment at file offset 0; RW segment at file offset 0x1000 and virtual offset 0x5000. Segment alignment 0x4000.
- Tape: RW 65,536 zeroed bytes at virtual offset 0x5060. Pointer movement uses checked unsigned offsets and traps through `exit(2)` when it leaves the tape.
- Linker records: DT_HASH, DT_STRTAB, DT_SYMTAB, DT_SYMENT, DT_STRSZ and DT_NULL. Required because Bionic's linker validates presence of hash, string and symbol tables. Null symbol, empty string, SysV hash table with one bucket. No imported libraries.
- Native slots: 10 slots of 48 AArch64 machine-code bytes each. Increment/decrement compile to a byte load, word arithmetic and byte store. Output calls AArch64 `write` syscall and exits(3) if the call does not return 1. The output path does not yet retry EINTR. Termination calls `exit(0)`.
- No loops, complex relocations, source-size growth or optimizer yet. Input uses a direct byte read and EOF stores zero; `EINTR` retry is not implemented. Pointer movement is checked but not yet executed on Android.

## Evidence and what remains unverified

The local tests run the Linux-native BF emitter against two independent Brainfuck interpreter seeds, validate ELF headers and native instruction words, and simulate the supported AArch64 instruction stream under two load bases. The tests are deterministic and limited; they are **not an Android OS execution test**. See `../evidence/android_aarch64_subset.json`.

To prove target execution, run a generated ELF on an Android AArch64 shell environment with the `/system/bin/linker64` loader available, such as a properly configured emulator or rooted/debuggable device. A typical manual transfer for a device with shell execution support is:

```sh
adb push /tmp/aarch64_test.elf /data/local/tmp/aarch64_test
adb shell 'chmod 700 /data/local/tmp/aarch64_test && /data/local/tmp/aarch64_test'
```

That must be tested rather than presumed to work. Do not infer APK packaging, app sandbox access, or broad API-level compatibility. AArch64 Android targets require PIE from Android 5.0/API 21 onward. Modern Bionic linker behavior varies; actual loader rejection remains possible until on-device testing.

After an Android execution witness, extend this BF emitter with bracket matching and native branch patching. Only then evaluate integration into `compiler/core.bf` and native Android self-hosting. Windows remains a separate required target.

## Reference material

- [Android Bionic linker mainline source](https://android.googlesource.com/platform/bionic/+/refs/heads/main/linker/linker_main.cpp) — ELF and PIE enforcement.
- [Bionic dynamic linking implementation](https://android.googlesource.com/platform/bionic/+/master/linker/linker.cpp) — required DT hash and symbol/string tables.
- [Android NDK stable native API reference](https://developer.android.com/ndk/guides/stable_apis) — platform libraries and ABI context.

## Iteration 23 — checked pointer movement and byte input

The experimental emitter now accepts `+`, `-`, `.`, `>`, `<` and `,`, still only ten
commands per source. The native AArch64 `>` and `<` slots update register x19,
subtract the load-relative tape base x20, and use an **unsigned** comparison
against 65,536. An out-of-range pointer goes straight to `exit(2)` before any
subsequent tape access. AArch64 slot encodings were checked with Clang's
AArch64 assembler as an independent development oracle; the shipping image is
still generated only by the Brainfuck emitter.

The emitter has **15,441** executable Brainfuck instructions and generates a
**494,327-byte Linux x86-64 host ELF**. It was shortened by replacing long
fixed-byte arithmetic runs in the header with zero-restoring BF loops, using
scratch cell 3, and shortening the output slot encoding. The scratch cell's
zero-at-entry condition has runtime witnesses, not a complete formal source
ownership proof. The previous 14,771-command emitter and its native host ELF
are retained under `evidence/history/iteration22/`.

Native-image verification includes **110 accepted** programs and **15 rejected**
ones, two simulated PIE load bases, **four forced boundary-trap witnesses**
and **20 comparisons** with independent BF interpreters. The AArch64 images
for **128 legacy three-instruction programs** are byte-identical to Iteration
22's native emitter. See `evidence/android_aarch64_subset.json` and
`evidence/android_aarch64_legacy_equivalence.json`.

The `,` slot uses AArch64 `read` of one byte into the current cell. EOF
explicitly stores zero. Unexpected syscall returns exit with status 4; an
`EINTR` retry loop is still missing. Six EOF checks and two forced read
faults were executed in the simulator.

This remains STRUCTURAL / SIMULATED, not Android execution. The emitter still
has **no `[` or `]`**, no source input NUL, no general optimizer, and no
proof that Bionic accepts the image. The full Android compiler, Android-native
self-hosting, and support for the actual Gmail/Twitter/Threads policies are
not implemented. The existing Linux authoritative compiler is unchanged.


## Iteration 24 — bracket span stage (not yet target loop codegen)

The standard Brainfuck program in
`experiments/android_bracket_relocations.bf` now resolves properly nested
brackets in a prefiltered source stream of up to ten commands. It runs as a
**separate native Linux executable built by the self-hosted BF compiler**.
For every closing bracket it emits the matched loop span and the one-based
closing slot number. This suffices to calculate both AArch64 loop branch
displacements, including backward branches and nested loops. All parsing,
stack bookkeeping and span arithmetic in that stage are Brainfuck, not Python.

Its evidence covers 448 valid streams, 2,145 correctly rejected streams
(including exhaustive bracket-only inputs up to ten commands), and 44
independent interpreter agreement cases. The independent test also checks
that the implied conditional branch offsets fit AArch64 `imm19`. See
`experiments/android_bracket_relocations.bf.notes.md` and
`evidence/android_bracket_relocations.json`.

**This is not loop support in the Android ELF emitter.** The six-instruction
emitter and 4,192-byte output format remain unchanged. Source buffering,
metadata integration and actual CBZ/CBNZ emission are still missing. No
Android-native code was executed in this iteration.

## Iteration 25 — native AArch64 loop branches from Brainfuck

The experimental **six-stage Brainfuck-native pipeline** now generates the
AArch64 `CBZ` and `CBNZ` instructions for both brackets. This is target native
code, not an interpreter or a special ninth command. Each stage has raw `.bf`
source and a Linux-native ELF compiled by the verified Linux BF compiler.

The pipeline consists of:

1. `stream_filter.bf`: turns byte-stuffed source into the eight standard commands.
2. `android_bracket_relocations.bf`: calculates matching nested bracket spans.
3. `android_branch_encoding.bf`: produces actual AArch64 conditional branch words.
4. `android_branch_mask.bf`: assigns valid placeholder slots to loop commands.
5. `android_aarch64_pie_subset.bf`: constructs the base AArch64 ELF entirely in BF.
6. `android_branch_apply.bf`: replaces the reserved slots with the native loop code.

The Python entry point `bootstrap/run_android_loops.py` transports bytes and
installs the final artifact atomically; it does not select machine instructions,
parse loops, or perform relocations. The emitter's older six-command entry
point remains intact for historical byte-for-byte regression tests.

Each bracket slot begins with `LDRB W9, [X19]`. The opening branch is
`CBZ W9` to the first instruction after its matching closing slot. The closing
branch is `CBNZ W9` to the first instruction after the opening slot. A slot is
48 bytes, so a loop span of `s` commands yields `imm19` word displacements
`12*s - 1` forward and `12*(2-s) - 1` backward. The actual displacement
encoding, including negative 19-bit immediates, is performed by the
Brainfuck source. Every remaining instruction in a loop slot is an AArch64
NOP. An independent Python oracle **tests** the resulting bytes but does not
participate in generation.

```sh
python3 tests/verify_android_aarch64_loops.py
python3 bootstrap/run_android_loops.py examples/android_loop_demo.bf /tmp/android-loop.elf
readelf -h -l /tmp/android-loop.elf
```

The test suite executes the entire BF-native pipeline for 166 programs,
including 163 containing brackets. It checks the emitted instructions, checks
unmodified ELF bytes, compares execution with a separate BF interpreter at two
simulated PIE load addresses, rejects 11 malformed or oversized sources, and
runs eight selected stage comparisons against independent BF interpreter seeds.
All bracket-only balanced inputs of length at most ten were included.

**Limits remain significant:** maximum ten executable source commands, fixed
byte tape, Android-oriented ELF PIE, and a Linux-hosted adapter. No Android
loader or device execution was performed. Six separate BF executables are not
yet a native Android compiler, and they do not self-host on Android. The
fixed-size slot design also does nothing for the existing 0.9999x performance
goal or the four larger third-party application targets.

See `experiments/android_branch_pipeline.bf.notes.md` and
`evidence/android_loop_pipeline.json` for exact byte protocols and hashes.

# ⚙️ Native compile

> Brainfuck source in, Windows or Android executable out. One process, no Python.

`bbc.exe compile` turns Brainfuck into an Android ARM64 or Windows x86-64 program
using only native XAX code. No Python, interpreter or foreign compiler runs at any
step. BBC's Brainfuck passes, the BFX format and the fixtures are unchanged.

📎 XAX side: [COMPILE.md](https://github.com/MrxSiN/XAX/blob/841e6d8f85dca72b78ce35b92582642f6491c9c4/compiler/integration/bfx/COMPILE.md)

---

## 🚀 Use

Put `bbc.exe`, `bbc-android-arm64.xax` and `bbc-windows-x86_64.xax` in one
directory (for example ignored `build/`), then:

```text
build\bbc.exe compile android-arm64 -O1 program < program.bf
build\bbc.exe compile windows-x86_64 program.exe < program.bf
```

- O1 is the default. Source is raw binary stdin.
- Next to the executable you also get `<output>.xax` (the verified build snapshot)
  and `<output>.provenance`.
- On any failure all three files are deleted.
- `bbc bind` shows the intermediate binding record.

| Exit | Meaning |
|---:|---|
| 0 | Success |
| 1 | Invalid source |
| 2 | Resource limit |
| 3 | I/O failure |
| 4 | Usage or internal failure |
| 5 | The native backend rejects the program for that target |

---

## 🔗 Pipeline

Everything runs inside one `bbc.exe` process:

1. **Front:** `stream_chunks.bf` and `fold.bf` (O1), then the
   strict BFX decoder and importer. A small framing function turns the decision
   into one expected-root edit record.
2. **Edit:** binds the decision into the target's host build request.
3. **Resolve:** produces the build snapshot.
4. **Build:** verifies, lowers and packages.

`bbc.exe` contains the whole XAX driver and calls its entry once per step. Every
step verifies its own inputs; the edit record is never trusted. That driver is always XAX's
current production `xax_compiler_driver_general.xax` plus only the Windows hosting layer
(process entry, file I/O, lazily committed views). When the production driver changes,
`bbc.exe` is rebuilt from it and BBC's checks rerun ([rules](../AGENTS.md#-contracts)).

---

## 📱 Rebuilt after XAX ledger 0025 (2026-11-11)

XAX ledger 0025 keeps the copies of a branch that leaves a loop out of the loop in the ARM64 backend. `bbc.xax` was
rebuilt from the new production driver (31 min 49 s, root `eabd31c1…`) and XAX's self-built compiler built `bbc.exe`
from it (4 min 55 s, 36,319,744 bytes).

- **Checks on hardware:** 18 programs × O0/O1 for Android ARM64, built on Windows 11 and run on a Pixel 8 Pro:
  70 of 72 builds, 70 matching runs. The Wine and `qemu-aarch64` campaign was not rerun, and Windows outputs were
  not rechecked.
- **Speed:** mandelbrot 0.93×, factor 0.91× the cycles of the previous build
  ([benchmarks](08_BENCHMARKS.md#-android-arm64-on-a-pixel-8-pro-2026-11-11)).
- **`bbc.exe` crashes at start on real Windows 11** unless its header commits the stack
  ([XAX OI-56](https://github.com/MrxSiN/XAX/blob/main/XAX_OPEN_ISSUES.md)).

📎 [android_device_benchmark_2026-11-11.json](../evidence/android_device_benchmark_2026-11-11.json) ·
XAX side: [ADR-394](https://github.com/MrxSiN/XAX/blob/main/XAX_DECISIONS.md)

---

## 📐 Rebuilt after XAX ledger 0023 (2026-11-08)

XAX ledger 0023 made the number of values one function view may hold a run-time word instead of a constant in 18
driver functions (still 262,144; the compiler behaves exactly as before). `bbc.xax` was rebuilt from the new production
driver (root `1e253130…`) and `bbc.exe` from it (36,319,232 bytes).

- **Checks** (Wine 9.0, `qemu-aarch64`): 93 programs × O0/O1 × 2 targets, 372 builds and 488 runs matching an
  independent interpreter; the five error paths as before.
- **Hanoi at O0** still declines: its decision has about 620,000 values, and raising the capacity also needs larger
  XAX front-end regions, room for the tables and a new ARM64 liveness
  ([XAX OI-54](https://github.com/MrxSiN/XAX/blob/7f898cc/XAX_OPEN_ISSUES.md)).

📎 [production_driver_0023_2026-11-08.json](../evidence/production_driver_0023_2026-11-08.json) ·
XAX side: [COMPILE.md](https://github.com/MrxSiN/XAX/blob/7f898cc/compiler/integration/bfx/COMPILE.md) ·
[ADR-391](https://github.com/MrxSiN/XAX/blob/7f898cc/XAX_DECISIONS.md)

---

## 🪓 Importer branches before each offset access (2026-11-08)

XAX's importer inside `bbc.exe` now writes each ADD and MUL as two blocks: the address and its bounds test with a
branch to the off-tape status, then the access itself. The masked single block it replaces cost an x86-64 ADD 15
instructions; it is 8 now. BFX and the frontend are unchanged; a failing instruction touches no cell before it
reports off-tape (it touched cell 0, which is not observable after a failure either way).

- **Checks** (Wine 9.0, `qemu-aarch64`): 93 programs × O0/O1 × 2 targets, 372 builds and 488 runs; one O0 Windows
  run mismatched on an artifact byte-identical to one that passed before, and three reruns passed (a transient Wine
  run).
- **Speed** (Wine, median of 7): mandelbrot 1,198 → 1,092 ms, factor 63 → 60 ms, life 50 → 46 ms. The same
  constant fold for ARM64 measured no gain under qemu and was not applied.

📎 [importer_split_2026-11-08.json](../evidence/importer_split_2026-11-08.json) ·
XAX side: [importer_split/README.md](https://github.com/MrxSiN/XAX/blob/d5433c6/compiler/integration/bfx/transactions/production_driver/native/importer_split/README.md) ·
[ADR-389](https://github.com/MrxSiN/XAX/blob/d5433c6/XAX_DECISIONS.md)

---

## ⚙️ Rebuilt after XAX's constant folding (2026-11-08)

XAX ledger 0022 changed its x86-64 register lowering: arithmetic on constants folds into constants, so the
importer's offset and factor pool becomes immediates instead of spilled values, and a function now saves the
callee-saved register of every constant it hoists. `bbc.xax` was rebuilt from the new production driver
(17 min 36 s) and XAX's new seed built `bbc.exe` from it in 3 min 49 s (36,302,848 bytes).

- **Checks** (Wine 9.0 and `qemu-aarch64` on one Linux host): the same 93 programs at O0 and O1 on both targets,
  372 of 372 builds and 488 runs matching an independent interpreter; the five error paths exit 1, 4, 4, 3, 3 and
  leave no files.
- **Speed:** Windows executables only (the ARM64 backend is unchanged); see the
  [2026-11-08 benchmark](08_BENCHMARKS.md#-bbc-against-eight-compilers-after-constant-folding-2026-11-08).
- Hanoi at O0 still declines (XAX's graph limits).

📎 [production_driver_0022_2026-11-08.json](../evidence/production_driver_0022_2026-11-08.json) ·
XAX side: [COMPILE.md](https://github.com/MrxSiN/XAX/blob/fce1f35/compiler/integration/bfx/COMPILE.md#bbcs-driver-after-ledger-0022-constant-folding-on-x86-64--2026-11-08) ·
[ADR-388](https://github.com/MrxSiN/XAX/blob/fce1f35/XAX_DECISIONS.md)

---

## 🏗️ Built by XAX's own compiler (2026-11-07)

Current figures: [rebuilt after XAX's constant folding](#️-rebuilt-after-xaxs-constant-folding-2026-11-08).

`bbc.exe`'s driver is XAX's current production driver plus only the Windows hosting layer.
XAX rebuilds it with native transactions ([rebuild.sh](https://github.com/MrxSiN/XAX/blob/f57384a/compiler/integration/bfx/transactions/production_driver/native/rebuild.sh)),
and XAX's pinned compiler seed builds `bbc.exe` from it in about 5 minutes (35,964,416 bytes, after XAX ledger 0020).
The Python generic SDK no longer takes part.

- BBC's layer (entry, commands, compile front, exception handler) is taken from the previous
  `bbc.xax`, without its graph proof cache.
- XAX ledger 0019 was needed: BBC's compile front inlined more helper calls than one
  function view holds (2^18 values), so the inliner now stops at 2^17.
- XAX ledger 0020 fixed deep nesting in XAX's ARM64 backend: parameter aliases no longer
  rescan every edge per round, and the interval pool is sized from liveness.

📎 [production_driver_0020_2026-11-07.json](../evidence/production_driver_0020_2026-11-07.json) (after ledger 0020),
[production_driver_2026-11-07.json](../evidence/production_driver_2026-11-07.json) (after ledger 0019) ·
XAX side, after ledger 0020: [COMPILE.md](https://github.com/MrxSiN/XAX/blob/754dd41/compiler/integration/bfx/COMPILE.md#bbcs-driver-after-ledger-0020-deep-nesting-on-android-arm64--2026-11-07) ·
XAX side: [COMPILE.md](https://github.com/MrxSiN/XAX/blob/f57384a/compiler/integration/bfx/COMPILE.md#bbcs-driver-is-the-production-driver-built-natively--2026-11-07)

---

## ✅ Checks

On the `bbc.exe` rebuilt after XAX ledger 0020 (Wine 9.0 and `qemu-aarch64` on one Linux host):

- **93 programs** at O0 and O1 on both targets: 372 of 372 builds and 488 runs, all
  matching an independent interpreter in output bytes and exit code.
- The programs: pilot programs, BBC tests, both depth-512 programs, 16 negative loops,
  60 random programs and capacity cases.
- ✅ **Deep nesting on Android ARM64:** the depth-512 active-loop program builds (3.5 s at
  O0, 6.9 s at O1) and runs correctly; it declined before ledger 0020. The depth-512 program's
  Android build takes 0.5–0.7 s instead of 122 s.
- Error paths exit 1, 4, 4, 3, 3 and leave no files behind.
- mandelbrot at O0 and hanoi at O1, which used to decline, now build and match;
  hanoi at O0 still declines.

> ⚠️ Wine and `qemu-aarch64` are not real Windows or device execution, and these
> artifacts have not run on Windows 11 or a Pixel yet: status BLOCKED for device runs.

The previous `bbc.exe` (generic SDK, 2026-10-21) passed 83 programs, 332 builds and 588
runs ([native_single_process.json](../evidence/native_single_process.json)).

---

## 📉 Build time, step by step

Median complete Android build under Wine (seconds):

| Program | Python SDK | 4 processes | 1 process | Lazy views | Proof cache |
|---|---:|---:|---:|---:|---:|
| hello | 1.27 | 0.245 | 0.110 | 0.100 | **0.109**¹ |
| nested_math | 1.24 | 0.247 | 0.113 | 0.097 | **0.097** |
| checksum_four | 1.24 | 0.237 | 0.111 | 0.096 | **0.096** |
| deep_nesting_512 | 11.2 | 0.853 | 0.883 | 0.652 | **0.639** |

¹ Different runs on a shared host; compare columns of the same step only.

### 1️⃣ Native pipeline

The first version launched four processes (bind, edit, resolve, build). It was
5× faster than the Python path and produced identical artifacts.

### 2️⃣ Single process

`bbc.exe` absorbed the driver, so no helper processes start. Each driver step is a
variant whose final `ExitProcess` becomes `SetLastError`, so control returns to
`bbc.exe`.

📎 [native_single_process.json](../evidence/native_single_process.json)

## 💤 Lazy views

The driver used to commit 3.3 GiB of memory views up front. Now its 17 large
views, the 512 MiB importer arena and the 16 MiB record view are only
*reserved*. A vectored exception handler commits the touched 1 MiB slice on
first use, zero-filled, and resumes. Any other fault still ends the process.

| Program | Peak commit before | After |
|---|---:|---:|
| hello | 3,398 MiB | 67–98 MiB |
| deep_nesting_512 | 3,398 MiB | 117–131 MiB |

📎 [native_lazy_views.json](../evidence/native_lazy_views.json)

## 🧠 Graph proof cache

The three driver steps share most graphs, so each graph is now checked once per
compile. Before checking a graph a step looks up its CID:

- **Hit:** replay the recorded pointer extents, trap heads and acceptance.
- **Miss:** check it normally and record the result.

Object CIDs, type and constant checks and store-level checks still run in every
step. Typing time falls about 40%; whole builds get 3–7.5% faster.

Handing stores between steps in memory was measured first: file I/O is under
1 ms per step, so it wasn't worth doing.

📎 [native_proof_cache.json](../evidence/native_proof_cache.json)

---

## 🔧 Native backend change

Windows builds of large decisions (over 256 nodes, such as O0 hello or the
depth-512 programs) used to fail with `NATIVE-CALL-ARITY` `[5,4]`. One XAX driver
transaction ported the ARM64 elision of returned borrowed views to x86-64. All 141
existing driver stores keep identical results.

## 🐛 Bootstrap finding

The generic bootstrap's Windows backend lost scalar values carried across later
loops and calls. The `bbc.exe` entry works around it by keeping process scalars in
its own view and putting loops in small helpers. The driver itself is unaffected.

---

## 📚 Android shared libraries

`bbc.exe bind android-arm64` records also bind XAX's `bfc_call_v1` shared-library host, for
apps that load Brainfuck policies with `dlopen`:

```text
buildbc.exe bind android-arm64 -O1 < policy.bf > policy.edit
python -m xax_android_bfc policy.edit libpolicy.so
```

- The second step is XAX's generic SDK, run from its `compiler/src`; BBC's passes and BFX are unchanged.
- The library needs a 65,536-cell tape and ignores the instruction budget argument.
- **Not migrated** to the 2 GiB tape: records from the current `bbc` don't bind into it
  until its C ABI changes ([XAX SHARED.md](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/SHARED.md)).
- Nine YouTubeHideAds policies matched their previously shipped libraries on about 1.8 million
  calls on a Pixel 8 Pro.
- A native `bbc compile` shared-library target is not implemented.

📎 XAX side: [SHARED.md](https://github.com/MrxSiN/XAX/blob/52e8808/compiler/integration/bfx/SHARED.md)

---

## 📏 Where the time goes now

See [benchmarks](08_BENCHMARKS.md). In short: a small build is about 0.1 s, and a
Wine launch alone is about 43 ms of it. Lowering in the build step is the biggest
remaining cost.

📎 [native_compile.json](../evidence/native_compile.json)

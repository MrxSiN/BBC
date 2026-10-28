# 📊 Status

> What works today, what doesn't yet, and where the proof lives.

Updated **2026-10-29**.

---

## ✅ Working

| Area | State |
|---|---|
| **Compile** | `bbc.exe compile` turns Brainfuck into Windows x86-64 and Android ARM64 programs in one native process, no Python ([native compile](25_NATIVE_COMPILE.md)) |
| **Format** | One [BFX format](02_BFX_CONTRACT.md): magic `42 46 58 00`, id `01`. No fallback, no legacy decoder |
| **Levels** | O0 keeps primitives; O1 packs runs and folds safe clear loops. O2/O3 don't exist yet |
| **Correctness** | 83 programs × O0/O1 × 2 targets: 332 builds and 588 runs match an independent interpreter |
| **Competitors** | All 18 [benchmark](08_BENCHMARKS.md) programs give correct output |
| **Devices** | Earlier artifacts ran on a Pixel 8 Pro and Windows 11; new builds reproduce them byte for byte |
| **Self-hosting** | Three identical native own-source frontend generations on each target |
| **Tape** | 2,147,246,080 cells, committed as touched. A 130,050-cell walk runs natively on Windows 11 and on a Pixel 8 Pro at O0 and O1; both edges still fail at the first crossing ([XAX dynamic tape](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/DYNAMIC_TAPE.md)) |

**Limits:** fixed budgets, listed in [BFX budgets](02_BFX_CONTRACT.md#-budgets).

---

## 🚧 Not yet

- 🐢 **Generated code is slow on heavy compute.** Mandelbrot takes about 22 s
  vs 0.5–1.7 s for the competitors. Loop optimizations (affine, scan, offset) are missing.
- ⏱️ **Build time** is about 0.1 s for small programs under Wine; native competitors
  take 4–80 ms. Lowering is the biggest cost.
- 📱 **Android:** no off-main-thread worker for unbounded programs; no
  Android-hosted compiler. `bfc_call_v1` [shared libraries](25_NATIVE_COMPILE.md#-android-shared-libraries)
  build through XAX's SDK, not natively.
- 📦 **Windows DLL packaging** and common helper loading are open.
- 🐧 **Linux** is optional and not a target. Cross-compiling doesn't count.
- 🧩 **XAX OI-49** (large ARM64 composite returns) is open; the importer avoids it.
- 🏁 **Milestones:** M4 incomplete, M8 not achieved. No performance lead is claimed.
- 📏 **Fixed limits remain** on source (1 MiB), instructions (65,536), nesting (32,768),
  input/output (64 KiB), the importer's record view and the native driver: it declines
  mandelbrot at O0 on Windows and factor O0 and mandelbrot on Android, and its 40 MB file
  capacity. The tape edge is XAX's x86-64 bound encoding ([XAX OI-52](https://github.com/MrxSiN/XAX/blob/main/XAX_OPEN_ISSUES.md)).
- 📚 **`bfc_call_v1`** shared libraries aren't migrated to the wider tape.

---

## 📚 Evidence index

Each report is an immutable snapshot for the sources it names. Superseded reports
were archived outside the repo on 2026-10-28 and remain in git history.

### 🏁 Benchmarks

| Report | What it shows |
|---|---|
| [dynamic_tape_benchmark_2026-10-29.json](../evidence/dynamic_tape_benchmark_2026-10-29.json) | **Current.** Windows-native and Pixel before/after the 2 GiB tape, vs brainfry; raw samples |
| [competitor_benchmark_2026-10-22.json](../evidence/competitor_benchmark_2026-10-22.json) | BBC vs 8 compilers under Wine on Linux: 18 programs, build, run, size, RAM |
| [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) | Brainfly correctness, brainfry optimizer defects |

### ⚙️ Native compile

| Report | What it shows |
|---|---|
| [native_proof_cache.json](../evidence/native_proof_cache.json) | Each graph checked once per compile |
| [native_lazy_views.json](../evidence/native_lazy_views.json) | Peak commit 3,398 → under 140 MiB |
| [native_single_process.json](../evidence/native_single_process.json) | Driver inside `bbc.exe` |
| [native_compile.json](../evidence/native_compile.json) | Python-free source-to-executable path |
| [xax_alias_index.json](../evidence/xax_alias_index.json) | ARM64 alias scan via incoming-edge index |
| [native_android_lowering.json](../evidence/native_android_lowering.json) | All 22 Android snapshots, 47 Pixel runs |
| [android_hello_smoke.json](../evidence/android_hello_smoke.json) | 5,880-byte Android hello |
| [native_windows_lowering.json](../evidence/native_windows_lowering.json) | Windows pointer frames, byte arithmetic |
| [native_bits1.json](../evidence/native_bits1.json) | One-bit AND/OR/XOR lowering |
| [unified_compilation.json](../evidence/unified_compilation.json) | One public compile entry |

### 🧾 Format and frontend

| Report | What it shows |
|---|---|
| [canonical_bfx.json](../evidence/canonical_bfx.json) | Current BFX: decoder, importer, frontend, Mandelbrot |
| [stream_runs.json](../evidence/stream_runs.json) | Streaming run packer |

### 🗃️ Migration and cleanup

| Report | What it shows |
|---|---|
| [format_cleanup.json](../evidence/format_cleanup.json) · [repository_cleanup.json](../evidence/repository_cleanup.json) | Retired formats and files, archived outside the repo |

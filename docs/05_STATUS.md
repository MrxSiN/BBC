# 📊 Status

> What works today, what doesn't yet, and where the proof lives.

Updated **2026-11-07**.

---

## ✅ Working

| Area | State |
|---|---|
| **Compile** | `bbc.exe compile` turns Brainfuck into Windows x86-64 and Android ARM64 programs in one native process, no Python. Since 2026-11-07 `bbc.exe` holds XAX's current production driver and is built by XAX's own compiler ([native compile](25_NATIVE_COMPILE.md)) |
| **Format** | One [BFX format](02_BFX_CONTRACT.md): magic `42 46 58 00`, id `02`, END byte, no count field. No fallback, no legacy decoder |
| **Levels** | O0 keeps primitives; O1 runs [`fold.bf`](10_FOLD_OPTIMIZATION.md): offset instructions per straight segment, multiply and clear loops. O2/O3 don't exist yet |
| **Correctness** | 93 programs × O0/O1 × 2 targets: 372 of 372 builds and 488 runs match an independent interpreter under Wine and `qemu-aarch64` ([2026-11-07, after XAX ledger 0020](../evidence/production_driver_0020_2026-11-07.json)) |
| **BFX `02`** | 26 programs × O0/O1 on Windows: 52 builds and runs match; Android builds only (no device attached) ([fold_v2.json](../evidence/fold_v2.json)) |
| **Competitors** | All 18 [benchmark](08_BENCHMARKS.md) programs give correct output |
| **Devices** | Earlier artifacts ran on a Pixel 8 Pro and Windows 11. The 2026-11-07 `bbc.exe` makes different bytes and has not run on a device yet (BLOCKED) |
| **Self-hosting** | Three identical native own-source frontend generations on each target |
| **Tape** | 2,147,246,080 cells, committed as touched. A 130,050-cell walk runs natively on Windows 11 and on a Pixel 8 Pro at O0 and O1; both edges still fail at the first crossing ([XAX dynamic tape](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/DYNAMIC_TAPE.md)) |

**Limits:** fixed budgets, listed in [BFX budgets](02_BFX_CONTRACT.md#-budgets).

---

## 🚧 Not yet

- 🐢 **Heavy compute still trails.** With packed decision lengths (2026-10-31) the Windows
  backend keeps values in registers: Mandelbrot O1 takes 1.08 s (was 7.66 s) vs 0.33–0.93 s
  for the competitors, and large builds got slower (mandelbrot 0.57 → 1.30 s). Scan loops
  are not folded yet ([benchmarks](08_BENCHMARKS.md#-packed-decision-lengths-2026-10-31)).
- 📦 **Executables** shrank 5–8× with packed lengths (small programs about 8.6 KB); brainfry's
  are still 3× smaller.
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
  input/output (64 KiB), the importer's record view and the native driver: since
  2026-11-07 mandelbrot O0 and hanoi O1 build on Windows and, since XAX ledger 0020, the
  depth-512 active-loop program builds on Android ARM64, but hanoi O0 still declines (its
  decision exceeds XAX's 4 MiB graph-body view and 2^18 values per function view)
  ([native compile](25_NATIVE_COMPILE.md#-checks)). Factor O0 and mandelbrot on Android
  are not rechecked. The tape edge is XAX's x86-64 bound encoding ([XAX OI-52](https://github.com/MrxSiN/XAX/blob/main/XAX_OPEN_ISSUES.md)).
- 📚 **`bfc_call_v1`** shared libraries aren't migrated to the wider tape.

---

## 📚 Evidence index

Each report is an immutable snapshot for the sources it names. Superseded reports
were archived outside the repo on 2026-10-28 and remain in git history.

### 🏁 Benchmarks

| Report | What it shows |
|---|---|
| [competitor_benchmark_2026-11-07.json](../evidence/competitor_benchmark_2026-11-07.json) | **Current comparison.** BBC O0/O1 vs the eight pinned competitors, 18 programs, raw samples (Windows arms under Wine): no competitor beaten; same platform, run time 1.07× brainfry's Windows output, builds 72× |
| [old_new_benchmark_2026-11-07.json](../evidence/old_new_benchmark_2026-11-07.json) | Old `bbc.exe` (rebuilt from the previous `bbc.xax`) vs the natively built one, interleaved under Wine, 6 programs, raw samples: identical executables where both build; builds 1.0–1.8× slower; mandelbrot O0 and hanoi O1 now build |
| [baseline_benchmark_2026-11-05.json](../evidence/baseline_benchmark_2026-11-05.json) | **Current baseline.** BBC O0/O1 vs brainfry, bf-x86 and Awib on one Linux host (Windows outputs under Wine), 8 programs, raw samples; hanoi and mandelbrot O0 decline in the native backend |
| [packed_lengths_benchmark_2026-10-31.json](../evidence/packed_lengths_benchmark_2026-10-31.json) | Windows-native. Packed decision lengths: before/after vs brainfry and Awib, 18 programs, raw samples, 170 differential cases |
| [final_benchmark_2026-10-29.json](../evidence/final_benchmark_2026-10-29.json) | Windows-native run vs brainfry, Awib, pablojorge and Brainfly: 18 programs, O0/O1, raw samples |
| [android_device_benchmark_2026-10-31.json](../evidence/android_device_benchmark_2026-10-31.json) | Pixel 8 Pro runs of the current build: every built program correct; mandelbrot and factor O0 decline at build |
| [fold_v2.json](../evidence/fold_v2.json) | BFX `02` and `fold.bf`: Windows before/after, 52 verified builds and runs; raw samples |
| [dynamic_tape_benchmark_2026-10-29.json](../evidence/dynamic_tape_benchmark_2026-10-29.json) | Windows-native and Pixel before/after the 2 GiB tape, vs brainfry; raw samples |
| [competitor_benchmark_2026-10-22.json](../evidence/competitor_benchmark_2026-10-22.json) | BBC vs 8 compilers under Wine on Linux: 18 programs, build, run, size, RAM |
| [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) | Brainfly correctness, brainfry optimizer defects |

### ⚙️ Native compile

| Report | What it shows |
|---|---|
| [production_driver_0020_2026-11-07.json](../evidence/production_driver_0020_2026-11-07.json) | **Current.** `bbc.exe` rebuilt after XAX ledger 0020: 93 programs, 372 of 372 builds, 488 runs, error paths (Wine, `qemu-aarch64`) |
| [production_driver_2026-11-07.json](../evidence/production_driver_2026-11-07.json) | Previous: `bbc.exe` from XAX's production driver, built by XAX's compiler: 93 programs, error paths, build and run samples (Wine, `qemu-aarch64`) |
| [native_proof_cache.json](../evidence/native_proof_cache.json) | Each graph checked once per compile (previous `bbc.exe`) |
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
| [stream_runs.json](../evidence/stream_runs.json) | Retired streaming run packer (BFX `01`) |

### 🗃️ Migration and cleanup

| Report | What it shows |
|---|---|
| [format_cleanup.json](../evidence/format_cleanup.json) · [repository_cleanup.json](../evidence/repository_cleanup.json) | Retired formats and files, archived outside the repo |

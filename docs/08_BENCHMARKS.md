# 🏁 Benchmarks

> BBC against eight other Brainfuck compilers: build time, run time, file size and memory.

Run on **2026-10-22**. Lower is better everywhere.

📎 Raw data: [competitor_benchmark_2026-10-22.json](../evidence/competitor_benchmark_2026-10-22.json)

---

## 🪟 Native Windows and Pixel, before/after the 2 GiB tape (2026-10-29)

First Windows-native and on-device numbers. Windows 11 on a Ryzen 9 5900HS and a Pixel 8 Pro;
brainfry `e55d457` is the only competitor rebuilt so far. Medians of 15 interleaved trials;
every built program's output matched the reference interpreter.

📎 [dynamic_tape_benchmark_2026-10-29.json](../evidence/dynamic_tape_benchmark_2026-10-29.json)

| Windows x86-64 (ms) | BBC O1 build before → after | BBC O1 run before → after | brainfry build | brainfry run |
|---|---:|---:|---:|---:|
| Small programs (12, typical) | ~95 → ~46 | ~16 → ~16 | ~17 | ~16 |
| mandelbrot | 1,731 → 1,529 | 10,605 → 10,339 | 18 | 938 |
| life | 318 → 242 | 2,852 → 2,795 | 14 | 22 |
| factor | 343 → 263 | 910 → 909 | 15 | 58 |
| bottles | 385 → 304 | 18 → 17 | 14 | 25 |

| Pixel 8 Pro (ms) | BBC O1 build | BBC O1 run | brainfry run |
|---|---:|---:|---:|
| mandelbrot | ❌ declined (exit 5) | — | 1,240 |
| life | 520 | 855 | 89 |
| factor | 694 | 319 | 245 |

- 🔨 **Faster builds come from the rebuilt `bbc.exe`, not the tape.** Rebuilding the
  unchanged store gives the same ~2× faster small builds. The same rebuild raises peak
  build working set (about 10 → 16 MiB small, up to 122 MiB for Mandelbrot).
- 🏃 **Run time is unchanged** by the wider tape on Windows. Pixel run times vary up to
  1.6× between runs of the same brainfry binary, so their before/after deltas aren't
  significant.
- 📏 **Peak commit** of a generated Windows program stays at 1.6 MiB: the tape is reserved,
  not committed (eager commit measured 6,157 MiB).
- ⚖️ brainfry still wins every compute-heavy run and every build. No lead is claimed.

---

## 🥊 The short version (2026-10-22, Wine on Linux)

| | Winner | BBC |
|---|---|---|
| ⚡ **Fastest build** | bf-x86, brainfry (~4 ms) | ~0.1 s, 2nd slowest of 10 |
| 🏃 **Fastest program** | brainfry, bf-x86 (~2.4 ms small) | ~45 ms, which is mostly Wine startup |
| 🪶 **Smallest file** | bf-x86 (264 B small) | 15.9 KB small, 361 KB large |
| 🧠 **Least build memory** | bf-x86 (1.7 MiB) | 26 MiB small, 132 MiB large |
| ✅ **All correct** | 9 of 10 arms | BBC 18/18 ✅ |

- 🟰 **Same platform, same Wine:** BBC ties brainfry's Windows build on small
  programs (44.9 vs 45.3 ms run).
- 🐢 **Heavy compute is BBC's weak spot:** Mandelbrot takes 22 s vs 0.5–1.7 s for
  everyone else.
- 🐘 **Brainfly is the outlier on build:** 6.9 s per small program and 1.2 MB files
  (it publishes a .NET NativeAOT app).

---

## 🧪 Setup

| | |
|---|---|
| **Host** | Linux x86-64, Intel Xeon @ 2.80 GHz, 4 cores |
| **BBC** | `bbc.exe compile windows-x86_64`, then runs the `.exe`, both under Wine 9.0 |
| **Others** | Build and run natively on Linux x86-64 |
| **brainfry-win** | brainfry's `windows-x86_64` target under Wine: the fair same-platform check for BBC |
| **Trials** | 1 validation run, then 5 build and 5 run trials, interleaved, order rotated |
| **Stats** | Median per program, geometric mean per group |
| **Memory** | Peak RSS of the largest process (includes the launcher's ~1.7 MiB floor) |
| **Wine** | Persistent `wineserver`, like a running Windows host |

### 🔧 Competitors

| Compiler | Rev | Build mode |
|---|---|---|
| [Awib](https://github.com/matslina/awib) | `f9f43a0` | `@lang_c` → `gcc -O2` |
| [brainfry](https://github.com/DirazCoder/brainfry) | `e55d457` | `bfnative --target linux-x86_64` (and `windows-x86_64`) |
| [bf-x86](https://github.com/skeeto/bf-x86) | `3a2feb2` | Direct ELF output |
| [bflang](https://github.com/Kuree/bflang) | `612c8eb` | `--O1`, LLVM/MLIR 18 |
| [Brainfly](https://github.com/hez2010/Brainfly) | `2e1d1b5` | `build` → .NET 10 NativeAOT publish |
| [pablojorge/brainfuck](https://github.com/pablojorge/brainfuck) | `1539247` | Rust `translate c` → `gcc -O2` |
| [abfc](https://github.com/fcostin/abfc) | `ea8d26d` | Self-hosted BF compiler → `.s` → `gcc` |
| [Wilfred/bfc](https://github.com/Wilfred/bfc) | `2cd6a75` | LLVM 14 |

Tools: gcc 13.3, clang 18.1, rustc 1.97, .NET SDK 10.0.402, Wine 9.0.

### 📝 Programs (18)

- **Small (12):** hello, binary_echo, wrap, nested_count, transfer_repeat,
  multi_transfer, scan, nested_math, clear_set, permit_flag, countdown_actions,
  checksum_four.
- **Large (5):** mandelbrot, bottles, factor, life, sierpinski.
- **Floor (1):** an empty program, to show fixed startup cost.

---

## 📦 Small programs

| Compiler | ✅ | Build | Run | File size | Build RAM | Run RAM |
|---|---:|---:|---:|---:|---:|---:|
| brainfry | 12/12 | 3.9 ms | **2.3 ms** | 1.3 KB | 2.3 MiB | 1.7 MiB |
| bf-x86 | 12/12 | **3.5 ms** | 2.5 ms | **264 B** | **1.7 MiB** | 1.9 MiB |
| pablojorge | 11/12 | 61 ms | 3.2 ms | 16.1 KB | 27 MiB | 1.7 MiB |
| Wilfred/bfc | 12/12 | 77 ms | 3.3 ms | 16.1 KB | 66 MiB | 1.7 MiB |
| bflang | 12/12 | 63 ms | 3.4 ms | 16.1 KB | 71 MiB | 1.7 MiB |
| Awib | 12/12 | 57 ms | 3.4 ms | 16.1 KB | 25 MiB | 1.7 MiB |
| abfc | 12/12 | 16 ms | 3.4 ms | 13.6 KB | 4.6 MiB | 1.7 MiB |
| Brainfly | 12/12 | 6,851 ms | 5.7 ms | 1.19 MB | 193 MiB | 3.5 MiB |
| **BBC** 🍷 | 12/12 | 104 ms | 44.9 ms | 15.9 KB | 26 MiB | 6.6 MiB |
| brainfry-win 🍷 | 12/12 | 3.9 ms | 45.3 ms | 3.0 KB | 2.3 MiB | 6.7 MiB |

🍷 = runs under Wine. An empty program costs ~43 ms there, against ~2–3 ms natively.

## 🏋️ Large programs

| Compiler | ✅ | Build | Run | File size | Build RAM |
|---|---:|---:|---:|---:|---:|
| Awib | 5/5 | 217 ms | **9.5 ms** | 19.7 KB | 54 MiB |
| pablojorge | 5/5 | 316 ms | 10.5 ms | 19.7 KB | 69 MiB |
| bflang | 5/5 | 647 ms | 10.6 ms | 21.7 KB | 96 MiB |
| Wilfred/bfc | 5/5 | 257 ms | 10.7 ms | 23.3 KB | 70 MiB |
| brainfry | 5/5 | 4.3 ms | 13.8 ms | 15.4 KB | 3.0 MiB |
| bf-x86 | 5/5 | **3.6 ms** | 22.6 ms | **4.2 KB** | **1.7 MiB** |
| abfc | 5/5 | 132 ms | 29.5 ms | 32.0 KB | 5.1 MiB |
| Brainfly | 5/5 | 12,742 ms | 38.6 ms | 1.20 MB | 1,519 MiB |
| brainfry-win 🍷 | 5/5 | 4.7 ms | 98.5 ms | 18.1 KB | 3.0 MiB |
| **BBC** 🍷 | 5/5 | 506 ms | 289 ms | 361 KB | 132 MiB |

### ⏱️ Run time per large program (ms)

| Program | BBC 🍷 | brainfry-win 🍷 | Awib | brainfry | bf-x86 | bflang | Brainfly | pablojorge | abfc | Wilfred/bfc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mandelbrot | 21,954 | 1,677 | **481** | 1,622 | 792 | 1,056 | 1,549 | 922 | 1,280 | 1,006 |
| bottles | 48 | 61 | 3.3 | 10.8 | 10.7 | 3.3 | 15.8 | 3.4 | 14.5 | **3.1** |
| factor | 49 | 45 | 3.6 | **2.2** | 2.4 | 3.1 | 5.4 | 3.3 | 3.1 | 3.3 |
| life | 911 | 45 | **3.6** | 4.5 | 98.5 | 3.8 | 98.6 | 3.7 | 97.6 | 3.7 |
| sierpinski | 42 | 45 | 3.7 | **3.0** | **3.0** | 3.3 | 6.5 | 3.3 | 4.0 | 3.6 |

### 🔨 Build time and size per large program

| Program | BBC build | BBC size | Fastest build | Smallest file |
|---|---:|---:|---|---|
| mandelbrot | 2,468 ms | 1.40 MB | bf-x86 4.5 ms | bf-x86 14.5 KB |
| bottles | 556 ms | 403 KB | bf-x86 3.6 ms | bf-x86 5.3 KB |
| factor | 495 ms | 436 KB | bf-x86 3.4 ms | bf-x86 5.1 KB |
| life | 424 ms | 376 KB | bf-x86 3.7 ms | bf-x86 4.9 KB |
| sierpinski | 115 ms | 67 KB | bf-x86 3.1 ms | bf-x86 644 B |

---

## 🔍 What it means

- ✅ **Correct everywhere.** BBC passes all 18. The only failure in the whole run is
  pablojorge on nested_math: its tape is 30,000 cells and isn't zeroed.
- 🍷 **Wine eats BBC's run time.** On small programs BBC's code runs as fast as
  brainfry's Windows output under the same Wine. The ~40 ms gap to native Linux
  compilers is startup, not code.
- 🐢 **Loops are slow.** Mandelbrot (22 s) and life (0.9 s) show that BBC's
  generated code lacks loop optimizations: affine transfers, scans and offset folding.
  92% of Mandelbrot's samples are in generated code, not Wine.
- 📦 **Large programs make large files.** Every BF instruction becomes checked native
  code: 361 KB on average vs 4–32 KB for most others.
- 🔨 **Build is mid-pack.** About 0.1 s for small programs, after the Wine
  launch. That beats Brainfly and is close to the gcc/LLVM pipelines on large
  programs. Lowering is the biggest remaining cost.
- 🧊 **Cold Wine is expensive.** If `wineserver` isn't already running, each Wine
  process pays ~0.55 s extra. Those samples are kept in the evidence, but they
  aren't used in the tables.

### 🎯 Next steps

1. Loop optimizations in the BF passes (affine transfer, scan, offset).
2. Smaller lowering for checked accesses, so files and build time shrink.
3. Real Windows and device runs, without Wine.

---

## 📜 History

Earlier, narrower comparisons. Their numbers stay as recorded.

| What (newest first) | Doc | Evidence |
|---|---|---|
| Native compile (2026-10-21), ~0.1 s builds under Wine | [native compile](25_NATIVE_COMPILE.md) | [native_compile.json](../evidence/native_compile.json) |
| Brainfly correctness, brainfry defects | [analysis](09_BRAINFRY_ANALYSIS.md) | [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) |

How to measure fairly: [performance plan](06_PERFORMANCE_PLAN.md).

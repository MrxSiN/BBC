# 🧠 BBC — Ballsdeep Brainfuck Compiler

> A Brainfuck compiler written in Brainfuck, turning `.bf` files into native Windows and Android programs through [XAX](https://github.com/MrxSiN/XAX).

---

## ✨ What it does

- 🧩 **Written in Brainfuck.** Source filtering, validation and optimization are plain `><+-.,[]` programs.
- ⚙️ **Native output.** Produces Windows x86-64 `.exe` files and Android ARM64 executables.
- 🚫 **No Python at compile time.** `bbc.exe compile` is a single native process.
- 📦 **One format.** Every level and size goes through the same [BFX](docs/02_BFX_CONTRACT.md) record.
- 🔒 **Checked.** Every build re-verifies its graphs. Moving off the tape is a clean failure, never undefined behavior.

---

## 🚀 Quick start

Put `bbc.exe`, `bbc-windows-x86_64.xax` and `bbc-android-arm64.xax` in `build/`
([how to bootstrap them](docs/04_BOOTSTRAP.md)), then from Command Prompt:

```text
build\bbc.exe compile windows-x86_64 hello.exe < hello.bf
build\bbc.exe compile android-arm64 -O1 hello < hello.bf
build\bbc.exe emit-bfx -O1 < hello.bf > hello.bfx
build\bbc.exe check < hello.bf
build\bbc.exe info < hello.bfx
```

- `-O1` (default) packs runs and folds clear loops. `-O0` keeps every instruction.
- Discard the output if the exit code isn't 0 ([exit codes](docs/25_NATIVE_COMPILE.md#-use)).
- In PowerShell, wrap commands in `cmd /d /c "..."` so redirection stays binary.

---

## 📐 Limits

| | |
|---|---|
| Source size | 1 MiB |
| Instructions (before packing) | 65,536 |
| Nesting depth | 32,768 |
| Tape | 65,536 wrapping byte cells |
| End of input | Reads 0 |

---

## 🏁 Benchmarks

BBC vs Awib, brainfry, bf-x86, bflang, Brainfly, pablojorge/brainfuck, abfc and
Wilfred/bfc on 18 programs (2026-10-22). Medians per program, geometric means per
group. Lower is better; **bold** is best, and 🏆 says who wins what.

### 📦 Small programs (12)

| Compiler | ✅ | Build | Run | File size | Build RAM | Run RAM | 🏆 Best at |
|---|---:|---:|---:|---:|---:|---:|---|
| **BBC** 🍷 | 12/12 | 104 ms | 44.9 ms | 15.9 KB | 26 MiB | 6.6 MiB | 🍷 Run under Wine (by 0.4 ms) |
| brainfry-win 🍷 | 12/12 | 3.9 ms | 45.3 ms | 3.0 KB | 2.3 MiB | 6.7 MiB | — |
| brainfry | 12/12 | 3.9 ms | **2.3 ms** | 1.3 KB | 2.3 MiB | 1.7 MiB | 🏃 Run |
| bf-x86 | 12/12 | **3.5 ms** | 2.5 ms | **264 B** | **1.7 MiB** | 1.9 MiB | 🔨 Build · 📦 Size · 🧠 Build RAM |
| pablojorge | 11/12 | 61 ms | 3.2 ms | 16.1 KB | 27 MiB | 1.7 MiB | — |
| Wilfred/bfc | 12/12 | 77 ms | 3.3 ms | 16.1 KB | 66 MiB | 1.7 MiB | — |
| bflang | 12/12 | 63 ms | 3.4 ms | 16.1 KB | 71 MiB | 1.7 MiB | — |
| Awib | 12/12 | 57 ms | 3.4 ms | 16.1 KB | 25 MiB | 1.7 MiB | — |
| abfc | 12/12 | 16 ms | 3.4 ms | 13.6 KB | 4.6 MiB | 1.7 MiB | — |
| Brainfly | 12/12 | 6,851 ms | 5.7 ms | 1.19 MB | 193 MiB | 3.5 MiB | — |

### 🏋️ Large programs (5)

| Compiler | ✅ | Build | Run | File size | Build RAM | 🏆 Best at |
|---|---:|---:|---:|---:|---:|---|
| **BBC** 🍷 | 5/5 | 506 ms | 289 ms | 361 KB | 132 MiB | — |
| brainfry-win 🍷 | 5/5 | 4.7 ms | 98.5 ms | 18.1 KB | 3.0 MiB | 🍷 Run under Wine |
| Awib | 5/5 | 217 ms | **9.5 ms** | 19.7 KB | 54 MiB | 🏃 Run |
| pablojorge | 5/5 | 316 ms | 10.5 ms | 19.7 KB | 69 MiB | — |
| bflang | 5/5 | 647 ms | 10.6 ms | 21.7 KB | 96 MiB | — |
| Wilfred/bfc | 5/5 | 257 ms | 10.7 ms | 23.3 KB | 70 MiB | — |
| brainfry | 5/5 | 4.3 ms | 13.8 ms | 15.4 KB | 3.0 MiB | — |
| bf-x86 | 5/5 | **3.6 ms** | 22.6 ms | **4.2 KB** | **1.7 MiB** | 🔨 Build · 📦 Size · 🧠 Build RAM |
| abfc | 5/5 | 132 ms | 29.5 ms | 32.0 KB | 5.1 MiB | — |
| Brainfly | 5/5 | 12,742 ms | 38.6 ms | 1.20 MB | 1,519 MiB | — |

### ⏱️ Run time per large program (ms)

| Program | BBC 🍷 | brainfry-win 🍷 | Awib | brainfry | bf-x86 | bflang | Brainfly | pablojorge | abfc | Wilfred/bfc | 🏆 Fastest |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| mandelbrot | 21,954 | 1,677 | **481** | 1,622 | 792 | 1,056 | 1,549 | 922 | 1,280 | 1,006 | **Awib** |
| bottles | 48 | 61 | 3.3 | 10.8 | 10.7 | 3.3 | 15.8 | 3.4 | 14.5 | **3.1** | **Wilfred/bfc** |
| factor | 49 | 45 | 3.6 | **2.2** | 2.4 | 3.1 | 5.4 | 3.3 | 3.1 | 3.3 | **brainfry** |
| life | 911 | 45 | **3.6** | 4.5 | 98.5 | 3.8 | 98.6 | 3.7 | 97.6 | 3.7 | **Awib** |
| sierpinski | 42 | 45 | 3.7 | **3.0** | **3.0** | 3.3 | 6.5 | 3.3 | 4.0 | 3.6 | **brainfry, bf-x86** |

🍷 = runs under Wine 9.0 (BBC builds Windows programs). An empty program costs
~43 ms there vs ~2–3 ms natively. Everything else builds and runs natively on
Linux x86-64. brainfry-win is brainfry's Windows output under the same Wine, the
fair same-platform comparison.

- 🟰 Under the same Wine, BBC's small programs run as fast as brainfry's (44.9 vs 45.3 ms).
- 🤝 Run RAM ties at ~1.7 MiB (the launcher floor) for six native compilers.
- 🐢 Heavy loops (Mandelbrot: 22 s) are BBC's weak spot; loop optimizations are next.
- ❌ pablojorge fails nested_math: its 30,000-cell tape isn't zeroed.

👉 Full tables and method: [benchmarks](docs/08_BENCHMARKS.md)

---

## 🗺️ How it works

```text
program.bf ──► Brainfuck passes ──► BFX ──► XAX importer ──► verify ──► lower ──► .exe / ELF
              (filter, pack, optimize)        └──────── all inside bbc.exe ────────┘
```

1. **Brainfuck passes** filter the source, pack runs and optimize safe loops.
2. **The XAX importer** turns the BFX record into a verified semantic graph.
3. **The XAX driver** binds, verifies, lowers and packages it for the target.

More: [XAX integration](docs/03_XAX_INTEGRATION.md) · [native compile](docs/25_NATIVE_COMPILE.md)

---

## 📊 Status

- ✅ Native single-process compile for Windows x86-64 and Android ARM64.
- ✅ 332 builds and 588 runs match an independent interpreter.
- 🐢 Slow generated code on heavy compute; loop optimizations are next.
- 🚧 Android worker thread, Windows DLLs and an Android-hosted compiler are open.

Details: [status and evidence](docs/05_STATUS.md)

---

## 📚 Docs

**Start here**
- [Execution profile](docs/01_BRAINFUCK_PROFILE.md) · [BFX format](docs/02_BFX_CONTRACT.md) · [Compile interface](docs/21_UNIFIED_COMPILATION.md) · [Native compile](docs/25_NATIVE_COMPILE.md)

**Inside**
- [XAX integration](docs/03_XAX_INTEGRATION.md) · [Bootstrap](docs/04_BOOTSTRAP.md) · [Optimization proofs](docs/07_OPTIMIZATION_PROOFS.md) · [Scalability](docs/16_SCALABILITY.md) · [Streaming](docs/17_STREAMING_COMPILATION.md)

**Performance**
- [Benchmarks](docs/08_BENCHMARKS.md) · [Performance plan](docs/06_PERFORMANCE_PLAN.md) · [Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md)

**History**
- Optimizations: [clear](docs/10_CLEAR_OPTIMIZATION.md) · [clear bench](docs/11_V2_BENCHMARKS.md) · [arithmetic](docs/12_ARITHMETIC_PACKING.md) · [arithmetic bench](docs/13_V3_BENCHMARKS.md) · [movement](docs/14_MOVEMENT_PACKING.md) · [movement bench](docs/15_V4_BENCHMARKS.md)
- Native path: [build cache](docs/18_BACKEND_BUILD_CACHE.md) · [driver follow-up](docs/19_NATIVE_DRIVER_FOLLOWUP.md) · [modernization](docs/20_MODERNIZATION.md) · [native lowering](docs/22_NATIVE_LOWERING.md) · [Android lowering](docs/23_ANDROID_NATIVE_LOWERING.md) · [ARM64 build latency](docs/24_XAX_BUILD_LATENCY.md)

**Contributing**
- [Rules for maintainers](AGENT.md) · [Status](docs/05_STATUS.md)

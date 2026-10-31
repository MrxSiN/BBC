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

- `-O1` (default) folds straight code into offset instructions and simple counted loops into multiplies. `-O0` keeps every instruction.
- Discard the output if the exit code isn't 0 ([exit codes](docs/25_NATIVE_COMPILE.md#-use)).
- In PowerShell, wrap commands in `cmd /d /c "..."` so redirection stays binary.

---

## 📐 Limits

| | |
|---|---|
| Source size | 1 MiB |
| Instructions (before folding) | 65,536 |
| Nesting depth | 32,768 |
| Tape | 2,147,246,080 wrapping byte cells (2 GiB − 232 KiB), memory used only as touched |
| Input, output | 65,536 bytes each |
| End of input | Reads 0 |

---

## 🏁 Benchmarks

BBC O1 vs brainfry and Awib (C output built with gcc and clang `-O2`) on 18 programs,
all built and run natively on Windows 11 (Ryzen 9 5900HS), 2026-10-31. Medians of 15
runs, geometric means per group. Lower is better; **bold** is best.

### 📦 Small programs (13) and 🏋️ large programs (5), geometric means

| Compiler | ✅ | Build | Run | File size | Build RAM | Large: build | Large: run | Large: size | Large: build RAM |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **BBC** | 18/18 | 40 ms | 13.6 ms | 8.6 KB | 16 MiB | 228 ms | 51.9 ms | 42 KB | 43 MiB |
| brainfry | 18/18 | **14 ms** | **13.4 ms** | **2.8 KB** | **9.2 MiB** | **15 ms** | 53.5 ms | **18 KB** | **9.2 MiB** |
| Awib + gcc | 18/18 | 241 ms | 14.0 ms | 62 KB | 10.8 MiB | 410 ms | **30.6 ms** | 66 KB | 10.8 MiB |
| Awib + clang | 18/18 | 157 ms | 13.9 ms | 116 KB | 22 MiB | 239 ms | 30.8 ms | 122 KB | 22 MiB |

### ⏱️ Run time per large program (ms)

| Program | BBC | brainfry | Awib + gcc | Awib + clang |
|---|---:|---:|---:|---:|
| mandelbrot | 1,080 | 933 | 329 | **325** |
| factor | 84 | 58 | **28** | 28 |
| life | 23 | 22 | **15** | 16 |
| bottles | **13.5** | 24 | 14.0 | 13.9 |
| sierpinski | **13.3** | 15.3 | 13.9 | 14.0 |

- 🟰 Small programs all run at the ~13–14 ms Windows process floor.
- 🏃 BBC beats brainfry on bottles and sierpinski and on large-program run time overall,
  but Awib's C output is ~3× faster on Mandelbrot and factor.
- 🔨 brainfry builds fastest and smallest; BBC builds faster than the C pipelines on small programs.
- 📈 Since 2026-10-29 Mandelbrot went 7.7 s → 1.08 s: decisions now take one packed length
  argument, so XAX's Windows backend keeps values in registers.

👉 Full tables, method, older 9-compiler runs (Wine/Linux) and Android: [benchmarks](docs/08_BENCHMARKS.md)

---

## 🗺️ How it works

```text
program.bf ──► Brainfuck passes ──► BFX ──► XAX importer ──► verify ──► lower ──► .exe / ELF
              (filter, fold)                  └──────── all inside bbc.exe ────────┘
```

1. **Brainfuck passes** filter the source and fold straight code and simple loops.
2. **The XAX importer** turns the BFX record into a verified semantic graph.
3. **The XAX driver** binds, verifies, lowers and packages it for the target.

More: [XAX integration](docs/03_XAX_INTEGRATION.md) · [native compile](docs/25_NATIVE_COMPILE.md)

---

## 📊 Status

- ✅ Native single-process compile for Windows x86-64 and Android ARM64.
- ✅ 332 builds and 588 runs match an independent interpreter; the current build matches
  the previous one on 170 differential cases.
- 🐢 Heavy compute still trails Awib by ~3×; scan loops aren't folded yet.
- 🚫 Mandelbrot at O0 is declined by XAX's native verifier (XAX OI-51).
- 🚧 Android worker thread, Windows DLLs and an Android-hosted compiler are open.

Details: [status and evidence](docs/05_STATUS.md)

---

## 📚 Docs

**Start here**
- [Execution profile](docs/01_BRAINFUCK_PROFILE.md) · [BFX format](docs/02_BFX_CONTRACT.md) · [Compile interface](docs/21_UNIFIED_COMPILATION.md) · [Native compile](docs/25_NATIVE_COMPILE.md)

**Inside**
- [XAX integration](docs/03_XAX_INTEGRATION.md) · [Bootstrap](docs/04_BOOTSTRAP.md) · [Optimization proofs](docs/07_OPTIMIZATION_PROOFS.md) · [Scalability](docs/16_SCALABILITY.md) · [Streaming](docs/17_STREAMING_COMPILATION.md) · [Fold pass](docs/10_FOLD_OPTIMIZATION.md)

**Performance**
- [Benchmarks](docs/08_BENCHMARKS.md) · [Performance plan](docs/06_PERFORMANCE_PLAN.md) · [Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md)

**Contributing**
- [Rules for maintainers](AGENT.md) · [Status](docs/05_STATUS.md)

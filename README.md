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
Wilfred/bfc on 18 programs (2026-10-22, medians, geometric means):

| | BBC 🍷 | Best other |
|---|---:|---|
| ✅ Correct | 18/18 | 7 others 18/18 |
| 🔨 Build, small | 104 ms | bf-x86 3.5 ms |
| 🏃 Run, small | 44.9 ms | brainfry 2.3 ms · brainfry-win 🍷 45.3 ms |
| 🏋️ Run, large | 289 ms | Awib 9.5 ms |
| 📦 Size, small | 15.9 KB | bf-x86 264 B |

🍷 BBC builds Windows programs, so it ran under Wine; an empty program costs
~43 ms there. Under the same Wine, BBC's small programs run as fast as brainfry's.
Heavy loops (Mandelbrot: 22 s) are BBC's weak spot.

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

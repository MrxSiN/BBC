# 🔍 Brainfry analysis

> Why the fastest competitor is fast, where it cuts corners, and what BBC learns from it.

Brainfry ([`e55d457`](https://github.com/DirazCoder/brainfry/tree/e55d45735a6feb450a7e47852f4340f5b532fef8))
is a Rust compiler that writes x86-64/ARM64 machine code and the executable
container itself, in one process. The current numbers are in
[benchmarks](08_BENCHMARKS.md).

---

## 🏎️ Why it's fast and small

| Area | Brainfry | BBC + XAX |
|---|---|---|
| Build | One native process: parse, optimize, emit, write. No assembler or linker | Brainfuck frontend, importer, then a general verified compiler that verifies every graph before lowering |
| Arithmetic | Any run becomes one immediate add | Packs runs in powers of two |
| Loops | `Zero`, offset `MulAdd` and stride `Scan` | Exact clear loops only; affine and scan need proofs first |
| Backend | Dedicated emitters, tape pointer in a register | General verified backend; code quality is the open problem |
| Tape | Fresh OS pages, a tiny runtime | A 2 GiB reservation committed as touched; each call clears cells 0–65,535 on a fresh tape |
| File size | Hand-written minimal PE/ELF | Generic packaging |

This is implementation analysis, not a per-pass timing experiment.

---

## 🐛 Bugs found in Brainfry

Its optimized native compiler gets these wrong:

| Program | Correct behavior | Brainfry does |
|---|---|---|
| `+[++].` | Loops forever (odd cell, even step) | Exits and prints `00` |
| `+[--].` | Loops forever | Exits and prints `00` |
| `+[<>-].` | Fails on the first move left of cell 0 | Exits and prints `00` |
| `+[+++].` | Terminates and prints `00` | ✅ Correct |

- The clear-loop recognizer accepts any step count without a termination proof.
- The offset recognizer can drop a move that has no cell effect.

These are correctness checks, not races. They don't disqualify Brainfry's valid
workloads, which stay in every comparison.

Other differences:

- Brainfry's tape grows and EOF leaves the cell unchanged.
- Brainfly uses unchecked spans and stops on EOF.

Timed programs avoid EOF and stay on low tape cells, so every arm agrees.

---

## 🛠️ What BBC took from this

- ✅ [Capacity flag](07_OPTIMIZATION_PROOFS.md#-p0-carry-triggered-capacity-flag): a frontend speedup.
- ✅ [Clear loops](10_FOLD_OPTIMIZATION.md) and arithmetic/movement
  [run packing](17_STREAMING_COMPILATION.md), each proven, with Brainfry's
  bugs kept as negative tests.
- ✅ A fully [native, single-process build](25_NATIVE_COMPILE.md): 0.10 s under
  Wine, down from about 1.5 s.
- ⏳ Still open: affine transfers, scans, odd-step clears, and above all
  generated-code quality.

---

## 🟣 Brainfly setup

Brainfly ([`2e1d1b5`](https://github.com/hez2010/Brainfly/tree/2e1d1b56725dd69b2278ee4566ee2dacfca5d348))
needs .NET 10. SDK **10.0.402** from Microsoft's official install script builds it
with zero warnings. Its JIT mode and its generated NativeAOT programs pass all
twelve pilot programs. The [latest benchmark](08_BENCHMARKS.md) times its NativeAOT
route.

📎 [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json)

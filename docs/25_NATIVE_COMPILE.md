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

1. **Front:** `stream_chunks.bf`, `stream_runs.bf` and `optimize.bf`, then the
   strict BFX decoder and importer. A small framing function turns the decision
   into one expected-root edit record.
2. **Edit:** binds the decision into the target's host build request.
3. **Resolve:** produces the build snapshot.
4. **Build:** verifies, lowers and packages.

`bbc.exe` contains the whole XAX driver and calls its entry once per step. Every
step verifies its own inputs; the edit record is never trusted.

---

## ✅ Checks

- **83 programs** at O0 and O1 on both targets: 332 builds and 588 runs, all
  matching an independent interpreter in output bytes and exit code.
- The programs: pilot programs, BBC tests, both depth-512 programs, negative loops,
  60 random programs and capacity cases.
- Rebuilt artifacts are byte-identical to ones that earlier ran on Windows 11 and
  a Pixel 8 Pro.
- Driver commands through `bbc.exe` match the standalone driver on all 141
  regression stores.
- Error paths exit 1, 4, 4, 3, 3 and leave no files behind.

> ⚠️ New runs used Wine 9.0 and `qemu-aarch64` on Linux. That is not real
> Windows or device execution; byte identity with earlier device runs is the link.

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

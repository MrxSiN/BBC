# 🗂️ Snapshot: arithmetic packing (v3)

> Historical. Measured before the format migration with the old Python-SDK
> build path. "v2/v3" name the evidence, not today's format.

What changed: [arithmetic packing](12_ARITHMETIC_PACKING.md). Same sixteen
workloads, hosts and protocol as the [v2 snapshot](11_V2_BENCHMARKS.md).

## ⏱️ Build and run time

Geometric mean of the 16 workload medians, in ms. Lower is better.

| Target | Boundary | BBC v2 | BBC v3 | Brainfry |
|---|---|---:|---:|---:|
| Android | Run | 6.275 | 5.825 | 5.432 |
| Android | Build | 1,249.8 | 1,143.0 | 26.9 |
| Windows | Run | 26.000 | 25.758 | 26.720 |
| Windows | Build | 1,331.6 | 1,171.9 | 26.9 |

Builds got 1.09× (Android) and 1.14× (Windows) faster: smaller graphs outweigh the extra stage.

## 🧠 Memory and 📦 size

| Target | BBC v3 build RAM | Brainfry build RAM | BBC v2 file | BBC v3 file | Brainfry file |
|---|---:|---:|---:|---:|---:|
| Android | 51.0 MiB | 5.3 MiB | 3,644 B | 2,743 B | 1,140 B |
| Windows | 51.0 MiB | 5.3 MiB | 21,501 B | 14,183 B | 2,890 B |

Android hello grew 16.7%; that regression is recorded.

## 🔁 Native decision calls (v2 → v3)

Geometric mean speedup: **1.432×** on Android, **1.236×** on Windows. Biggest wins:
`clear_set` 20.4× / 8.0×, `multi_transfer` 2.53× / 1.56×, `nested_math` 1.94× / 1.47×.

## 🧾 Verdict

A real speedup for arithmetic-heavy code, plus smaller files. Brainfry still
builds about 43× faster and its files are smaller.

📎 [bfx_v3_measurements.json](../evidence/bfx_v3_measurements.json) · [bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json)

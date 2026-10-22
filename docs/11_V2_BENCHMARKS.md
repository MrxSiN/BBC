# 🗂️ Snapshot: clear-loop pass (v2)

> Historical. Measured before the format migration with the old Python-SDK
> build path. "v1/v2" name the evidence, not today's format.

What changed: the [clear-loop pass](10_CLEAR_OPTIMIZATION.md). Sixteen workloads
(the twelve pilot programs plus four clear-loop ones). Ryzen 7 5800H and Windows 11;
Pixel 8 Pro running API 37. Three run clusters.

## ⏱️ Build and run time

Geometric mean of the 16 workload medians, in ms. Lower is better.

| Target | Boundary | BBC v1 | BBC v2 | Brainfry |
|---|---|---:|---:|---:|
| Android | Run | 7.335 | 7.019 | 6.172 |
| Android | Build | 1,345.5 | 1,348.0 | 30.2 |
| Windows | Run | 27.318 | 27.223 | 28.117 |
| Windows | Build | 1,430.2 | 1,432.9 | 30.2 |

## 🧠 Memory and 📦 size

| Target | BBC v1 build RAM | BBC v2 build RAM | Brainfry build RAM | BBC v2 file | Brainfry file |
|---|---:|---:|---:|---:|---:|
| Android | 51.0 MiB | 51.0 MiB | 5.3 MiB | 3,644 B | 1,140 B |
| Windows | 51.0 MiB | 51.0 MiB | 5.3 MiB | 21,501 B | 2,890 B |

## 🔁 Native decision calls (v1 → v2)

Geometric mean speedup: **1.416×** on Android, **1.222×** on Windows. Biggest wins:
`clear_repeat` 28.8× / 7.4×, `clear_set` 2.10× / 1.76×.

## 🧾 Verdict

The pass shrinks clear-heavy programs and speeds up their execution. The extra
build stage costs a little. Brainfry stays far ahead on build time and size.

📎 [bfx_v2_optimization.json](../evidence/bfx_v2_optimization.json): plan, bytes, hashes, raw samples, intervals.

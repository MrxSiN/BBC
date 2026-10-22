# 🗂️ Snapshot: movement packing (v4)

> Historical. Measured before the format migration with the old Python-SDK
> build path. "v3/v4" name the evidence, not today's format.

What changed: [movement packing](14_MOVEMENT_PACKING.md). Same sixteen workloads,
hosts and protocol as the [v2 snapshot](11_V2_BENCHMARKS.md).

## ⏱️ Build and run time

Geometric mean of the 16 workload medians, in ms. Lower is better.

| Target | Boundary | BBC v3 | BBC v4 | Brainfry |
|---|---|---:|---:|---:|
| Android | Run | 6.493 | 6.464 | 5.560 |
| Android | Build | 1,132.7 | 1,110.7 | 26.5 |
| Windows | Run | 25.589 | 25.993 | 26.663 |
| Windows | Build | 1,159.7 | 1,137.1 | 26.7 |

## 🧠 Memory and 📦 size

| Target | BBC v4 build RAM | Brainfry build RAM | BBC v3 file | BBC v4 file | Brainfry file |
|---|---:|---:|---:|---:|---:|
| Android | 51.0 MiB | 5.3 MiB | 2,743 B | 2,729 B | 1,140 B |
| Windows | 51.0 MiB | 5.3 MiB | 14,183 B | 14,036 B | 2,890 B |

No file grew. Android hello went from 5,976 to 5,888 bytes, still above v2's 5,120.

## 🔁 Native decision calls (v3 → v4)

Geometric mean: **0.930×** on Android (slower) and **1.005×** on Windows.
`binary_echo` (0.56×) and `clear_input` (0.63×) slowed down even though their
libraries are byte-identical. A follow-up control found near parity, but it
could not isolate why. So this run shows **no** runtime gain.

📎 [call controls](../evidence/bfx_v4_call_controls.json)

## 🧾 Verdict

Slightly smaller files and builds about 1.02× faster. No runtime win. Brainfry stays ahead.

📎 [bfx_v4_measurements.json](../evidence/bfx_v4_measurements.json) · [bfx_v4_movement.json](../evidence/bfx_v4_movement.json)

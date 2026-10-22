# 🗂️ Snapshot: ARM64 alias index

> Historical. Depth-512 builds went from almost two minutes to under a second.

## 🐌 The problem

Building a depth-512 snapshot spent 112.4 of 112.7 seconds in ARM64 alias/range
analysis. For every parameter, the fixed point re-scanned every CFG edge.

## ⚡ The fix (XAX)

Build one incoming-edge index per function, then visit only the relevant block's
incoming edges.

- Order, representatives, distinctness stamps and fixed-point rounds are all preserved.
- If the scratch space doesn't fit, it falls back to the original scan.
- First verification is untouched.
- Root `ec66899f…`. Compiler PE: 11,876,864 bytes (6,656 bytes larger).

## ✅ Checks

- 1,091 helper checks and 1,091 production-dispatch checks against a whole-CFG
  reference, including cycles, self edges, capacity failures and a 200-block chain.
- 22 Android snapshots, 44 builds and 47 Pixel 8 Pro runs. Every artifact is unchanged.
- 160 diagnostics and 3 Windows smoke artifacts are exact.

## ⏱️ Prepared-store build time

| Android snapshot | Before | After | Saved |
|---|---:|---:|---:|
| hello | 32.15 ms | 26.76 ms | 16.8% |
| nested_math | 28.90 ms | 23.35 ms | 19.2% |
| checksum_four | 29.06 ms | 23.13 ms | 20.4% |
| deep-512 O1 | 111,340 ms | 327 ms | 99.7% |
| deep-active-512 O1 | 146,465 ms | 688 ms | 99.5% |

These numbers exclude frontend, import and binding. Measured on Ryzen 7 5800H.
The deep cases have only 3 samples per arm.

📎 [xax_alias_index.json](../evidence/xax_alias_index.json)

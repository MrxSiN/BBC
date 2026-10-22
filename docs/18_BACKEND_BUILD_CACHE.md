# 🗂️ Snapshot: compile-local proof cache (Python SDK)

> Historical. An early attempt to reuse verification facts inside the old
> Python-SDK build. It did not help. The native
> [graph proof cache](25_NATIVE_COMPILE.md#-graph-proof-cache) later did.

## 🧪 What was tried

One empty `ProofCache` per compiler process, attached to the first
`StoreReader`, so later backend passes reuse object proofs.

- The first verification had zero entries and zero hits.
- No sidecar or producer assertion supplied any trusted fact.

## ✅ Checks

All 64 validation builds reproduced the earlier v4 executable hashes, across
16 sources, 2 targets and 2 configurations. All 32 Windows executions and the
16 Android ones passed.

## ⏱️ Result

216 timed builds; Ryzen 7 5800H, Python 3.13.5. Median ms:

| Target | Program | BBC | BBC + cache | Brainfry |
|---|---|---:|---:|---:|
| Android | hello | 1,674.9 | 1,664.4 | 28.1 |
| Android | nested_math | 1,594.9 | 1,595.6 | 28.2 |
| Android | checksum_four | 1,559.6 | 1,536.2 | 28.1 |
| Windows | hello | 1,684.3 | 1,686.6 | 29.0 |
| Windows | nested_math | 1,621.0 | 1,608.7 | 28.0 |
| Windows | checksum_four | 1,565.3 | 1,566.4 | 27.8 |

- Speedup: **1.009×** (Android target) and **1.001×** (Windows). Not significant.
- RAM was unchanged (about 57.4 MiB, vs about 5.2 MiB for Brainfry).
- Brainfry built about 56× faster.

## 🔍 Side finding

The 508-function Windows driver's largest graph body is 1,884,002 bytes, under
the 2 MiB budget. So graph size did not explain its self-store decline.

📎 [backend_build_cache.json](../evidence/backend_build_cache.json)

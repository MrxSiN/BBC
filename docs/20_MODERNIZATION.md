# 🗂️ Snapshot: modernization baseline

> Historical. The "before" photo, taken 2026-10-21 at BBC `2d9fbd6` / XAX `42de0fc`,
> before the native pipeline existed.

## 🧱 Architecture back then

| Stage | Implementation | Ran on |
|---|---|---|
| Bounded source filtering | `compiler.bf` | Native BF or the seed interpreter |
| Wide filtering | `stream_chunks.bf` + XAX `source.xax` | Native BF and XAX |
| Optimizations | `optimize.bf`, `pack_arithmetic.bf`, `pack_moves.bf`, `stream_runs.bf` | Native BF |
| BFX validation and import | XAX `bfx.xax`, `import_bfx.xax` | Native, Windows and Android |
| Verification, binding, lowering, packaging | Generic XAX Python SDK | Python on Windows |

## ⏱️ Measurements

180 fresh-process builds; Ryzen 7 5800H, Windows 11. Brainfry pinned at `e55d457`.

| Program | Target | BBC ms | Brainfry ms | Peak RAM BBC / Brainfry | File BBC / Brainfry |
|---|---|---:|---:|---|---|
| hello | Windows | 1,578.9 | 24.0 | 63.1 / 5.2 MiB | 25,600 / 3,584 B |
| hello | Android | 1,558.1 | 23.6 | 63.1 / 5.2 MiB | 5,880 / 1,760 B |
| nested_math | Windows | 1,507.4 | 23.4 | 63.2 / 5.2 MiB | 17,408 / 3,072 B |
| nested_math | Android | 1,468.7 | 23.6 | 63.0 / 5.2 MiB | 3,540 / 1,200 B |
| checksum_four | Windows | 1,500.3 | 23.8 | 62.8 / 5.2 MiB | 17,408 / 3,072 B |
| checksum_four | Android | 1,462.5 | 23.5 | 63.0 / 5.2 MiB | 3,496 / 1,216 B |

## 🐌 Where the time went (Windows hello)

| Stage | ms |
|---|---:|
| Python startup and SDK import | ~815 |
| Binding with its checks | ~233 |
| Lowering | ~180 |
| First verification | ~133 |
| Repeated verification | ~72 |
| BBC's own Brainfuck filtering, packing and import | ~1.6 |

Brainfuck was never the bottleneck. Python startup and XAX graph work were.
That set the plan: a native driver, then proof reuse, then semantic optimizations.

## ➡️ What happened next

[Native compile](25_NATIVE_COMPILE.md) replaced the Python path: the same
builds now take about 0.1 s under Wine.

📎 [modernization_baseline.json](../evidence/modernization_baseline.json)

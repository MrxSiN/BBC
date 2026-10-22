# BBC — Ballsdeep Brainfuck Compiler

BBC compiles Brainfuck to native programs through XAX. Standard Brainfuck
sources validate/filter source and perform semantic optimization; canonical XAX
graphs validate BFX, import decisions and generate native code.

There is one portable **BFX** format for every optimization level, supported
source size and target. [The BFX specification](docs/02_BFX_CONTRACT.md) is the
single wire authority. The intentional migration uses a new four-byte magic
and one identifier; old layouts are rejected without fallback.

One [public compilation interface](docs/21_UNIFIED_COMPILATION.md) accepts
small and large binary sources: up to **1 MiB raw source**, **65,536 commands**
before optimization and balanced nesting **32,768**. These are fixed budgets;
[dynamic workspace growth](docs/16_SCALABILITY.md) remains open. Programs use
65,536 wrapping byte cells, checked movement and EOF-as-zero.

## Use the compiler

Put `bbc.exe` and the two host requests `bbc-android-arm64.xax` and
`bbc-windows-x86_64.xax` in ignored `build/` (see [native compilation](docs/25_NATIVE_COMPILE.md)
and the external XAX [bootstrap recipes](https://github.com/MrxSiN/XAX/blob/1af64bff46723b54a132a9586a82f9a0fa527534/compiler/integration/bfx/COMPILE.md)).
From Command Prompt:

```text
build\bbc.exe compile windows-x86_64 -O1 program.exe < program.bf
build\bbc.exe compile android-arm64 -O1 program < program.bf
build\bbc.exe emit-bfx -O1 < program.bf > program.bfx
build\bbc.exe check < program.bf
build\bbc.exe info < program.bfx
```

PowerShell users can run these through `cmd /d /c "..."` for binary redirection.
O0 preserves primitives; O1 integrates BF run packing and safe bounded clear
optimization. O2/O3 are not implemented. Every level uses identical BFX framing.
Discard output on nonzero exit. [The interface guide](docs/21_UNIFIED_COMPILATION.md)
defines the source interface and limits; [native compilation](docs/25_NATIVE_COMPILE.md)
defines `compile` exits and outputs.

Every command runs without Python, and `compile` runs in one process: `bbc.exe`
contains the native XAX driver, which binds, resolves, verifies, lowers and
packages. Bootstrapping
`bbc.exe` and the driver still uses the disclosed generic XAX SDK once. Native
components execute on Windows x86-64 and Android ARM64. See [integration](docs/03_XAX_INTEGRATION.md)
and [bootstrap](docs/04_BOOTSTRAP.md). The bounded compiler and text framer are
private seed/reference components, not another public workflow.

BBC has no established overall performance lead. [Benchmarks](docs/08_BENCHMARKS.md),
[Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md), [measurement plan](docs/06_PERFORMANCE_PLAN.md),
[cold cache experiment](docs/18_BACKEND_BUILD_CACHE.md) and
[native driver follow-up](docs/19_NATIVE_DRIVER_FOLLOWUP.md) retain their scoped
results. M4 remains incomplete and M8 is not achieved. The installed .NET SDK
unblocks Brainfly correctness testing; no Brainfly timing score is established.
The BFX migration makes no performance claim.

The [modernization audit and fresh baseline](docs/20_MODERNIZATION.md) records
180 current-revision builds and native driver coverage. It confirms that startup
and XAX graph work dominate compilation. The complete native driver remains
an implementation milestone. The
[unified interface phase](docs/21_UNIFIED_COMPILATION.md) now implements the
public entry point; the frozen baseline describes its earlier state.

[Android native lowering](docs/23_ANDROID_NATIVE_LOWERING.md) passes all 22
prepared Android snapshots, 44 native builds and 47 Pixel 8 Pro executions,
including an active depth-512 program. The 20 previously successful Android
artifacts remain identical. Prepared-build timings exclude frontend/import/
binding; full native compilation and competitive evaluation remain incomplete.

[Native compilation](docs/25_NATIVE_COMPILE.md) completes the Python-free
source-to-executable path: 332 builds and 588 emulated executions match an
independent interpreter, earlier device-executed artifacts reproduce exactly,
and single-process builds measure about 0.11 s under Wine against about 1.4 s
for the previous Python path on the same host. The driver's large views are now
committed only when touched: peak commit falls from 3,398 MiB to under 140 MiB.
Each graph is now checked once per build, 3–7.5% faster. No Brainfry verdict
follows.

[XAX build-latency work](docs/24_XAX_BUILD_LATENCY.md) replaces repeated ARM64
whole-graph alias scans with an incoming-edge index. All 22 Android artifacts
and 160 diagnostic controls remain exact. The report compares fresh native
prepared builds; full-source compilation and competitor scores remain separate.

## Documentation

- [Execution profile](docs/01_BRAINFUCK_PROFILE.md)
- [BFX specification](docs/02_BFX_CONTRACT.md)
- [XAX integration](docs/03_XAX_INTEGRATION.md)
- [Bootstrap](docs/04_BOOTSTRAP.md)
- [Status and evidence](docs/05_STATUS.md)
- [Performance plan](docs/06_PERFORMANCE_PLAN.md)
- [Optimization proofs](docs/07_OPTIMIZATION_PROOFS.md)
- [Benchmarks](docs/08_BENCHMARKS.md)
- [Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md)
- [Clear optimization](docs/10_CLEAR_OPTIMIZATION.md)
- [Historical clear benchmarks](docs/11_V2_BENCHMARKS.md)
- [Arithmetic packing](docs/12_ARITHMETIC_PACKING.md)
- [Historical arithmetic benchmarks](docs/13_V3_BENCHMARKS.md)
- [Movement packing](docs/14_MOVEMENT_PACKING.md)
- [Historical movement benchmarks](docs/15_V4_BENCHMARKS.md)
- [Scalability](docs/16_SCALABILITY.md)
- [Streaming compilation](docs/17_STREAMING_COMPILATION.md)
- [Backend cache](docs/18_BACKEND_BUILD_CACHE.md)
- [Native driver follow-up](docs/19_NATIVE_DRIVER_FOLLOWUP.md)

- [Modernization audit and fresh baseline](docs/20_MODERNIZATION.md)

- [Unified public compilation and native command](docs/21_UNIFIED_COMPILATION.md)
- [Native lowering and remaining Android coverage](docs/22_NATIVE_LOWERING.md)
- [Android native lowering](docs/23_ANDROID_NATIVE_LOWERING.md)
- [XAX ARM64 build latency](docs/24_XAX_BUILD_LATENCY.md)
- [Native source-to-executable compilation](docs/25_NATIVE_COMPILE.md)

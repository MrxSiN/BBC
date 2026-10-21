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

Build the native Windows command using the external XAX
[bootstrap recipe](https://github.com/MrxSiN/XAX/blob/d320babab5bb9fe61a9d29f1f14942a847bf83a7/compiler/integration/bfx/COMPILE.md),
then place `bbc.exe` in ignored `build/`. From Command Prompt:

```text
build\bbc.exe emit-bfx -O1 < program.bf > program.bfx
build\bbc.exe check < program.bf
build\bbc.exe info < program.bfx
```

PowerShell users can run these through `cmd /d /c "..."` for binary redirection.
O0 preserves primitives; O1 integrates BF run packing and safe bounded clear
optimization. O2/O3 are not implemented. Every level uses identical BFX framing.
Discard output on nonzero exit. [The interface guide](docs/21_UNIFIED_COMPILATION.md)
defines exit codes, limits, typed API and current optimization coverage.

The supported commands execute without Python. Building the command and compiling
BFX into native executables/libraries still require the external Windows-hosted
generic XAX SDK; full native `bbc compile` remains incomplete. Native components
execute on Windows x86-64 and Android ARM64. See [integration](docs/03_XAX_INTEGRATION.md)
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

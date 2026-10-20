# BBC — Ballsdeep Brainfuck Compiler

BBC compiles Brainfuck to native programs through XAX. Standard Brainfuck
sources validate/filter source and perform semantic optimization; canonical XAX
graphs validate BFX, import decisions and generate native code.

There is one portable **BFX** format for every optimization level, supported
source size and target. [The BFX specification](docs/02_BFX_CONTRACT.md) is the
single wire authority. The intentional migration uses a new four-byte magic
and one identifier; old layouts are rejected without fallback.

| Route | Raw-source budget | Instruction budget | Balanced depth |
|---|---:|---:|---:|
| Bounded `compiler/compiler.bf` | 65,533 bytes | 3,840 | 255 |
| Streaming BF with canonical XAX coordination | 1 MiB | 65,536 before packing | 32,768 |

These are fixed implementation budgets. [Dynamic workspace growth](docs/16_SCALABILITY.md)
remains open. The program tape has 65,536 wrapping byte cells, checked pointer
movement and EOF-as-zero. Only `><+-.,[]` execute; `#` is not a comment delimiter.

## Use the compiler

1. Frame bounded source as `length:u16le || source || 01` and execute
   [compiler.bf](compiler/compiler.bf) with a matching BF interpreter/native component.
2. Require successful termination and complete successful BFX. Save exact `.bfx` bytes.
3. Optionally run the bounded [clear](docs/10_CLEAR_OPTIMIZATION.md),
   [arithmetic](docs/12_ARITHMETIC_PACKING.md) and
   [movement](docs/14_MOVEMENT_PACKING.md) passes on validated records plus `01`.
4. Import with the [canonical XAX sources](https://github.com/MrxSiN/XAX/tree/42de0fc3ce31d4447f697e35a565cb4fdc489eda/compiler/integration/bfx),
   verify the complete store and generate native code for Android ARM64 or Windows x86-64.

For larger sources use [streaming compilation](docs/17_STREAMING_COMPILATION.md).
The optional [text framer](bootstrap/frame_source.bf) accepts 7,680 NUL-terminated
text bytes; binary source uses explicit lengths. See [bootstrap](docs/04_BOOTSTRAP.md)
and [integration](docs/03_XAX_INTEGRATION.md) for exact authority and buffer contracts.

Native components execute on both required targets. Builds still use unchanged
Windows-hosted generic Python XAX utilities; the native compiler driver remains
a prototype. Current tests and historical evidence are separated in
[status](docs/05_STATUS.md). The Android demo's earlier eight bounded application
cases do not establish general worker/cancellation integration.

BBC has no established overall performance lead. [Benchmarks](docs/08_BENCHMARKS.md),
[Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md), [measurement plan](docs/06_PERFORMANCE_PLAN.md),
[cold cache experiment](docs/18_BACKEND_BUILD_CACHE.md) and
[native driver follow-up](docs/19_NATIVE_DRIVER_FOLLOWUP.md) retain their scoped
results. M4 remains incomplete and M8 is not achieved. The installed .NET SDK
unblocks Brainfly correctness testing; no Brainfly timing score is established.
The BFX migration makes no performance claim.

The [modernization audit and fresh baseline](docs/20_MODERNIZATION.md) records
180 current-revision builds and native driver coverage. It confirms that startup
and XAX graph work dominate compilation; the single public entry point and
complete native driver remain implementation milestones.

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

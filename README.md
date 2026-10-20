# BBC — Ballsdeep Brainfuck Compiler

**A compiler written in Brainfuck, with native code generation through XAX.**

BBC reads Brainfuck source, checks it and produces a **BFX module** containing
the validated instructions. XAX turns that module into verified native code
for Android ARM64 or Windows x86-64.

[Get started](#use-the-compiler) · [Benchmarks](docs/08_BENCHMARKS.md) ·
[Project status](docs/05_STATUS.md) · [Documentation](#documentation)

> **Experimental:** native execution and frontend self-compilation are tested
> on both targets. Development and performance work are ongoing.

## How it works

```text
Brainfuck source → BBC → BFX module → XAX → Native program
```

All executable source in this repository is standard Brainfuck. The
[separate XAX project](https://github.com/MrxSiN/XAX/blob/0232858c7ad9be0e66b6feb300b4d0880bc276a5/docs/18_BFX_IMPORT.md)
handles graph verification, machine code and platform packaging.

For a small example, [decision.bf](examples/decision.bf) reads one input byte
and returns a permit/block result. The Android demo uses that result to show
or hide a sample row.

## What works today

| Feature | Tested support |
|---|---|
| Compiled frontend and decision programs | Android ARM64 and Windows x86-64 |
| Frontend self-compilation | Three identical rebuild generations on each target |
| Standalone executable | Android ARM64 and Windows x86-64 |
| Android demo app | Eight fixed, bounded permit, block and error cases |

The recorded builds use Windows-hosted XAX tools, including unchanged generic
Python bootstrap utilities. The native Windows build driver is still a
prototype. General Android decisions that may run indefinitely still need
worker integration. An optional Brainfuck pass now folds exact clear loops
and removes full wrapping arithmetic groups. A second optional pass packs
arithmetic into powers of two, with canonical XAX lowering.
See [status and evidence](docs/05_STATUS.md) for the full scope.

The latest frontend optimization passes three native rebuild generations
on Android and Windows. The [Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md)
explains the performance gaps, reproduced correctness defects and next steps.
The .NET 10 SDK is installed and Brainfly's JIT/NativeAOT routes pass the
twelve-program Windows correctness corpus; competitive timings are pending.

**Performance:** [Benchmarks](docs/08_BENCHMARKS.md) compare complete build time,
memory use, standalone execution and file size. The latest
[v3 follow-up](docs/13_V3_BENCHMARKS.md) measures the same sixteen programs,
including four clear-loop workloads, with pinned compiler configurations. BBC has no overall performance
lead; broader testing and optimization remain.

## Use the compiler

You need an external Brainfuck interpreter matching
[BBC's execution profile](docs/01_BRAINFUCK_PROFILE.md), plus XAX for native output.

1. **Prepare the input.** Frame the source with its byte length and a final
   terminator, as shown below. The [text framer](bootstrap/frame_source.bf)
   can prepare NUL-terminated text up to 7,680 bytes.
2. **Run BBC.** Execute [compiler.bf](compiler/compiler.bf) with that framed input.
3. **Save the result.** Check that the complete response reports success, then
   save its exact bytes as a `.bfx` file.
4. **Build native code.** Use the [XAX importer](https://github.com/MrxSiN/XAX/blob/0232858c7ad9be0e66b6feb300b4d0880bc276a5/compiler/integration/bfx/IMPORT.md)
   to import the module, verify the result and generate code for your target.

For the optional optimized route, validate the complete successful v1 module,
append byte `01`, and execute [optimize.bf](compiler/optimize.bf) before import.
Validate its complete successful v2 result and use the v2-capable importer.
The [v2 contract](docs/10_BFX_V2_CLEAR.md) and
[tape notes](compiler/optimize.bf.notes.md) specify this internal interface.

For compact arithmetic, validate that v2 result, append byte `01`, then run
[pack_arithmetic.bf](compiler/pack_arithmetic.bf). Validate and import its v3
result with the current consumer. The [v3 contract](docs/12_BFX_V3_ARITHMETIC.md)
records encoding, safety and native rebuild evidence. V1 remains available
independently; source acceptance limits are unchanged.

The binary input layout is:

```text
source length (2 bytes, little endian) | source bytes | terminator (hex 01)
```

BBC accepts up to **65,533 source bytes**, **3,840 instructions** and
**255 nested loops**. It uses 65,536 zeroed byte cells, wrapping arithmetic,
EOF as zero and checked pointer movement. Only `><+-.,[]` execute; `#` does
not introduce a comment.

Follow the [bootstrap guide](docs/04_BOOTSTRAP.md) for seed execution and native
rebuilds, or the [BFX contract](docs/02_BFX_CONTRACT.md) for exact input, output
and error handling.

## Documentation

| Read about | Guide |
|---|---|
| Language behavior and binary format | [Execution profile](docs/01_BRAINFUCK_PROFILE.md) · [BFX contract](docs/02_BFX_CONTRACT.md) |
| Native builds and Android integration | [XAX integration](docs/03_XAX_INTEGRATION.md) · [Bootstrap](docs/04_BOOTSTRAP.md) |
| Verified results and remaining work | [Project status](docs/05_STATUS.md) |
| Performance comparisons | [Benchmarks](docs/08_BENCHMARKS.md) · [V2 measurements](docs/11_V2_BENCHMARKS.md) · [Measurement plan](docs/06_PERFORMANCE_PLAN.md) |
| Competitor implementation and optimization priorities | [Brainfry analysis](docs/09_BRAINFRY_ANALYSIS.md) |
| Optional semantic optimization | [BFX v2](docs/10_BFX_V2_CLEAR.md) · [BFX v3](docs/12_BFX_V3_ARITHMETIC.md) · [V3 measurements](docs/13_V3_BENCHMARKS.md) · [Optimizer notes](compiler/optimize.bf.notes.md) · [Packer notes](compiler/pack_arithmetic.bf.notes.md) |
| Compiler implementation | [Algorithm and tape layout](compiler/compiler.bf.notes.md) · [Optimization proofs](docs/07_OPTIMIZATION_PROOFS.md) |
| Tests | [Fixtures and verification](tests/bfx/README.md) |

Independent interpreters and test drivers live outside this repository.
Generated artifacts belong in ignored `build/`; recorded results live in
[`evidence/`](evidence/).

[MIT license](LICENSE) · [Maintenance rules](AGENT.md)

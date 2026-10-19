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
[separate XAX project](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/docs/18_BFX_IMPORT.md)
handles graph verification, machine code and platform packaging.

For a small example, [decision.bf](examples/decision.bf) reads one input byte
and returns a permit/block result. The Android demo uses that result to show
or hide a sample row.

## What works today

| Feature | Tested support |
|---|---|
| Compiled frontend and decision programs | Android ARM64 and Windows x86-64 |
| Frontend self-compilation | Three identical rebuild generations on each target |
| Standalone executable | Android ARM64 |
| Android demo app | Eight fixed, bounded permit, block and error cases |

The recorded builds use Windows-hosted XAX tools, including unchanged generic
Python bootstrap utilities. The native Windows build driver is still a
prototype. General Android decisions that may run indefinitely still need
worker integration; source-program folding and loop optimization remain
unimplemented. See [status and evidence](docs/05_STATUS.md) for the full scope.

**Performance:** BBC's standalone Android programs beat the pinned Awib build
in the twelve-program process test; brainfry remains faster. This does not
establish an overall performance lead. The [benchmark guide](docs/08_BENCHMARKS.md)
compares elapsed time and file size, with the test conditions and raw evidence.

## Use the compiler

You need an external Brainfuck interpreter matching
[BBC's execution profile](docs/01_BRAINFUCK_PROFILE.md), plus XAX for native output.

1. **Prepare the input.** Frame the source with its byte length and a final
   terminator, as shown below. The [text framer](bootstrap/frame_source.bf)
   can prepare NUL-terminated text up to 7,680 bytes.
2. **Run BBC.** Execute [compiler.bf](compiler/compiler.bf) with that framed input.
3. **Save the result.** Check that the complete response reports success, then
   save its exact bytes as a `.bfx` file.
4. **Build native code.** Use the [XAX importer](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/IMPORT.md)
   to import the module, verify the result and generate code for your target.

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
| Performance comparisons | [Benchmarks](docs/08_BENCHMARKS.md) · [Measurement plan](docs/06_PERFORMANCE_PLAN.md) |
| Compiler implementation | [Algorithm and tape layout](compiler/compiler.bf.notes.md) · [Optimization proofs](docs/07_OPTIMIZATION_PROOFS.md) |
| Tests | [Fixtures and verification](tests/bfx/README.md) |

Independent interpreters and test drivers live outside this repository.
Generated artifacts belong in ignored `build/`; recorded results live in
[`evidence/`](evidence/).

[MIT license](LICENSE) · [Maintenance rules](AGENT.md)

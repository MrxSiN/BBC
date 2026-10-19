# BFX — Ballsdeep Brainfuck XAX

BBC is the Brainfuck compiler frontend. It compiles human-authored decision
logic into **BFX v1** modules; XAX imports those modules as verified canonical
graphs and supplies native code, application behavior and platform packaging.
All executable implementation in this repository is standard Brainfuck.

The frontend, BFX importer and native frontend rebuild cycle execute on
**Android ARM64 and Windows x86-64**. The Android decision app shows or hides
a sample row from the compiled Brainfuck result. Native lowering and packaging
use unchanged Windows-hosted XAX bootstrap tools.

| Verified work | Result |
|---|---|
| Record validation | 393 decoder cases and 393 complete-importer cases on each platform |
| Native decisions | 89 Windows decision calls across 13 emitted modules |
| Frontend rebuilds | Three generations per platform with identical BFX, stores and native artifacts; eight Android fixtures per generation |
| Android application | Eight permit, block and error cases on Pixel 8 Pro |

[Status and evidence](docs/STATUS.md) distinguish these results from remaining
work: BBC optimization, Linux execution and Android-hosted XAX lowering.
No runtime speed advantage is claimed.

## Use the compiler

1. Frame source as `source_length:u16le || source_bytes || 01`.
2. Execute [compiler/compiler.bf](compiler/compiler.bf) with an independent
   interpreter implementing [the Brainfuck profile](docs/BRAINFUCK_PROFILE.md).
3. Accept a complete successful [BFX response](docs/BFX_CONTRACT.md) and save
   its bytes as `.bfx`.
4. Pass the module to the [canonical XAX importer](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/IMPORT.md),
   verify the emitted store and lower it through XAX for the selected target.

The frontend accepts 65,535 raw source bytes, 3,840 filtered instructions and
255 nested loops. It runs on 65,536 zeroed wrapping byte cells with EOF zero
and checked pointer movement. Only `><+-.,[]` execute; a hash character does
not hide commands in annotations. See [bootstrap](docs/BOOTSTRAP.md) for
source framing and the native rebuild cycle.

## Repository guide

| Path | Purpose |
|---|---|
| [compiler/compiler.bf](compiler/compiler.bf) | Validate framed source and emit BFX |
| [compiler/compiler.bf.notes.md](compiler/compiler.bf.notes.md) | Frontend algorithm, tape layout and hashes |
| [bootstrap/frame_source.bf](bootstrap/frame_source.bf) | Frame NUL-terminated text source |
| [examples/decision.bf](examples/decision.bf) | Permit/block decision from one input flag |
| [tests/bfx/README.md](tests/bfx/README.md) | Exact fixtures and verification procedure |
| [docs/BFX_CONTRACT.md](docs/BFX_CONTRACT.md) | BFX framing, version and compiler errors |
| [docs/BRAINFUCK_PROFILE.md](docs/BRAINFUCK_PROFILE.md) | Instruction semantics and native decision ABI |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | Seed execution and repeatable native frontend rebuilds |
| [docs/XAX_INTEGRATION.md](docs/XAX_INTEGRATION.md) | Pinned XAX sources, importer ABI and Android application |
| [docs/STATUS.md](docs/STATUS.md) | Current support, evidence and remaining work |
| [AGENT.md](AGENT.md) | Maintenance rules |

XAX implementation lives in the [separate XAX repository](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/docs/18_BFX_IMPORT.md).
Canonical graphs are its source. Generic Python verifier, transaction, native
lowering, APK and signing utilities remain disclosed build dependencies.
Independent interpreters and verification drivers stay outside this repository;
generated build artifacts stay in ignored `build/`.

[MIT license](LICENSE). Compiler jokes are cheap; native proof needs hashes.

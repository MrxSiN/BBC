# BBC — Ballsdeep Brainfuck Compiler

BBC is the Brainfuck compiler frontend. It compiles human-authored decision
logic into **BFX v1** modules; XAX imports those modules as verified canonical
graphs and supplies native code, application behavior and platform packaging.
All executable implementation in this repository is standard Brainfuck.

The BFX importer and optimized frontend rebuild cycle have executed on
**Android ARM64 and Windows x86-64**.
The Android decision app shows or hides
a sample row from the compiled Brainfuck result. Native lowering and packaging
use unchanged Windows-hosted XAX bootstrap tools.

| Verified work | Result |
|---|---|
| Record validation | 393 decoder cases and 393 complete-importer cases on each platform |
| Standalone Android process | Canonical XAX executable host; faster than pinned Awib in the twelve-program process comparison; brainfry remains faster |
| Native decisions | Current importer: 380 checks across 20 modules on each required target; full tape/output match an independent interpreter |
| Frontend rebuilds | Current importer: three generations per platform, twenty fixture/own-source/boundary checks per generation |
| Frontend verification | 131,072 counter states, 512 decoder states, 42 interpreter checks and 530 native byte/property cases |
| Android application | Eight permit, block and error cases on Pixel 8 Pro |

[Status and evidence](docs/05_STATUS.md) distinguish these results from remaining
work: general unbounded-decision worker integration and source-program optimization.
Android and Windows are required; Linux is optional.
The [competitor pilot](docs/08_BENCHMARKS.md) measures Awib and brainfry on both
required targets and records coverage for all eight projects. The competitive
objective remains unachieved; the [comparison plan](docs/06_PERFORMANCE_PLAN.md)
defines the remaining gates. The pilot's process, test-build and size aggregates
favor both measured competitors. The separate standalone Android follow-up
averages **13.44 ms for BBC versus 31.08 ms for Awib**; brainfry still wins
its pairing, **7.47 ms versus BBC's 12.50 ms**. This is a scoped process
result, with steady-state competitor comparisons and RAM still unmeasured.
The [verification follow-up](docs/08_BENCHMARKS.md#verification-cost-diagnosis)
separates cold helper setup from graph checks and measures reuse of XAX's
existing proof cache. Its warm-stage gains are not new competitor results.
The [standalone Windows hashing host](docs/03_XAX_INTEGRATION.md#windows-native-hashing-host)
now executes the existing XAX BLAKE3 graph with verified Windows buffer and
stream handling. It passed 139 successful inputs and five failure cases;
the compiler's common helper loader still needs integration. A separate
[Windows native driver prototype](docs/03_XAX_INTEGRATION.md#windows-native-driver-prototype)
now verifies the BBC compiler and importer stores, resolves a request, replays
small edits and builds a runnable PE fixture. Its 212-case corpus retains four
declines and one diagnostic mismatch. This is a bounded native route; full BBC
DLL compilation remains on the bootstrap path.
[P0 proofs and measurements](docs/07_OPTIMIZATION_PROOFS.md) cover
BBC's grouped source-byte counter and single-copy decoder. The decoder's local
frontend speedups are 2.23x on Android and 1.94x on Windows against the preceding
counter frontend. No application or competitor speed advantage
is claimed.

The [eight-byte tape reset](docs/07_OPTIMIZATION_PROOFS.md#xax-eight-byte-tape-reset)
now improves repeated native calls while preserving the complete 65,536-byte
reset. The [new measurements](docs/08_BENCHMARKS.md#eight-byte-tape-reset)
average 6.168 to 5.624 ms per call on Windows and 1.360 to 1.302 ms on Android
across the fixed corpus. The later [standalone Android package](docs/08_BENCHMARKS.md#standalone-android-process)
removes the fixed shared-library test host and improves the process comparison
against Awib. These results change no end-to-end compiler or RAM claim.

## Use the compiler

1. Frame source as `source_length:u16le || source_bytes || 01`.
2. Execute [compiler/compiler.bf](compiler/compiler.bf) with an independent
   interpreter implementing [the Brainfuck profile](docs/01_BRAINFUCK_PROFILE.md).
3. Accept a complete successful [BFX response](docs/02_BFX_CONTRACT.md) and save
   its bytes as `.bfx`.
4. Pass the module to the [canonical XAX importer](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/IMPORT.md),
   verify the emitted store and lower it through XAX for the selected target.

The frontend accepts 65,533 raw source bytes, 3,840 filtered instructions and
255 nested loops. It runs on 65,536 zeroed wrapping byte cells with EOF zero
and checked pointer movement. Only `><+-.,[]` execute; a hash character does
not hide commands in annotations. See [bootstrap](docs/04_BOOTSTRAP.md) for
source framing and the native rebuild cycle.

## Repository guide

| Path | Purpose |
|---|---|
| [compiler/compiler.bf](compiler/compiler.bf) | Validate framed source and emit BFX |
| [compiler/compiler.bf.notes.md](compiler/compiler.bf.notes.md) | Frontend algorithm, tape layout and hashes |
| [bootstrap/frame_source.bf](bootstrap/frame_source.bf) | Frame NUL-terminated text source |
| [examples/decision.bf](examples/decision.bf) | Permit/block decision from one input flag |
| [tests/bfx/README.md](tests/bfx/README.md) | Exact fixtures and verification procedure |
| [docs/01_BRAINFUCK_PROFILE.md](docs/01_BRAINFUCK_PROFILE.md) | Instruction semantics and native decision ABI |
| [docs/02_BFX_CONTRACT.md](docs/02_BFX_CONTRACT.md) | BFX framing, version and compiler errors |
| [docs/03_XAX_INTEGRATION.md](docs/03_XAX_INTEGRATION.md) | Pinned XAX sources, importer ABI and Android application |
| [docs/04_BOOTSTRAP.md](docs/04_BOOTSTRAP.md) | Seed execution and repeatable native frontend rebuilds |
| [docs/05_STATUS.md](docs/05_STATUS.md) | Current support, evidence and remaining work |
| [docs/06_PERFORMANCE_PLAN.md](docs/06_PERFORMANCE_PLAN.md) | Comparator coverage and measurement gates |
| [docs/07_OPTIMIZATION_PROOFS.md](docs/07_OPTIMIZATION_PROOFS.md) | Frontend counter invariant, finite-state checks and local measurements |
| [docs/08_BENCHMARKS.md](docs/08_BENCHMARKS.md) | Pinned competitor pilot, raw results, exclusions and remaining gates |
| [AGENT.md](AGENT.md) | Maintenance rules |

XAX implementation lives in the [separate XAX repository](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/docs/18_BFX_IMPORT.md).
Canonical graphs are its source. Generic Python verifier, transaction, native
lowering, APK and signing utilities remain disclosed build dependencies.
Independent interpreters and verification drivers stay outside this repository;
generated build artifacts stay in ignored `build/`.

Retired-format reports and generated artifacts have been removed from the
working repository after archiving outside it; see
[cleanup evidence](evidence/format_cleanup.json). The reusable Brainfuck framer
and current fixtures remain in place. Historical bootstrap provenance inside
immutable BFX evidence is retained without relabeling old measurements.

[MIT license](LICENSE). Compiler jokes are cheap; native proof needs hashes.

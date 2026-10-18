# BBC — Brainfuck Ballsdeep Compiler

Human decisions in Brainfuck. AI application logic in XAX. The frontend is
Brainfuck; XAX owns native code generation and platform packaging.

**PROTOTYPE:** the frontend and Brainfuck bootstrap framing execute under two
independent interpreters. The XAX BBX importer constructs verified graphs and
passes ARM64 instruction simulation. **Android app integration and native
frontend self-hosting are EXECUTED** on a Pixel 8 Pro: permit/block/error UI
actions and three byte-identical rebuild generations passed. Windows x86-64
native decision and frontend component execution also passed. Linux x86-64
execution remains unverified because no host is available. XAX's compiler host
uses Python bootstrap helpers; the combined toolchain is not Brainfuck-only.

## The useful bits

| Path | Purpose |
|---|---|
| [compiler/compiler.bf](compiler/compiler.bf) | Validate source and emit a portable BBX module |
| [bootstrap/frame_source.bf](bootstrap/frame_source.bf) | Frame the compiler's text source using ordinary Brainfuck |
| [examples/decision.bf](examples/decision.bf) | Emit permit or block from one input flag |
| [tests/](tests/bbx/README.md) | Small Brainfuck programs and exact binary fixtures |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | Cold bootstrap procedure, limits and external dependencies |
| [docs/BBX_CONTRACT.md](docs/BBX_CONTRACT.md) | Precise compiler input/output framing |
| [docs/BRAINFUCK_PROFILE.md](docs/BRAINFUCK_PROFILE.md) | Unchanged eight-command execution semantics |
| [docs/XAX_INTEGRATION.md](docs/XAX_INTEGRATION.md) | Executed Android app, XAX interfaces and reproduction |
| [docs/STATUS.md](docs/STATUS.md) | Executed evidence and unimplemented milestones |

The compiler has 2,455 instructions. It accepts 65,535 raw source bytes,
3,840 filtered instructions and nesting depth 255. Tape is 65,536 zeroed
wrapping byte cells; input EOF reads zero and out-of-range pointers fail.
Only `><+-.,[]` execute. A hash character does not hide commands in comments.

All implementation and executable tests in this repository are `.bf`.
There are no shell/Python/C bootstrap programs, native backends, vendored
apps or in-repository test harnesses. Generated modules belong in ignored
`build/`. An independent interpreter, external verification tools and the
separate XAX project are disclosed dependencies. Brainfuck does not acquire
filesystem access, processes or Android APIs by changing its file extension.

The obsolete repository contents, including uncommitted changes, were saved
in a verified external recovery archive before removal; see
[the cleanup record](evidence/repository_cleanup.json). Those files are not a
build dependency. The combined BBC/XAX toolchain is not Brainfuck-only.

[MIT license](LICENSE). Compiler jokes are cheap; native proof now has hashes.

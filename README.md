# BFX — Ballsdeep Brainfuck XAX

Human decisions in Brainfuck. AI application logic in XAX. BBC is the
Brainfuck frontend; BFX is its portable handoff to the XAX native backend.

**BFX import is implemented as canonical XAX.** The frontend emits BFX v1,
using `42 46 58 01`, and fixtures use `.bfx`. The XAX importer produces complete
canonical decision stores. It passed 393 record cases, 89 native Windows
decision cases and three exact frontend rebuild generations. The canonical
Android app passed eight Activity cases on Pixel 8 Pro. Generic Python
bootstrap tools remain build dependencies. The importer and three frontend
rebuild generations also execute on Android; see [status](docs/STATUS.md).

| Path | Purpose |
|---|---|
| [compiler/compiler.bf](compiler/compiler.bf) | Brainfuck frontend; validate framed source and emit BFX |
| [bootstrap/frame_source.bf](bootstrap/frame_source.bf) | Brainfuck source framing |
| [examples/decision.bf](examples/decision.bf) | Permit/block decision from one input flag |
| [tests/bfx/README.md](tests/bfx/README.md) | Exact request/response and profile fixtures |
| [docs/BFX_CONTRACT.md](docs/BFX_CONTRACT.md) | Framing, versioning and compatibility |
| [docs/BRAINFUCK_PROFILE.md](docs/BRAINFUCK_PROFILE.md) | Eight-command execution semantics and decision ABI |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | Bootstrap limits and dependencies |
| [docs/XAX_INTEGRATION.md](docs/XAX_INTEGRATION.md) | Canonical XAX importer and Android app |
| [docs/STATUS.md](docs/STATUS.md) | Current implementation and verified results |

The frontend accepts 65,535 raw source bytes, 3,840 filtered instructions and
255 nested loops. Its 2,455 instructions run on 65,536 zeroed wrapping byte
cells, with EOF zero and checked pointer movement. Only `><+-.,[]` execute;
a hash character does not hide commands in annotations.

All executable implementation and test programs in this repository are `.bf`.
XAX integration lives in `D:\GitHub\XAX`; its new decoder source is
`compiler/integration/bfx/bfx.xax`. External interpreters, verification drivers
and unchanged XAX Python bootstrap/lowering utilities remain disclosed
dependencies. The whole toolchain is not claimed to be XAX-only or
Brainfuck-only. Generated artifacts stay in ignored `build/`.

[MIT license](LICENSE). Compiler jokes are cheap; native proof needs hashes.

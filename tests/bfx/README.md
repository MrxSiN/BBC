# Binary fixtures and verification

Each `.request` is compiler input and its matching `.bfx` is exact expected
stdout. `truncated.request` lacks the required terminator; `raw-zero` includes
literal NUL and FF. See [the contract](../../docs/BFX_CONTRACT.md).
Modules must contain BFX magic as well as use the `.bfx` extension.

The `.input`/`.output` pairs run `../basic.bf`, `../loops.bf` and
`../../examples/decision.bf` (permit/block). `../bounds.bf` and
`../bounds_right.bf` must fail on executed out-of-range tape movement.
The `../bootstrap/` fixtures exercise the standard Brainfuck framer.
Fixture bytes are protected from checkout line-ending conversion.

The current external seed verifier is
`C:\Users\User\.codex\visualizations\2026\10\19\01a151a5-3e3d-7680-a6b1-3dd4bd01e4c9\verify-bfx.ps1`.
It uses a .NET interpreter with checked 65,536-cell tape, wrapping bytes and
EOF zero. It executes the BF framer/compiler, compares all eight BFX fixtures,
checks limits, and compares interpreted own-source output. It is external
development tooling, not a production compiler or repository implementation.
A different machine can use any independent interpreter with the same profile.

The new XAX decoder has static input/result/loop-pair data in the separate
XAX repository at `compiler/integration/bfx/decoder_cases.json`. External
native-call drivers exercise that canonical graph without supplying any
validation or translation implementation. Current results and tool hashes:
[BFX evidence](../../evidence/bfx_migration.json).

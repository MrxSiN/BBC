# Binary fixtures and external verification

Each `bbx/*.request` is complete compiler input and its `.bbx` is exact
expected stdout. `truncated.request` lacks its terminator. `raw-zero` contains
literal NUL and FF bytes. `safe-annotations` checks ordinary ignored text.
See [the contract](../../docs/BBX_CONTRACT.md).

The `.input`/`.output` pairs run `../basic.bf`, `../loops.bf` and
`../../examples/decision.bf` (permit/block). `../bounds.bf` and
`../bounds_right.bf` must fail on executed tape movement, without output.

The `../bootstrap/*.input`/`.output` pairs run
[the BF framer](../../bootstrap/frame_source.bf): empty text, annotated text,
and explicit NUL termination. [BOOTSTRAP.md](../../docs/BOOTSTRAP.md) explains
its text-only boundary and complete bootstrap sequence. Fixture byte contents
are protected from checkout line-ending conversion by `.gitattributes`.

No verifier implementation is kept in this repository. Session development
tools are external:

- `C:\Users\SiN\.codex\visualizations\2026\10\18\01a14f2c-277c-7330-85c1-2cd5abe8d120\bbc-verify.ps1`
- `C:\Users\SiN\.codex\visualizations\2026\10\18\01a14f2c-277c-7330-85c1-2cd5abe8d120\bbc-reference-verify.py`

Run the PowerShell driver first, then the Python driver with Python 3.12.
The first uses .NET Add-Type for an independent eight-command interpreter
with wrapping bytes, checked tape and zero-on-EOF. It emits ignored
`build/bbx/compiler.bbx`, `decision.bbx` and `bootstrap.bbx` **by executing
Brainfuck**, then records exact comparisons. Its expected-output oracle is
used only for testing. The second uses external `bbc_reference.py`, preserved
from the retired repository reference interpreter, to compare independent
results. Neither tool is a production compiler or required runtime.

The reference and driver hashes are recorded in
[frontend evidence](../../evidence/bbx_frontend.json),
[bootstrap evidence](../../evidence/bbx_bootstrap.json) and
[Python evidence](../../evidence/bbx_reference.json).
A different machine may use any independent interpreter conforming to the
profile to run the static fixtures. Extended randomized/boundary tests need
the separately supplied drivers or an equivalent external verifier. The
recovery archive is never used as part of bootstrap or verification.

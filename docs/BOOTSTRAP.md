# Brainfuck bootstrap

Status: EXECUTED under independent interpreters on Windows x86-64 and natively
on Android ARM64. Three frontend rebuild generations agree exactly, with an
external XAX backend cross-compiling on Windows.

## What runs

All repository-owned bootstrap logic is in
[bootstrap/frame_source.bf](../bootstrap/frame_source.bf) and
[compiler/compiler.bf](../compiler/compiler.bf). There is no C seed, Python
framer, shell builder, machine-code emitter or test harness in this repository.
An external conforming interpreter executes the first Brainfuck program.
That cold execution dependency is explicitly permitted by the project prompt;
Brainfuck itself does not open files or launch processes.

1. Supply the exact bytes of `compiler/compiler.bf` as input to
   `bootstrap/frame_source.bf`, executed by an independent interpreter.
2. Pass its complete stdout to `compiler/compiler.bf`, again executed by the
   seed. The frontend performs the validation and emits its own BBX module.
3. Accept only a complete successful response under
   [BBX_CONTRACT.md](BBX_CONTRACT.md). A partial record is not an artifact.
4. For the current interpreted check, execute the emitted instruction payload
   under the seed with the same BF-produced input frame. Its output must be
   byte-identical. This is interpreter agreement, not native self-hosting.
5. XAX imports that BBX module and emits the native frontend component. Run
   it on Android with the same BF-produced request, import its new BBX output,
   and rebuild through XAX. Repeat the native execution and rebuild three times.
   The recorded run obtained identical BBX records, canonical graphs and ELF
   libraries in every generation. This step has now executed.

The same sequence compiles the bootstrap framer. Executing its emitted
instruction payload under the seed reproduces the original input frame.
External tooling may copy buffers and inspect output; it must not replace the
Brainfuck framing, validation or translation algorithms.

## Text framing contract

The framer reads bytes until the first NUL or physical EOF, and emits:

`text_length:u16le || original_text_bytes || 01`

It accepts at most **7,680 bytes**, including whitespace and safe annotations.
If more text arrives before termination, it consumes to termination and emits
**no bytes**. A successful frame is always at least three bytes. Feeding an
empty failed result to the frontend deterministically produces framing error
1; callers must not treat empty stdout as a valid empty-source frame.

The NUL terminator is a bootstrap transport restriction, not a source-language
change. Use this stage for the canonical NUL-free `.bf` text. Embedded NUL ends
this text input; it cannot be distinguished from physical EOF under standard
zero-on-EOF semantics. For arbitrary binary source, including embedded NUL,
supply the general known-length BBX request instead. The frontend retains its
full 65,535-byte binary source contract and literal-zero tests.

The framer uses eight-cell slots, with cells 0 through 7 kept as a sentinel.
Each stored slot holds a marker, original byte, low/high count and scratch.
A count-high of thirty refuses further storage. The last working slot starts
at `8 * (7680 + 1) = 61,448` and ends at 61,455. No overflow input advances the
working slot. Output begins only after the limit check finishes.

Current source: 1,207 bytes, 302 instructions; SHA-256
`1b1f7d90c17414417c8622303244d424ccf6e30704ee6165c77f3161e0bd454f`.
The compiler text is 4,531 bytes and therefore fits. Its generated BBX record
is 2,462 bytes. No generated artifact is authoritative source.

## Independent checks

[Bootstrap evidence](../evidence/bbx_bootstrap.json) records count carry,
7,679/7,680/7,681 boundaries, large rejection, every nonzero byte, NUL
termination, exact fixtures, compiler framing and interpreted round trips.
The Python reference independently checks fixture and boundary agreement.
[Fixture instructions](../tests/bbx/README.md) identify the external tools.
These tools are development-only dependencies; the recovery archive is not
used to execute the current bootstrap.

## Native Android cycle

[Native self-hosting evidence](../evidence/bbx_selfhost_android.json) records
22 checks on a Pixel 8 Pro, Android 17/API 37, arm64-v8a. The BF framer executes
natively to frame both authoritative sources. The native compiler reproduces
its own BBX in three generations, reproduces the bootstrap module, and agrees
with all eight exact fixtures under the initial and final native libraries.
Each rebuild emits an identical 66,504-byte frontend shared library, SHA-256
`0d3505127191c92d7639bf16f696f19602fddd174fcb5bb09b409a95e44e36e5`.

External NDK C loaders perform file/buffer transport and output-canary checks;
they contain no source filtering, framing, validation, translation or BF VM.
The executable framing and compilation remain the two BF programs. The loader
uses trusted initialized views for the internal component call, not an
untrusted production pointer interface. These tools stay outside this repo.

This proves **Brainfuck frontend self-hosting with an XAX backend**. XAX's
backend used Python bootstrap helpers on Windows; it was not self-hosted on
Android. The tested native components use 65,536-byte input/output views: the
canonical sources fit; the full 65,538-byte maximum general source frame is
outside that configured component bound. No Linux native frontend cycle or
performance advantage is claimed.

## Native Windows frontend cycle

[Windows evidence](../evidence/bbx_windows.json) records 22 native checks:
11 decision/profile calls, three identical BBX/graph/PE compiler generations,
and all eight frontend fixtures. It uses the same seed BBX and BF-produced
source frame as the Android cycle. The native compiler DLL is 701,952 bytes;
external ctypes only supplies buffers and calls the Win64 component.
Windows execution of the bootstrap framer itself was not tested. XAX backend
self-hosting is not claimed; its Windows Python helpers remain external.

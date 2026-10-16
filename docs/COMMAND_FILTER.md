# Comment filtering — an actual Brainfuck experiment

The production compiler still stores every decoded source byte. Comments take buffer space and become 32-byte NOP slots. That is the remaining problem, not a secret ninth instruction.

`experiments/command_filter.bf` is a **separate 862-command Brainfuck program**. It reads a one-byte length followed by that many raw bytes (0–255), then writes only `><+-.,[]`. It uses four Brainfuck tape cells: count, input, comparison scratch, and a zero-on-exit match flag. The matching byte is output unchanged. All other bytes disappear, including NUL and `0xFF`.

This is regular Brainfuck, not a DSL or a preprocessor the shipping compiler secretly calls. The native experiment is compiled using `compiler/core.bf`'s existing self-hosted ELF backend.

## What was tested

Run:

```sh
python3 tests/verify_command_filter.py
```

The script compiles the raw BF filter to a native ELF, checks the emitted machine-code templates and branch displacements, then executes **135 input cases**. Every possible input byte is covered. Additional randomized cases include embedded zero bytes, `0xFF`, ASCII prose, and repeated real Brainfuck instructions. Two independently written BF interpreters spot-check **24** of the cases.

Machine-readable results are in [`../evidence/command_filter.json`](../evidence/command_filter.json).

## Why it is not installed in core.bf

The compiler's input decoder, four-cell source buffer, size scanner, bracket metadata, and 32-byte branch displacements currently use **decoded byte positions**, not compacted instruction positions. Pasting the filter into one stage would leave the others lying about offsets. It would also exceed the compiler's current **112-byte self-compilation headroom** without a separate size reduction.

Integration needs one consistent stored-command count, correct handling of byte-stuffed compiler input, explicit buffer exhaustion behavior, and a fresh Stage 0–2 self-hosting cycle. The standalone filter uses length framing for the experiment; it does not replace the compiler's `FF01`/`FF02` transport.

**Status: EXECUTED experiment, UNIMPLEMENTED production filter.** A lexer working in isolation is useful. Calling it an optimizer already would be a bit ambitious.

## Iteration 13 follow-up

An EOF-streaming version now speaks the real byte-stuffed compiler protocol and reports malformed escapes, including a truncated `FF`. The streamed version is now 816 BF commands (1,031 originally); it can be chained to the BF compiler for test-only comment-independent ELF output and self-compilation, but it is not an integrated frontend. See [`STREAM_FILTER.md`](STREAM_FILTER.md).

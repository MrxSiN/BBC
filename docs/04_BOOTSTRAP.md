# 🥚 Bootstrap

> How a Brainfuck compiler written in Brainfuck gets born without cheating.

All BBC implementation is plain Brainfuck. [`compiler.bf`](../compiler/compiler.bf)
is the private bounded seed. The public frontend is
[`stream_chunks.bf`](../compiler/stream_chunks.bf) plus XAX coordination. Every
path speaks the one [BFX format](02_BFX_CONTRACT.md).

---

## 🔁 The loop

1. Run the BF frontend under an independent interpreter that follows the
   [profile](01_BRAINFUCK_PROFILE.md), feeding it its own source.
2. Require a complete, successful BFX record with exactly the filtered source bytes.
3. Run that output under the interpreter and require the same result again.
   This proves the seed agrees with itself; native execution comes next.
4. Import through the XAX importer, fully verify the store, then lower and
   package it with the unchanged generic XAX SDK.
5. Run the native frontend on the target and require the exact seed record.
6. Repeat import, verification and lowering. Record, store and native bytes must
   match across generations on each target.

The [public entry](21_UNIFIED_COMPILATION.md) runs the O0/O1 passes for you.
The pieces below are private bootstrap and reference parts.

- **Bounded passes** (clear, arithmetic and movement packing) each take a validated
  success record of up to 3,840 instructions plus `01`, and emit BFX again.
  Never feed them a failure. Validate every result.
- **Streaming packing** handles bigger programs and already-packed opcodes.
  Its private packet core is bootstrapped through native BF and XAX import, then
  specialized by exact-root graph transactions.

---

## ✏️ Text framer

[`frame_source.bf`](../bootstrap/frame_source.bf) turns text into a bounded request.

- Reads up to 7,680 bytes, ending at NUL or end of file.
- Writes `length:u16 | text | 01`.
- An embedded NUL ends the text. Oversized input is read and dropped, and nothing is written.
- Binary sources use the explicit length request instead.

Tape use: the framer's last working cell is 61,455 (8-cell slots). The bounded
compiler's is 61,471 (16-cell slots). Comments must not contain the eight
instruction characters; nothing strips them.

---

## ⚖️ Who is allowed to do what

- The generic XAX SDK tools verify, lower and package.
- ctypes and NDK transports only allocate, copy bytes and call exports. None of
  them parses Brainfuck, decodes BFX or generates code.
- Native component execution on Android is not the same as running the compiler
  on Android.

---

## 📎 Evidence

- [Unified compilation](../evidence/unified_compilation.json): three identical
  `stream_chunks` own-source generations, the exact imported BF core and identical
  per-target images. Each Android generation runs and imports its own record.
- Older [capacity-flag](../evidence/frontend_capacity_gate.json) and
  [wide bootstrap](../evidence/wide_bootstrap.json) reports stay byte-identical,
  with their original source and wire identities. Don't cite them for today's sources.

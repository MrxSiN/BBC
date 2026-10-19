# Brainfuck bootstrap

BBC's bootstrap algorithms remain ordinary Brainfuck in
[bootstrap/frame_source.bf](../bootstrap/frame_source.bf) and
[compiler/compiler.bf](../compiler/compiler.bf). BFX is generated data;
Brainfuck gains no filesystem or platform commands from its extension.

## Current BFX seed path

1. Execute the framer under an independent interpreter with the exact compiler
   source bytes as input.
2. Execute the compiler with the resulting frame and capture its complete
   stdout. Accept only a successful [BFX response](BFX_CONTRACT.md).
3. Execute that response's instruction payload under the same interpreter
   with the same source frame. Require byte-identical output.
4. Execute the canonical XAX importer to produce a decision store, then use
   generic XAX native lowering. Three Windows frontend generations now agree
   through this path. See
   [native import evidence](../evidence/bfx_xax_import.json).

The current external .NET interpreter passed 21 fixture/bootstrap/boundary
checks, including interpreted own-source agreement. The framer preserves
bytes, count carry and termination in the tested canonical inputs. The
frontend retains its 65,535-byte general source frame, 3,840-command and
255-nesting limits. See [current evidence](../evidence/bfx_migration.json).

## Text framing contract

The framer reads until NUL or physical EOF and emits:

`text_length:u16le || original_text_bytes || 01`

It accepts at most **7,680 bytes**, including safe annotations and whitespace.
Oversized input is consumed to termination and produces no bytes. Empty
successful text produces a three-byte frame. Embedded NUL terminates this
bootstrap transport; arbitrary binary source must use the general known-length
compiler request. This restriction does not change Brainfuck semantics.

Eight-cell slots start after a zero sentinel. The last working slot starts
at cell 61,448 and ends at 61,455. Rejected input does not advance that slot.
The compiler uses sixteen-cell slots; its last working cell is 61,471.

Framer source: 1,207 bytes, 302 instructions, SHA-256
`1b1f7d90c17414417c8622303244d424ccf6e30704ee6165c77f3161e0bd454f`.
Compiler source: 4,531 bytes, 2,455 instructions. Its own BFX record is
2,462 bytes. Current compiler hashes are in [the tape notes](../compiler/compiler.bf.notes.md).

## Native frontend verification

The canonical XAX importer passes a three-generation Windows cycle with
byte-identical BFX, canonical stores and native DLLs. Generic Python backend
utilities remain build dependencies. External ctypes and Android C transports
only supply buffers and call native code; they contain no compiler, source
framing or Brainfuck interpreter.

The BFX importer and native Brainfuck frontend also execute on Android ARM64.
Three generations produce identical BFX, canonical stores and ELF libraries;
eight exact fixtures pass in every generation. Native lowering remains on the
Windows build host. See [Android import evidence](../evidence/bfx_android_importer.json).
No Linux execution or timing advantage is claimed.

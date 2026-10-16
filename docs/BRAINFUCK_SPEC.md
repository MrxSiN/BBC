# Brainfuck execution contract — V0

Eight commands. The rest of the pain is implementation detail.

| Property | This compiler's rule |
|---|---|
| Commands | `><+-.,[]` |
| Cell | Unsigned byte; arithmetic wraps modulo 256 |
| Tape | 65,536 initially zero bytes |
| Pointer | Starts at cell zero; out-of-range move exits(2) |
| `,` | Raw-byte input; EOF sets current cell to zero |
| `.` | One raw-byte output |
| `[` / `]` | Current cell zero-test / loop back |
| Bad brackets | Reject compilation; no accepted ELF |
| Compiler source limit | **16,128 executable commands, comments excluded** |
| Maximum nested brackets | 255 |

Non-instruction bytes are removed inside the standard Brainfuck decoder. They do not occupy compiler source-buffer records or native code slots. Escaped raw `00` and `FF` are ignored as source characters. Ignored text still consumes input-processing time. The first validated compiler with this behavior is Iteration 19.

## Source byte transport

The compiler reads a byte stream on stdin. Brainfuck input under this profile cannot distinguish byte NUL from physical EOF, so the optional transport layer stuffs input bytes:

```text
raw 00 -> FF 01
raw FF -> FF 02
other bytes -> unchanged
physical EOF -> end of compiler source
```

Brainfuck code validates those escapes and decodes them. The Python adapter only encodes byte transport and writes an accepted result to disk. It does not parse brackets or generate x86 machine code. The 16,128 ceiling applies after Brainfuck-owned filtering, to executable commands only.

The compiler's stdout format is `ELF artifact || one status byte`. Status zero accepts the ELF; any nonzero status means discard all preceding bytes. Invalid source may have a partial ELF prefix. Don't run it.

## Linux I/O failures

The generated executable uses `read(0, &cell, 1)` and `write(1, &cell, 1)`:

- Pointer out of range: exit(2).
- Failed write or nonpositive write return: exit(3); `-EINTR` retries.
- Failed read: exit(4); `-EINTR` retries; EOF stores zero.
- `-EAGAIN` is an error, not a spin loop or readiness wait.
- Broken stdout pipes have the kernel's default `SIGPIPE` behavior.

This is an explicit Linux target contract, not a ninth Brainfuck instruction.

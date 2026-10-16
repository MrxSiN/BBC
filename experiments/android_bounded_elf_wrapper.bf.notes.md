# Extended bounded Android ELF wrapper — Iteration 29

**BF source SHA-256:** `1222f47656537c56053d64272895c891eaa5178cd769b17c988caf906e657091`. **Filtered BF SHA-256:** `e41de4271f4e382f76872c7300cf5e13d559dbbc7b2d61470f28eac0914a84a5`. **BF instructions:** 8,531. **Linux native ELF SHA-256:** `51a113f6906e045e9f1ada9426b2d3b08e1f6b615188c49505e1bbbecf8fd08c`.


This is a second, experimental Brainfuck-native ELF constructor. It is **not** the general dynamically sized Android ELF writer still planned for Iteration 30.

## Interface and layout

The transport input is one unsigned byte containing a slot count `0..74`, followed by exactly `count * 48` binary slot bytes. The upstream adapter reorders a BF-owned framed record; it does not synthesize headers, instructions, relocations or ELF contents. Counts `75..255` are rejected with status 1. The output is 4,192 ELF bytes followed by a zero framing byte and a status byte. Incomplete binary slot transport cannot be reliably distinguished from actual zero bytes by the V0 EOF-zero input primitive; **the adapter must enforce exact input length**.

The ELF64 PIE startup, interpreter `/system/bin/linker64`, five program headers, executable segment and 96-byte dynamic table are written as **Brainfuck output bytes**. They deliberately preserve the earlier AArch64 ELF ABI and 16 KiB alignment:

| Range | Contents |
|---|---|
| `0x000–0x20f` | ELF headers, interpreter, tiny dynamic linker metadata and tape address startup |
| `0x210–0xfef` | 74 native 48-byte slots; trailing unused slots are AArch64 NOPs |
| `0xff0–0xffb` | Exit syscall |
| `0xffc–0xfff` | One NOP |
| `0x1000–0x105f` | 96-byte dynamic data, followed by zero-initialized tape from the RW segment's BSS |

All output bytes are emitted by this standard Brainfuck program. The fixed 4,192-byte file has 4 KiB executable bytes and a 65,536-cell zeroed tape through the documented Android load contract. The empty-slot NOPs add overhead. This is an intentional correctness-first bridge from the old ten-slot fixed image toward an actual scalable dynamic-image layout.

## Limitations

No bracket relocations are applied. A BF-owned upstream slot stage returns status 3 for bracketed input, and the adapter refuses such input before calling this ELF wrapper. The adapter cannot accept more than 74 commands, despite the slot stage's multi-byte counter. This prototype is Linux-hosted: instruction-level simulation at two load biases and `readelf` structural checks do **not** establish actual Android shell loading, on-device compiler execution, or Android-native self-hosting. Android 16 KiB page and loader compatibility beyond the old bounded prototype remains to be verified on device.

Cells 0–3 own count, remaining slots, and error status; cell 4 outputs a byte; cell 5 receives opaque slot bytes; cells 10–12 are comparison scratch; cell 13 is the 12-NOP-word filler counter. No BF instruction character occurs in adjacent `.bf` source comments.

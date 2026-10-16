# Android AArch64 PIE subset prototype

The executable logic is in the adjacent standard Brainfuck source. The host development script used to author its fixed byte constants is not required at runtime. This is an experimental separate backend and is not the authoritative compiler.

This test backend accepts ASCII source containing only increment, decrement, output, and ignored noninstruction text. Unsupported commands are rejected with final status 1. The source is terminated by NUL or host EOF; NUL within ignored text is not supported. A maximum of ten accepted commands is enforced. The file protocol is fixed 4192 output bytes followed by one status byte. Do not install the binary if status is nonzero.

Image layout: ELF64 ET_DYN AArch64. Five program headers, PT_INTERP at offset 0x160 for /system/bin/linker64, code entry at 0x200, ten 48 byte native slots beginning at 0x210, termination at 0x3f0, RX region 0x0000..0x0fff, RW segment at virtual 0x5000 and file offset 0x1000, 96 byte dynamic table with DT_HASH DT_STRTAB DT_SYMTAB DT_SYMENT and DT_STRSZ plus termination then a 65536 byte zero tape from 0x5060. Both LOAD segments have 0x4000 alignment to keep a 16 KiB page compatibility target. The code calls Linux arm64 write and exit using direct svc instructions. Android syscall availability and loader behavior still need on device tests.

There are no loops, input, or pointer movement in the supported subset. The generated tape pointer remains on cell zero, so no pointer escape is possible for accepted programs. Writes currently exit on any nonone return rather than retrying EINTR, so this is not yet fully equivalent to the Linux backend's I/O policy.


## Current source status after Iteration 23

The first paragraph is historical. The current file also supports pointer
movement and input in addition to increment decrement and output. Movement is
checked and the input slot stores zero at EOF. The interpreter-based and
instruction-simulator tests cover these operations. In Iteration 24 a
**separate** Brainfuck bracket-span resolver was added; this file still does
not emit either bracket instruction. Read
`android_bracket_relocations.bf.notes.md` for the relocation stage. The
10-command source limit and 4192-byte image contract remain unchanged.

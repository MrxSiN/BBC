# BF-owned Android affine optimizer

Source SHA-256: `811f45ca94f513b1ecb3659680ab23a826c8c09bcde189656c1c4d7b5e4c9af8`

Filtered instruction SHA-256: `c5d7c251a21dcccc0178b3d4034a775e5aeeb10b4530a825bd5c3bd3952444c3`

The adjacent raw standard BF source contains 15,595 commands. Both independent
BF seeds execute `compiler/core.bf` to build the same 499,255-byte Linux ELF.
That ELF was cross-built on Windows; it was not natively executed here.
The BF stage itself ran under both independent interpreters.

Input is at most ten already validated, filtered commands, NUL, then the
complete trusted 4,192-byte image from the six-stage Android pipeline. Output
is a 4,192-byte image and zero status. This internal stage does not validate
arbitrary ELF files or replace the upstream source validator. The adapter
checks status, size and provenance before installing an image.

Records use sixteen cells: source at 0, recognized kind at 1, ordinary path
flag at 2, counter at 3, byte/equality scratch at 4, copy temporary at 5,
conditional flags at 6..11, spare cells at 12..13, slot count at 14 and rewind
sentinel at 15. Scratch stays within each record. The source scan recognizes
`[-]`, `[+]`, `[>+<-]`, `[->+<]`, `[<+>-]` and `[-<+>]`.

Each replacement occupies the original opening bracket's 48-byte slot and
jumps past the complete loop. Slot positions and upstream branch relocations
stay valid. Clear loops become a zero store. Transfers skip the body when the
source is zero; otherwise they check the adjacent address against the full
65,536-byte range before loading or storing it. An invalid destination jumps
to the original pointer slot's exit(2) trap. Addition wraps at the byte store.
The source becomes zero, destination receives the old source, and the pointer
remains at its original cell. All other commands retain upstream code.

Changing `PT_INTERP` to `PT_NULL` removes the unnecessary Bionic startup for
this syscall-only image. No libc or unresolved dynamic symbols are needed.
The next resource stage can also remove unused data mappings where proven.
Native execution is verified on Pixel 8 Pro, Android 17/API 37 with 4-KiB
pages; other devices and page sizes remain untested.

See [the full differential and native evidence](../evidence/android_native_optimization.json)
and [the resource stage](android_resource_optimize.bf.notes.md).

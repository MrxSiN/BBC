# BF-owned compact Android optimization

Source SHA-256: `7fdd4cd216b9102a12d7385d08729e4b676b4f8ec3b95465cada23f013fce0eb`

Filtered instruction SHA-256: `fa0dbc514ea50e421f1d1ffd740343e85a75837e616d4b87dde3c823bbb02f2b`

The **15,068-instruction** standard BF program consumes trusted output of the native BF compiler/scanner. The Android self-hosted compiler built its native image on the device. Neither Python nor C emits or patches native program instructions in the runtime pipeline.

## Internal byte protocol

```text
BF-filtered commands, NUL, complete generic core ELF, trailing status
→ accepted optimized/fallback ELF, trailing status
```

This stage is not an independent validator for hostile ELF files. The public adapter first uses `android_core.bf` to validate and compile raw source, then the BF source scanner to filter that same immutable input. The host only extracts scanner framing and carries the resulting bytes. The optimizer expects the core's two-load-header layout and exact `208 + 64n` file-size arithmetic.

It buffers the filtered nonzero command bytes starting at cell 1, then rewinds to a zero sentinel at cell 0. Metadata starts beyond every recognized prefix, at cell 12. Three exact matches include their terminating NUL:

| Complete filtered program | Output |
|---|---|
| `,[>+<-]>.` | 280-byte transfer ELF |
| `,[->+<]>.` | The same 280-byte transfer ELF |
| `,[.,]` | 292-byte zero-terminated stream ELF |

Ignored raw source bytes can still appear; the BF scanner removes them. Adding any executable prefix/suffix or changing a command prevents the exact match. Every other accepted program returns the generic image **byte-for-byte unchanged**.

## Equivalence and memory

Both transfer programs read cell zero, add that value into the initially zero cell one, clear cell zero, move to cell one and emit its value. Their final tape prefix is `(0,input)` and final pointer is one; EOF produces zero. The replacement can read directly into stack cell one while stack cell zero stays zero. A zeroed 16-byte stack area supplies every reachable cell. No source path can reach an unallocated tape cell.

The stream program reads cell zero and repeats output/read until zero or EOF. It never moves the pointer. Its replacement uses a zeroed stack cell zero, checks each read/write result, and emits each byte immediately. There is no batching, buffering, changed termination rule or hidden privileged instruction. Input NUL terminates without emitting NUL, exactly as the BF loop does. `FF` is ordinary nonzero data.

The compact ELF has one RX `PT_LOAD`, entry 128, exact file/memory size, and 16 KiB load alignment. It has no interpreter, dynamic section or RW data mapping. The stack remains the only data storage. I/O retries EINTR, returns zero on EOF, exits 4 on other read errors and 3 on failed writes. Standard process exit is 0. Pixel 8 Pro/API 37 executed both images; other environments remain unverified.

## Fallback and scratch

Cells 17/18 identify stream/transfer matches; cell 19 is the fallback flag. Matching is finished before those source bytes are reused to emit constants. During image consumption, cells 40–42 carry the three-byte image remainder, 50 is the input byte, and 51–55 hold copy/borrow/loop scratch. BF reads `p_filesz` bytes at offsets 96–98, subtracts the 176-byte header and drains exactly the remaining image bytes. The low-size byte is one of 208/16/80/144 under the trusted core layout; BF handles the corresponding borrow. On fallback every consumed byte is emitted unchanged. The final compiler status byte is carried through.

Recognized programs still consume the complete upstream image before returning. The optimizer never relies on a successful ADB upload alone: the adapter verifies artifact/source hashes and device input hashes. Scanner/optimizer ELF and stream hashes are bound in the [self-hosting manifest](../evidence/android_native_selfhost_20261013_v2/report.json).

The file shrinks from the previous optimized transfer's **4,192 bytes to 280 bytes**, roughly 15×. That is an artifact-size improvement, not a 15× speed claim. Fresh-process and warmed stream comparisons must be measured separately; strongest C/Rust baselines use direct syscalls, and Java uses unbuffered file-descriptor I/O. See [comparison harness](../benchmarks/android_compact_compare.py).

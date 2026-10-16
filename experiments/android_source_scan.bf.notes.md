# Wide streamed source scanner — Iteration 27 experimental BF stage

Source SHA-256: `c9a6b7c9d3e4f17f0802fa64b382cc5bfda37027aaf6ee277cc1432787b18bf2`  
Filtered instruction SHA-256: `03658024b1517ed74ce478707bc0bdc70ded76dbcce50afbe07d14baac9b2984`  
**1,170 Brainfuck instructions**. The program is ordinary Brainfuck. Safe `#` comments are ignored by a standard interpreter. It is **not** the Linux canonical compiler or an Android-native compiler.

## What this changes

The old `stream_filter.bf` already decoded the `FF 01`/`FF 02` byte-stuffed input protocol and emitted source instructions. This sibling BF program additionally counts **only emitted executable commands**, in three little-endian counter cells. It does not hold the whole source on its tape. Ignored UTF-8 bytes, NUL and FF source bytes, and ordinary prose never increase the counter.

Native Linux execution demonstrates 300,001 command bytes pass through the scanner with the correct count, beyond both the Android emitter's **ten-command limit** and the Linux canonical compiler's **16,128-command source limit**. This does **not** make the Android backend accept 300,001 commands: bracket metadata, output layout, ELF emission and relocations remain bounded to ten.

## Tape ownership

| Cells | Owner / lifetime |
|---|---|
| 0 | Existing input status; zero on success; one on malformed escape |
| 1–6 | Existing streaming byte filter; its temporary source and classifier state |
| 7 | Marker set exactly when the original BF-owned filter emits a command; cleared each input iteration |
| 8–10 | Unsigned 24-bit emitted-command counter, little endian; persists until EOF |
| 11 | Zero-test flag; cleared before leaving a counter update |
| 12–13 | Destructive-copy scratch, restored/cleared during carry testing |
| 14 | Carry out of 24 bits; converted into nonzero final status 2 |

Each command emitter sets the marker; one central counter routine consumes it and increments the low byte. A wrapped low byte increments the middle byte; a wrapped middle byte increments the high byte; high-byte rollover marks failure. Copy and restore are done with standard Brainfuck loops, not host arithmetic. The pattern never inspects raw text outside Brainfuck. Counter width can represent 0 through 16,777,215; **the actual maximum accepted by the wrapper is further bounded to 1 MiB of raw source**. The direct stage has no raw-byte size check or compile-time 300,000-command limit. Very large untrusted streams therefore still require resource limits at the transport boundary.

There is no formal whole-program tape-ownership proof. The first fourteen cells remain within the fixed 65,536-cell V0 tape. The static pointer walk is within zero through fourteen, and dynamic cases exercise ordinary carries, wrapping, malformed framing and a separately instrumented 24-bit overflow sentinel. This is executed test evidence, not a formal proof of all possible paths.

## Output subprotocol

```text
filtered BF command bytes ...
uint24_le command_count
uint8 final_status
```

The byte stream is **not NUL-delimited**. A consumer reads the last **four bytes** to find the count and final status. Status zero means the BF decoder accepted the encoded input. Status one indicates malformed FF transport; status two indicates a 24-bit count wrap. A nonzero final status invalidates the entire partial stream.

The `--scanner` option on `bootstrap/run_android_loops.py` consumes this BF-emitted frame instead of the old filter's one-status-byte frame. It checks that the count metadata is consistent with the returned bytes but performs no BF source filtering or bracket analysis. All later BF stages and their ten-slot constraint are unchanged. Both modes keep the same atomic install behavior.

## Reproduce the local evidence

```sh
python3 tests/verify_android_source_scan.py
python3 tests/verify_android_source_scan_integration.py
python3 tools/check_docs.py
```

The tests compile this `.bf` through the existing verified Linux Brainfuck compiler; run 37 cases including 16,128, 65,536, 300,000 and 300,001 commands; reject six malformed transport cases; compare two independent seed interpreters on smaller inputs; run an instrumented near-overflow case; and compare nine legacy versus scanner AArch64 output images. Exact inputs, hashes and caveats: [`../evidence/iteration27_source_scan.json`](../evidence/iteration27_source_scan.json) and [`../evidence/iteration27_scan_integration.json`](../evidence/iteration27_scan_integration.json).

**Next:** Brainfuck-owned multi-byte bracket positions and relocations must consume the wide stream. The current scanner has only proved the source-ingestion primitive; it has not removed the Android emitter's ten-command ceiling or demonstrated Android self-hosting.

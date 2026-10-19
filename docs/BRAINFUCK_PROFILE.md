# BBC Brainfuck execution profile

This profile applies to the BFX/XAX lane on Android ARM64, Windows x86-64
and Linux x86-64. Target support is tracked in [STATUS.md](STATUS.md).

| Property | Required behavior |
|---|---|
| Instructions | Exactly `><+-.,[]`; all other source bytes ignored |
| Cells | 65,536 zero-initialized unsigned bytes |
| Arithmetic | Wrap modulo 256 |
| Initial pointer | Cell zero |
| Pointer movement | Every executed out-of-range move fails immediately |
| Input | Next raw byte; zero on every read after EOF |
| Output | Append the raw cell byte; explicit failure if capacity is exhausted |
| Loops | Test the current cell; repeat while it is nonzero |
| Brackets | Reject unmatched brackets during compilation |

Only executed pointer movements can fail; a zero-entry skipped loop does not
move the pointer. Comments are ordinary ignored bytes, so instruction
characters inside annotations execute even after a hash character. The
compiler's size limits are documented in [BFX_CONTRACT.md](BFX_CONTRACT.md).
The bootstrap text framer has a separate NUL-termination restriction described
in [BOOTSTRAP.md](BOOTSTRAP.md); it does not change binary source semantics.

## Decision call

The conceptual call is `run_decision(input_bytes) -> status + output_bytes`.
Each call starts with fresh tape, pointer and I/O cursors. The XAX side owns
input and output buffers and validates lengths, capacity, pointer validity and
any supported aliasing policy before execution. Reads never exceed input
length; writes never exceed output capacity. Buffers and tape must not alias.

The typed XAX adapter core uses 0 success, 1 tape bounds, 2 output capacity,
and 3 invalid logical lengths. These are distinct from BFX compilation error
codes. It borrows three distinct live initialized buffer views; the XAX caller
must establish their pointer validity, initialization and lifetimes. The core
resets the full tape on each valid call. Its native scalar packs output length
in the high 32 bits and status in the low 32 bits. This is an internal typed
call; an untrusted raw-pointer/JNI boundary is not implemented. See
[the integration contract](XAX_INTEGRATION.md). On failure, output may contain
a prefix; the application must discard it. No callbacks, system calls,
or application capabilities belong to Brainfuck. A looping program need not
terminate; an external verifier's step limit is not a source-language feature.

`examples/decision.bf` consumes one flag byte. Zero means no blocking condition
and emits `01`; any nonzero flag emits `00`. The Android app shows
or hides a sample row accordingly. EOF also reads zero, so the app must check
its one-byte application input contract before calling. Output values beyond
these two and nonzero statuses must produce an app error, not an action.

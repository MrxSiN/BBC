# BBC Brainfuck execution profile

This profile governs every BFX decision on Android ARM64, Windows x86-64 and
Linux x86-64. [05_STATUS.md](05_STATUS.md) records which targets have execution
evidence; sharing the profile does not itself establish target support.

## Instruction semantics

| Property | Required behavior |
|---|---|
| Instructions | Exactly `><+-.,[]`; all other source bytes ignored |
| Cells | 65,536 zero-initialized unsigned bytes |
| Arithmetic | Wrap modulo 256 |
| Initial pointer | Cell zero |
| Pointer movement | Every executed move outside cells 0..65,535 fails immediately |
| Input | Consume the next raw input byte; read zero after EOF |
| Output | Append the raw cell byte; fail if logical output capacity is exhausted |
| Loops | Test the current cell; repeat while it is nonzero |
| Brackets | Reject unmatched brackets during compilation |

A skipped zero-entry loop does not execute its body or its pointer movements.
A looping program need not terminate. An external test driver's step limit
is not a language feature. No platform call, callback or application capability
belongs to Brainfuck.

Whitespace and annotations are ordinary ignored source bytes. `#` has no
special lexical meaning: any of the eight instruction characters after it
still execute. Keep annotations free of those characters. Compiler resource
limits, including the 65,533-byte source and 65,536-byte complete request, are
defined in [02_BFX_CONTRACT.md](02_BFX_CONTRACT.md); the optional text
framer's transport restriction is defined in [04_BOOTSTRAP.md](04_BOOTSTRAP.md).

## Native decision contract

Conceptually: `run_decision(input_bytes) -> status + output_bytes`.

The generated core borrows three distinct, live, initialized views: read-only
input, writable output and writable tape, **65,536 bytes each**. The typed XAX
caller establishes pointer validity, ownership, non-aliasing and lifetimes.
Two unsigned 32-bit values specify logical input length and output capacity.
They may be zero and must not exceed the corresponding view extent.

A valid call resets the whole tape and starts with pointer and I/O cursors at
zero. Reads respect logical input length; writes respect logical output
capacity. Invalid logical lengths reject before tape reset. Output buffers
need not be zero initially; bytes after the written prefix remain untouched.

The native scalar result is:

`(output_length << 32) | status`

| Native status | Meaning |
|---|---|
| 0 | Success |
| 1 | Executed tape movement exceeded the tape bounds |
| 2 | Output capacity exhausted |
| 3 | Invalid logical input length or output capacity |

These codes are distinct from BFX compiler errors and importer validation
errors. A failed call may have written an output prefix; the application must
discard it. The raw-pointer core is an internal typed interface, not a public
boundary that validates arbitrary foreign pointers. The Android JNI entry
accepts scalar integers and allocates its views before calling this core.
See [03_XAX_INTEGRATION.md](03_XAX_INTEGRATION.md) for ABI details.

## Decision application

[examples/decision.bf](../examples/decision.bf) consumes one flag byte. Zero
emits raw byte `01` (permit); any nonzero flag emits raw byte `00` (block).
EOF also reads zero under the language profile, so applications must establish
their required one-byte input contract before calling.

The Android application accepts `flag` in 0..255 and `capacity` in 0..16.
Defaults are 0 and 1. It supplies exactly one input byte, requires native
success and exactly one output byte of 0 or 1, then sets the UI mode:

| UI mode | Result | Sample row |
|---|---|---|
| 0 | PERMIT: Brainfuck returned `01` | Visible |
| 1 | BLOCK: Brainfuck returned `00` | Hidden |
| 2 | ERROR: rejected input, native failure or unexpected output | Hidden |

Capacity zero reaches the native output-exhaustion path. Out-of-range scalar
inputs reject before the decision call. Allocation failure takes the existing
checked-null trap and is not a recoverable UI error. The current evidence does
not claim a new OOM-injection test. Eight executed Activity cases and package
identity are recorded in [the integration guide](03_XAX_INTEGRATION.md).

The embedded decision is bounded and the current app invokes it synchronously
in lifecycle/UI flow. Potentially unbounded Brainfuck must execute off the
Android main thread. That general worker integration remains unimplemented;
see [status](05_STATUS.md). A host cancellation or budget, if later supported,
is an integration-policy outcome, must discard failed output and leave the
next invocation isolated, and is not a Brainfuck instruction or language status.

## Optimization obligations

The optional [clear pass](10_CLEAR_OPTIMIZATION.md) folds exact unit-step clear loops
and removes complete 256-command same-direction arithmetic groups. P0 optimizes
compiler bookkeeping. A second [arithmetic pass](12_ARITHMETIC_PACKING.md) packs powers
of two in consecutive arithmetic. The [movement pass](14_MOVEMENT_PACKING.md) packs
identical monotone movements, retaining first-crossing failures. The authoritative frontend preserves
transparent BFX; see
[the proofs](07_OPTIMIZATION_PROOFS.md). Every source rewrite must preserve
output bytes, input consumption, byte wrapping, pointer position, loop
termination behavior and the order of defined bounds failures. Opposite
pointer moves cannot generally cancel: an intermediate move may already fail.
Require positive, negative, nested-loop, wraparound and tape-boundary
comparisons against an independent interpreter before enabling a rule.

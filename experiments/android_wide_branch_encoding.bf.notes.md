# Brainfuck wide AArch64 branch word encoder — Iteration 28 follow-up

**Implementation:** [`android_wide_branch_encoding.bf`](android_wide_branch_encoding.bf)  
**Source SHA-256:** `94054133a519078fda5636047afd5eb8ab1aa5f498480898b6ec660cf908de96`  
**Filtered instruction SHA-256:** `f5914356d17146367f183dd4fb0b9228be4a0164bb766722c39a2e3f4fce22b0`  
**Executable Brainfuck instructions:** **13,985**  
**Linux native build:** [`../build/android_wide_branch_encoding_x86_64_linux.elf`](../build/android_wide_branch_encoding_x86_64_linux.elf) — **447,735 bytes**, SHA-256 `3b0edc45da4a9724492900d85e20e7c0f61c96de73fe17665aea3bb51882bfd2`  
**Executed evidence:** [`../evidence/iteration28_wide_branch_encoding.json`](../evidence/iteration28_wide_branch_encoding.json)

## Record interface

Input is **trusted** upstream BF bracket pair data: one or more seven-byte records `5D <opening 24-bit LE> <closing 24-bit LE>`, followed by `00 <upstream status>`. Positions are **one-based**. The upstream stage must already have verified bracket nesting and source validity. This stage does not replace that check.

Output is 15 bytes per accepted pair: `5D <opening 24-bit LE> <closing 24-bit LE> <forward B instruction LE32> <reverse B instruction LE32>`, then `00 <status>`. Earlier output is invalid if the final status is nonzero. `01` rejects bad tags, zero opening, equal/reversed positions; `04` rejects unsupported branch reach; a nonzero upstream status propagates when read at the record terminator. In the V0 EOF-zero model, incomplete trusted pair transport cannot be reliably distinguished from an explicit zero input byte; the adapter must validate the prior stage and framing.

Only the eight standard BF instructions execute. The commented BF source can be stripped without changing emitted native ELF bytes. The emitter computes subtraction and machine instruction bytes itself. Python's independently calculated AArch64 words are **test assertions**, never production output.

## Native slot contract

For a source command index `i` (zero-based), keep **48 bytes per command**: 12 AArch64 instructions. The loop slot starts with `LDRB W9, [X19]` (`0x39400269`); the next instruction inverts the loop condition to skip the unconditional branch when iteration continues normally:

- Opening bracket: `CBNZ W9, +8` (`0x35000049`), followed by `B` to immediately **after the closing slot**.
- Closing bracket: `CBZ W9, +8` (`0x34000049`), followed by `B` to immediately **after the opening slot**.
- Nine remaining instructions are ordinary AArch64 NOPs (`0xd503201f`).

If the one-based opening/closing positions are `o` and `c`, the two `B` immediate displacements, in four-byte instruction units, are:

```text
forward = 12 * (c - o) + 10
reverse = 10 - 12 * (c - o)
B word = 0x14000000 | (signed_displacement & 0x03ffffff)
```

These are distances **from the unconditional B**, not from the preceding CBZ/CBNZ. `B` has signed 26-bit range. This stage deliberately caps pair separation at **2,796,201 source commands**, the forward side's last accepted position difference. It rejects larger differences rather than emitting a wrapped, unsafe branch. The **300,000-command** objective fits this reach, but a still-larger compiler would need a further layout rule or a multi-instruction far jump.

## Tape and source assumptions

Cells 0–3 hold record control and status, 4–9 the input positions, 10–12 a three-byte unsigned difference and cell 13 its borrow, 14–16 temporary counters, 17–20 the four-byte forward displacement, 21–24 the four-byte two's-complement reverse displacement, and 25–29 intermediate flags and counter. The stage implements subtraction with tracked borrows and multiplication by twelve using bounded byte loops and carry propagation. It restores its temporary scratch cells. There is no tape pointer calculation based on an untrusted pair value; all data fields are stored in fixed cells. This is a **local design argument**, not a formal proof of the complete compiler.

## Verification boundary

The native Linux executable was produced by the verified Linux BF compiler. Independently calculated words, branch targets, range and failure cases are checked in [`../tests/verify_android_wide_branch_encoding.py`](../tests/verify_android_wide_branch_encoding.py). True metadata and pair records from other BF-native stages were fed to this encoder, including a 300,000-command span, depth 255 and 4,000 sequential loops. Two independent interpreted BF seeds agreed on four small inputs. The opt-in `--scanner --wide-branches` adapter can check this stage before the original ten-slot pipeline. **It still uses the OLD encoder and patcher for actual ELF construction.** No dynamic image emission, large Android executable, target-device execution of this veneer, or Android-native compiler self-hosting was demonstrated here.

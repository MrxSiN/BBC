# Iteration 53 — BF-owned AArch64 long-range loop branches

**Classification:** Linux-executed standard-Brainfuck compiler stages; freestanding AArch64 ELF structurally inspected and behavior simulated. **No new Android loader run or app/JNI integration**.

## Implemented

The opt-in `bootstrap/android_compact_dynamic_far_elf53.py` pipeline removes the previous 26-bit direct `B` branch encoding from the bracket slots. A bracket is eight native 32-bit words: `LDRB W9,[X19]`, conditionally skip (`CBNZ` for an open bracket; `CBZ` for a close bracket), `ADR X10,#0`, `LDR X11,#12` to read a signed 64-bit *relative word count*, `ADD X10,X10,X11,LSL #2`, `BR X10`, then the embedded eight-byte signed word displacement. Both directions are relocation-safe under PIE load bias. `X10` and `X11` are scratch registers. The six other opcode templates remain unchanged.

Four newly generated **standard eight-command BF** stages own instruction selection/encoding, compact native word tracking, literal patch positions and signed 64-bit relative displacements. The existing BF-owned disk-backed stack matcher, 64-bit span stage and BF-owned ELF metadata stages are reused. Generic Python transport joins opaque BF-produced fields and writes eight bytes at BF-produced word indices, without computing displacements. Existing Iteration 52 sources and binaries are preserved.

## Verified results

| Evidence | Result |
|---|---:|
| Source-dependent differential ELF programs | 57 |
| Simulated runs at distinct PIE biases | 114 |
| Checked loop pairs | 1,466 |
| Arithmetic tests including spans above signed imm26 reach | 36 |
| Bracket-free ELF byte parity with iteration 52 | 6 |
| Malformed/over-quota outputs rejected atomically | 4 |
| Independent BF interpreter agreement | 2 |
| New BF native stage byte-identical regeneration | 4 of 4 |
| Structural synthetic source | 296,307 commands |
| Synthetic ELF size | 3,686,824 bytes |

Evidence: [`iteration53_android_far_elf_tests.json`](../evidence/iteration53_android_far_elf_tests.json) and [`iteration53_large_synthetic.json`](../evidence/iteration53_large_synthetic.json). For exact test source and emulator see [`verify_android_compact_far_elf53.py`](../tests/verify_android_compact_far_elf53.py). `llvm-objdump` independently decodes the new jump instructions. The 296,307-command case was **not** run in the AArch64 simulator and does **not** derive from any original Android app policy.

## Explicit limits

No ELF with a branch spanning beyond 128 MiB was executed, although the BF 64-bit arithmetic was tested at and above that threshold, including offsets over 4 GiB. The embedded signed-64-bit word displacement replaces the direct imm26 restriction, but output size, host and filesystem resources remain finite. Source frames are raw byte streams and the host uses disk-backed pairs; no universal 100-million-command compilation pass is claimed. Android's current actual device-loader/SELinux environment has not validated this PIE, and none of the eleven GmailHideAds/TwitterHideAds/ThreadsHideAds policies has been compiled into JNI-compatible libraries. Historical bounded Android S2 evidence is separate from this backend.

## Run

```bash
python tests/verify_android_compact_far_elf53.py
python bootstrap/android_compact_dynamic_far_elf53.py examples/program.bf -o /tmp/program.elf
readelf -Wl /tmp/program.elf
```

`tools/author_android_far_branches53.py` is a *development-only* macro author. At source-compilation time all code-layout decisions are executed by the saved BF stages, not by this script.

## Next gates

First run the newly generated ELF fixtures through an actual Android AArch64 loader. Second compile the *original* pinned 11 policy sources (starting with GmailHideAds `scope.bf` and `row.bf`) and compare real policy frames, preserving per-program tape and I/O behavior. Third implement JNI-callable shared-library artifacts and Android application builds. Test a genuinely long executable branch and larger mixed-source input before claiming general 100-million-command coverage.

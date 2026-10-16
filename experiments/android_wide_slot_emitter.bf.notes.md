# Android AArch64 wide slot emitter — Iteration 29

**BF source SHA-256:** `335208de730d4ebd112f943eaa2724b63e0dfdf1a87538d09a0438fe89bd17f3`. **Filtered BF SHA-256:** `e6f215591f93a2c65e0c15f99c918671dcd7e373d9a8971d8d642f992af3a378`. **BF instructions:** 16,075. **Linux native ELF SHA-256:** `6d383688d6359a73aa86247c1e1178b55df0a9f03fb280a93f6bf86798b96252`.


The executable implementation is the adjacent **standard Brainfuck** `.bf` file, not the host transport. It is an experimental Linux-hosted stage compiled by `compiler/core.bf`.

## Input and output

Input: an already filtered standard Brainfuck instruction stream, terminated by an EOF/zero byte. Input bytes other than the eight BF commands cause a nonzero status. The upstream BF scanner owns ordinary source filtering, including ignored bytes.

Output: exactly **48 native AArch64 code bytes per recognized instruction**, then a three-byte little-endian command count, one zero terminator, and a status byte. On status `0`, all output slots are usable. Status `1` means a non-BF input byte; `2` is the 24-bit counter wrap; `3` identifies bracket slots whose branch relocations have not been applied. **Any nonzero status invalidates the entire output.** Count and status belong to Brainfuck logic.

It recognizes all eight instruction bytes. The six linear operation templates reproduce the earlier BF-generated bounded ELF slots. Opening and closing brackets produce reserved 12-word slots beginning with `LDRB`, opposite `CBNZ/CBZ +8`, and **an unpatched unconditional `B`** with immediate zero. This stage deliberately refuses to advertise such slots as runnable code (status `3`). The previous 24-bit bracket pairing and branch-word encoder have not yet been merged with executable-image relocation.

## Tape ownership

Cells 0–3: input, comparisons, match flag. Cell 4: output-byte accumulator. Cells 5–7: unsigned 24-bit slot count. Cell 8: failure status. Cell 9: carry flag. Cells 10–12: comparison scratch and flag. Cell 13: repeated NOP instruction count. Cell 14: unrelocated bracket marker. All are within the normative 65,536-cell V0 tape. No dynamic tape addresses or host-memory pointers are computed by this stage.

## Validation scope

The archived native Linux BF compiler directly generated the stage executable. The test suite verifies commented/stripped source invariance, native-byte parity with the old slots, count carries at 255/256 and 1,023/1,024, rejection cases, 74-command ELF integration and bounded AArch64 simulation. The 300,000-command source **scanning** and **bracket matching** tests from Iterations 27–28 do not prove this slot stage can emit 300,000 native slots within a practical time or memory budget. A 24-bit counter is an *encoding*, not a tested end-to-end compilation limit.

The original standard BF instructions remain the only executable input language. The template constants were transcribed from already BF-generated AArch64 slots during development; neither a Python machine-code backend nor LLVM runs in the compilation path.

The new stage occupies **16,075 of 16,128** supported executable BF commands for the existing Linux compiler. This leaves just **53** commands of capacity and is a concrete reason to keep later relocation logic in its own Brainfuck-owned stage.

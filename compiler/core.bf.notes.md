# Compiler notes — where the bytes go

Source SHA-256: `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`

Filtered instruction SHA-256: `fbb5db5a140f5b890d47915e69b975a91ea2a780681574c23f0069a5f57546af`

Offsets are zero-based and half-open, measured in the filtered instruction stream of `compiler/core.bf`. None of this text executes. The compiler has enough byte arithmetic already.

| Range | What it does |
|---|---|
| `0:2462` | Decode byte stuffed source and discard noninstructions using the BF only classifier while preserving source count lanes and overflow traps |
| `2462:2848` | Keep the input error bit safe and calculate the ELF file byte count using the stored command count |
| `2848:4277` | Emit ELF and startup bytes with short arithmetic loops using compiler cell 61 as zeroed scratch |
| `4277:4331` | Restore the pending input error bit after the header |
| `4331:14854` | Emit fixed native slots only for commands and resolve branches on the compacted source |
| `14854:14859` | Output the compiler error status byte |

Generated executables contain exactly `215 + 32 * filtered_command_count` bytes. The RW tape remains a separate nonexecutable segment.  The compiler tape uses cell 61 as a temporary loop counter only while constructing fixed ELF header bytes; it must be zero at entry and on exit.

The current 16,128-byte command ceiling counts executable instructions only, not comments. Two count metadata lanes must survive every decoder iteration; sentinel and malformed transport errors are preserved.

Any source change requires regenerating the derived annotated view and rerunning both independent bootstrap seeds, native Stages 0 to 2, semantic tests, and ELF validation.

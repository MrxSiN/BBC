# Standalone command-filter notes

Source SHA-256: `d71055100503a0fc26858b3c134f688f452dc1e88afb68230516d266cdc772bd`

`command_filter.bf` has **862** original Brainfuck instructions. This is a separate experiment, not the production compiler's frontend. Its input is one unsigned byte for the count, then exactly that many raw bytes.

- Cell 0 stores the remaining byte count.
- Cell 1 stores the input byte and remains unchanged during comparisons.
- Cell 2 is a temporary copy used for subtraction-based comparisons.
- Cell 3 is a match flag. It returns to zero after every comparison.

The eight comparisons use only normal tape moves, copying, modular subtraction and conditional loops. A match writes the original byte through `.`. No matching byte is interpreted as a new command. Input NUL works because the loop is controlled by the length, not by the input value.

See [`../docs/COMMAND_FILTER.md`](../docs/COMMAND_FILTER.md) for verified behavior and what is still missing before the production compiler can use this routine.

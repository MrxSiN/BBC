# Annotated compiler — generated, not source

Source SHA-256: `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`
Filtered instruction SHA-256: `fbb5db5a140f5b890d47915e69b975a91ea2a780681574c23f0069a5f57546af`

Generated from `compiler/core.bf` and the hash-locked notes. This is for reading, not compiling.
Every offset refers to the raw BF command stream. The compiler ignores this whole file.

## Instructions 0–2461

Decode byte stuffed source and discard noninstructions using the BF only classifier while preserving source count lanes and overflow traps

2462 BF commands in this region.

Start of region:

```brainfuck
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>,<<<[-]>[-]>[-]>[-<<+>+>]<[->+<]<+<[-]+>[[-]<[-]>]<[[-]>>>,>[-]<<<<[-]>[-]>[-]>[-<<+>+>]<[->
```

End of region:

```brainfuck
-]+>[[-]<[-]>]<[[-]<<<<[-]>>>>]<<<<][-]<<<<[-]>[-]>>>>>[-<<<<<<+>+>>>>>]<<<<<[->>>>>+<<<<<]<+>>>>[-]+<<<<[[-]>>>>[-]<<<<]>>>>[[-]>>>[-]>[-]+<<<<]>[-]>[-]<<<<<<<
```

## Instructions 2462–2847

Keep the input error bit safe and calculate the ELF file byte count using the stored command count

386 BF commands in this region.

Start of region:

```brainfuck
>>>>>>>>>[->>>>>>>>+<<<<<<<<]<<<<<<<<<>>>>>>>>>-----------------------------------------<[>++++++++++++++++++++++++++++++++[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<--
```

End of region:

```brainfuck
>>[-<<<<+>>>>]<>>[-]+<<[[-]>>[-]<<]>>[-<<<<+>>>>]]<<<<<<[->>>>+<<<<]>[->>>>+<<<<]>[->>>>+<<<<]>]<<<<[>>>>>[-<<<<+>>>>]>[-<<<<+>>>>]>[-<<<<+>>>>]<<<<<<<<<<<]<<<<
```

## Instructions 2848–4276

Emit ELF and startup bytes with short arithmetic loops using compiler cell 61 as zeroed scratch

1429 BF commands in this region.

Start of region:

```brainfuck
[-]>++++++++++++++[<+++++++++>-]<+.>++++++++[<------->-]<--.+++++++.------.>+++++++++++[<------>-]<--.-..-.........++.--.>+++++++++[<+++++++>-]<-.>+++++++++[<--
```

End of region:

```brainfuck
++++++++++++++++++++++++++++++++++.>+++++++++++++++[<+++++>-]<..+.-.>+++++++++++++++[<+++++++>-]<+.>+++++++++++++++[<------->-]<.>+++++++++++[<++++++++>-]<+.[-]
```

## Instructions 4277–4330

Restore the pending input error bit after the header

54 BF commands in this region.

Start of region:

```brainfuck
>>>>>>>>>>>>>>>>>[-<<<<<<<<+>>>>>>>>]<<<<<<<<<<<<<<<<<
```

End of region:

```brainfuck
>>>>>>>>>>>>>>>>>[-<<<<<<<<+>>>>>>>>]<<<<<<<<<<<<<<<<<
```

## Instructions 4331–14853

Emit fixed native slots only for commands and resolve branches on the compacted source

10523 BF commands in this region.

Start of region:

```brainfuck
>>>>>>>>[>[-]>[-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>]<--------------------------------------------------------------<[-]+>[[-]<[-]>]<[[-][-]+++++++++++++++++++++++++
```

End of region:

```brainfuck
----------------------------...+++++++++++++++++++++++++++++++++++++++++++++++++.--------------------------------------------------.++++++++++++++++.----------.
```

## Instructions 14854–14858

Output the compiler error status byte

5 BF commands in this region.

Start of region:

```brainfuck
>>>>.
```

End of region:

```brainfuck
>>>>.
```


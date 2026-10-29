# fold dot bf  BBC offset and loop folding pass
#
# Input  the filtered primitive instruction bytes of one validated program
#        followed by a zero byte or end of input
# Output the BFX v2 operation body for those instructions  the caller frames it
#        and appends the END byte
#
# The tape holds a window of 256 slots that mirrors the program tape around the
# start of the current straight segment  Slot 128 is offset zero  Each slot has
# 16 cells
#   0 A    1 for window slots  0 for the two guard slots
#   1 V    visited in this segment
#   2 D    net delta of the cell modulo 256
#   3 I    the slot offset as a signed byte  slot minus 128
#   4 E    1 on the two edge slots 0 and 255
#   5 CK   a turning point was left here and needs a bounds check
#   6 NC   1 on every window slot except the cursor
#   7 RUN  main loop flag  travels with the cursor
#   8 P    a loop open is pending  travels with the cursor
#   9 LL   last move went left   travels with the cursor  flush mode S later
#   10 LR  last move went right  travels with the cursor  flush temp later
#   11 M   move flag  bracket flag during a flush
#   12 K   kind of the current byte
#   13 X   14 Y   15 Z   temps  the zero test idiom uses Y and Z after X
#
# Kinds  1 right  2 left  3 open  4 close  5 output  6 input  7 end  8 edge
# 9 a close folded into multiply form
#
# Emitted operations  all offsets are signed bytes relative to the pointer
#   01 d k  add k to the cell at offset d        bounds checked
#   02 d k  add k times the current cell to offset d   bounds checked
#   03 d    bounds check offset d
#   04 n    move the pointer by n                 bounds checked
#   00      clear the current cell
#   the loop and input output primitives unchanged
#
# Every point a segment path can first leave the tape at is a turning point or
# its end  Each is checked by an add or multiply at that offset  a check  or
# the final move  A segment holds no input output or loops  so failing at any
# of those checks instead of the first crossing is not observable
#
# A loop whose body is one segment that returns to offset zero and changes
# that cell by one or minus one runs exactly x or 256 minus x times  It becomes
# a guarded multiply form  open  checks and multiplies  clear  close
# The guard keeps the checks conditional on entering the loop
#
# ======== init
>>>>>>>>>>>>>>>>+  slot 0 field A
>>>>>>>>>>>>>++++++++[-<<<<<<<<<<++++++++++++++++>>>>>>>>>>]  slot 0 index 128 via X
<<<<<<<+  slot 0 NC
<<+  slot 0 edge
>>>>>>>>-  K counts 255 more slots
[  build one more slot
-[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]  move the count on
<<<<<<<<<[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<>>>>>>>>>>+<<<<<<<<<<]>>>>>>>>>>[-<<<<<<<<<<+>>>>>>>>>>]<<<<<<<<<<  copy the index on
>>>>>>>>>>>>>>>>+  next index
<<<+>>>>>>+  A and NC
>>>>>>  back to K
]  slot 255 reached
<<<<<<<<+  slot 255 edge
>>>>>>>>>>>>>>>+  right guard index nonzero
<<<<<<<<<<<<<<<<[<<<<<<<<<<<<<<<<]  scan to the centre slot
<<+>>>>>->+  centre visited  is the cursor  RUN set
# ======== main loop
[  at RUN
>>>>>>,  read one byte into X
>+<[>-]>[<<+++++++>>->]<<  zero is end
------------------------------------------->+<[>-]>[<<<<<<<<<<<<+>>>>>>>>>>>>->]<<  plus
->+<[>-]>[<<++++++>>->]<<  input
->+<[>-]>[<<<<<<<<<<<<->>>>>>>>>>>>->]<<  minus
->+<[>-]>[<<+++++>>->]<<  output
-------------->+<[>-]>[<<++>>->]<<  left
-->+<[>-]>[<<+>>->]<<  right
----------------------------->+<[>-]>[<<+++>>->]<<  open
-->+<[>-]>[<<++++>>->]<<  close
[-]  clear X
<[->+>+<<]>>[-<<+>>]<  X is a copy of K
->+<[>-]>[<<<+>>>->]<<+[-]  M is kind one
<<[  move right
->-  clear M and K
<<<[-<<<<+>>>>]  turning point after a left move
>[-]+  last move right
<<<[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]  carry RUN P LR
<<<<+>>>>>>>>>>>>>>>>-  cursor moves
<<<<<[-]+>>>>>>>>>>  visited  back to M
]
>[->+>+<<]>>[-<<+>>]<  X is a copy of K
-->+<[>-]>[<<<+>>>->]<<++[-]  M is kind two
<<[  move left
->--  clear M and K
<<[-<<<<<+>>>>>]  turning point after a right move
<[-]+  last move left
<<[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]>[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]>[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]  carry RUN P LL
<<<+<<<<<<<<<<<<<<<<-  cursor moves
<<<<<[-]+>>>>>>>>>>  visited  back to M
]
<<<<<<<[->>>>>>>>>+>+<<<<<<<<<<]>>>>>>>>>>[-<<<<<<<<<<+>>>>>>>>>>]<[-<++++++++>]  an edge sets kind 8
<[  flush the segment at K
# ======== flush
<<<[-]>[-]  forget the last move direction
>>[->+>+<<]>>[-<<+>>]<  X is a copy of K
---->+<[>-]>[<<<<<+>>>>>->]<<++++[-]  S is kind four
<<<<[->+<]>[-<<[->+>>>>+<<<<<]>>>>>[-<<<<<+>>>>>]<<<]  S and pending open
<[->+<]>[-<<<<<<<[->>>>>>>>>>+>+<<<<<<<<<<<]>>>>>>>>>>>[-<<<<<<<<<<<+>>>>>>>>>>>]<>+<[>-]>[<<<<<+>>>>>->]<<[-]<<<]  S and cursor at offset zero
<[->+<]>[-<<<<<<<<[->>>>>>>>>>>+>+<<<<<<<<<<<<]>>>>>>>>>>>>[-<<<<<<<<<<<<+>>>>>>>>>>>>]<->+<[>-]>[<<<<<++>>>>>->]<<++>+<[>-]>[<<<<<+>>>>>->]<<-[-]<<<]  S is 2 for delta one and 1 for delta minus one
<[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<[[-]<+++++>]  a folded close becomes kind 9
<<<<<[->[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<>+<[>-]>[<>>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[-]<<>->]<<[-]<<<<<]  emit a pending open unless folded
>[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<[[-]<<<<<<<<<<<<<<<<<<<<<<<<<<<<[->>>>>>>>>>>>>>>>>>>>>>>>>>+>>>+<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[-<<<<<<<<<<<<<<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]>>>[-<<<<<<+>>>+>>>]<<<[->>>+<<<]<]  M counts visited neighbours when folding
<<<<<<<<<<<<[>>>>>>>>[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]>>[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]<<<<<<<<<<<<<<<<<<<<<<<<<<]  carry S and M to the slot before the first visited
>>>>>>>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]<<<<<<<<<<>>>>>>>>>>>>>>>>  and onto the first visited slot
>>>>>>>>>>[->>+>+<<<]>>>[-<<<+>>>]<[[-]>>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[-]<<]<<<<<<<<<<<<  guarded multiply form opens
[  walk every visited slot from the left
>>>>>>>>[->+>>>>+<<<<<]>>>>>[-<<<<<+>>>>>]<<<<  LR is a copy of S
[[-]<<<<<<<[->>>>>>>>>>+>+<<<<<<<<<<<]>>>>>>>>>>>[-<<<<<<<<<<<+>>>>>>>>>>>]<>+<[>-]>[<<<<<<+>>>>>>->]<<[-]<<<]  P marks the skipped centre when folding
+<<[->>-<<]>>  LR is one unless skipped
[  emit this slot
-<<+>>  P is the else flag
<<<<<<<<[->>>>>>>>>>>+>+<<<<<<<<<<<<]>>>>>>>>>>>>[-<<<<<<<<<<<<+>>>>>>>>>>>>]<  X is a copy of D
[  delta nonzero
[-]<<<<<->>>>>  no else
>>+<<<<<<[->>>>+>+<<<<<]>>>>[-<<<<+>>>>]>[[-]>+<]>.[-]  opcode one or two
<<<<<<<<<<<<.  offset
>>>>>>[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<  X is a copy of S
-->+<[>-]>[<<<<<<<<<<<<[->>>>>>>>>>>>>-<<<<<<<<<<<<<]>>>>>>>>>>>>>[-<<<<<<<<<<<<<+>>>>>>>>>>>>>]<<>->]<<++[-]  negate D for an incrementing counter
<<<<<<<<<<<.>>>>>>>>>>>  factor
]
<<<<<[-<<<[->>>>>>>>+>+<<<<<<<<<]>>>>>>>>>[-<<<<<<<<<+>>>>>>>>>]<[[-]>>+++.[-]<<<<<<<<<<<<.>>>>>>>>>>]<<<<<]  otherwise a check if marked
>>
]
<<<<<<<<[-]>>>[-]  clear D and CK
>>>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]  carry S and M on
>>>>>>  next slot V
]
>>>>>>>>[[-]>>>>>>.<<<<<<]>>[[-]>>>>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[-]<<<<]  folded form ends with clear and a guard close
<<<<<<<<<<<<<<<<<<<<<[<<<<<<<<<<<<<<<<]  scan back to the cursor
<<<[->>>>>>>>>>+>+<<<<<<<<<<<]>>>>>>>>>>>[-<<<<<<<<<<<+>>>>>>>>>>>]<[[-]>>++++.[-]<<<<<<<<<<<<.>>>>>>>>>>]  a nonzero final offset is a move
<[->+>+<<]>>[-<<+>>]<  X is a copy of K
---->+<[>-]>[<>>+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[-]<<>->]<<->+<[>-]>[<>>++++++++++++++++++++++++++++++++++++++++++++++.[-]<<>->]<<->+<[>-]>[<>>++++++++++++++++++++++++++++++++++++++++++++.[-]<<>->]<<++++++[-]  close  output  input
<<<<<<<<<<<<<[<<<<<<<<<<<<<<<<]  to the left guard
>>>>>>>>>>>>>>>>[>[-]>>>>>[-]+>[-]>>>>>[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]<<<<<<<<<<<<>>>>>>>>>>>>>>>>]  reset the window and carry K right
>>>[>>>>>>>>>[-<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>]<<<<<<<<<<<<<<<<<<<<<<<<<]  carry K back to the centre
<<+>>>>>->+>>>>>  new centre cursor with RUN
[->+>+<<]>>[-<<+>>]<  X is a copy of K
--->+<[>-]>[<<<<<<+>>>>>>->]<<---->+<[>-]>[<<<<<<<->>>>>>>->]<<+++++++[-]  an open is pending  an end stops
<[-]  K cleared
]  end of flush
<<<<<  back to RUN
]

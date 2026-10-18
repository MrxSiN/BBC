# BBC portable compiler
# PURPOSE Validate framed source and emit a BBX module
# INPUT Raw little endian source length then source then byte one
# OUTPUT BBX magic version status then count and commands on success
# LIMIT At most three thousand eight hundred forty commands
# LIMIT At most two hundred fifty five nested loops
# LAYOUT Each slot has sixteen cells and slot zero is a sentinel
# CELLS Zero stored flag and one raw source byte
# CELLS Two and three comparison scratch and four command flag
# CELLS Five bracket depth and six temporary flag
# CELLS Seven and eight command count low and high
# CELLS Nine and ten remaining raw length low and high
# CELLS Eleven bracket error and twelve size error
# CELLS Thirteen loop flag and fourteen and fifteen bracket flags

# Read length into the first working slot
>>>>>>>>>>>>>>>>
>>>>>>>>>,>,

# Set loop flag if either length byte is nonzero
<[-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<
[[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]
>>>>>>>>
[-<<<<<<<<+>+>>>>>>>]<<<<<<<[->>>>>>>+<<<<<<<]<
[[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]
>>>>>>>>>>>
[
  [-]
  <<<<<<<<<<<<,

  # Recognize right pointer movement
  [->+>+<<]>>[-<<+>>]<
  --------------------------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize left pointer movement
  [->+>+<<]>>[-<<+>>]<
  ------------------------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize increment
  [->+>+<<]>>[-<<+>>]<
  -------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize decrement
  [->+>+<<]>>[-<<+>>]<
  ---------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize output
  [->+>+<<]>>[-<<+>>]<
  ----------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize input
  [->+>+<<]>>[-<<+>>]<
  --------------------------------------------
  >+<[[-]>[-]<]>[->+<]<<

  # Recognize opening bracket
  [->+>+<<]>>[-<<+>>]<
  ------------------------------------------------------------
  -------------------------------
  >+<[[-]>[-]<]>[->+>>>>>>>>>>+<<<<<<<<<<<]<<

  # Recognize closing bracket
  [->+>+<<]>>[-<<+>>]<
  ------------------------------------------------------------
  ---------------------------------
  >+<[[-]>[-]<]>[->+>>>>>>>>>>>+<<<<<<<<<<<<]<<

  # Increase depth and reject wrapping nesting
  >>>>>>>>>>>>>[
    -<<<<<<<<<+
    [-<<<+>+>>]<<[->>+<<]<
    >>>>+<<<<[[-]>>>>[-]<<<<]>>>>
    [[-]>>>>>>[-]+<<<<<<]
    >>>>>>>>
  ]

  # Decrease depth or mark an unmatched closing bracket
  >[
    -<<<<<<<<<<
    [-<<<+>+>>]<<[->>+<<]<
    >>>>+<<<<[[-]>>>>[-]<-<<<]>>>>
    [[-]>>>>>[-]+<<<<<]
    >>>>>>>>>
  ]

  # Subtract one from the remaining length with borrow
  <<<<<<
  [-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<
  >>>>+<<<<[[-]>>>>[-]<<<<]>>>>
  [->>>>-<<<<]>>>-

  # Continue if the low remaining length is nonzero
  [-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<
  [[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]

  # Continue if the high remaining length is nonzero
  >>>>>>>>
  [-<<<<<<<<+>+>>>>>>>]<<<<<<<[->>>>>>>+<<<<<<<]<
  [[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]

  # Refuse another command when the high count reaches fifteen
  >>>>>>
  [-<<<<<<+>+>>>>>]<<<<<[->>>>>+<<<<<]<
  ---------------
  >>>>+<<<<[[-]>>>>[-]<<<<]>>>>
  [[-]<<[[-]>>>>>>>>[-]+<<<<<<<<]>>]

  # Store only instructions and carry live state to the next slot
  <<[
    -<<<<+>>>>>
    [->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >>+
    [-<<<<<+>+>>>>]<<<<[->>>>+<<<<]<
    >>>>+<<<<[[-]>>>>[-]<<<<]>>>>
    [->>+<<]>
    [->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >[->>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<]
    >>>>>>>
  ]
  >>>>>>>>>
]

# Remaining depth means an unclosed opening bracket
<<<<<<<<[
  [-]>>>>>>[-]+<<<<<<
]

# Read required terminator and remember a framing failure
<<<<,-[[-]>>>>>>>>>>>>>+<<<<<<<<<<<<<]

# Select bracket then size then framing status
>>>>>>>>>>[[-]<<<<<[-]++>>>>>]
>[[-]<<<<<<[-]+++>>>>>>]
>>[[-]<<<<<<<<[-]+>>>>>>>>]

# Emit BBX magic and a separate binary version after validation
<<<<<<<<<<<<<[-]
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++.
.
++++++++++++++++++++++.
[-]+.
>>>>>.

# Emit payload only when status is zero
>>>>>>>+<<<<<<<[[-]>>>>>>>[-]<<<<<<<]
>>>>>>>[
  [-]<<<<<<.>.
  <<<<<<<<
  <<<<<<<<<<<<<<<<[<<<<<<<<<<<<<<<<]
  >>>>>>>>>>>>>>>>
  [>. <>>>>>>>>>>>>>>>>]
]

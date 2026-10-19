# BBC portable compiler
# PURPOSE Validate framed source and emit a BFX module
# INPUT Raw little endian source length then source then byte one
# OUTPUT BFX magic version status then count and commands on success
# LIMIT At most three thousand eight hundred forty commands
# LIMIT At most two hundred fifty five nested loops
# LAYOUT Each slot has sixteen cells and slot zero is a sentinel
# CELLS Zero stored flag and one raw source byte
# CELLS Two and three comparison scratch and four command flag
# CELLS Five bracket depth and six temporary flag
# CELLS Seven and eight command count low and high
# CELLS Nine group byte counter and ten later full groups
# CELLS Eleven bracket error and twelve size error
# CELLS Thirteen loop flag and fourteen and fifteen bracket flags

# Read length into the first working slot
>>>>>>>>>>>>>>>>
>>>>>>>>>,>,

# Reject source lengths whose complete frame cannot fit the native input view
# Preserve length bytes and consume the whole declared frame even on error
[-<<<<<<<<+>+>>>>>>>]<<<<<<<[->>>>>>>+<<<<<<<]<+
>>>>+<<<<[[-]>>>>[-]<<<<]>>>>
[
  -
  >>>[-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<+
  >>+<<[[-]>>[-]<<]>>
  [[-]>>>>>>>>[-]+<<<<<<<<]
  >>>>>[-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<++
  >>+<<[[-]>>[-]<<]>>
  [[-]>>>>>>>>[-]+<<<<<<<<]
  >>
]
>>>>

# Set loop flag if either length byte is nonzero
<[-<<<<<<<+>+>>>>>>]<<<<<<[->>>>>>+<<<<<<]<
[[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]
>>>>>>>>
[-<<<<<<<<+>+>>>>>>>]<<<<<<<[->>>>>>>+<<<<<<<]<
[[-]>>>>>>>>>>>[-]+<<<<<<<<<<<]
>>>>>>>>>>>

# Prepare counted byte groups only for a nonempty source
[
  -<<<<<<<<<+
  >>>>>
  [->>>>>+>+<<<<<<]>>>>>>[-<<<<<<+>>>>>>]<
  >+<[[-]>[-]<]>
  [-<<<<<->>>>>]
  <<
]
<<<<<<<<<[->>>>>>>>>+<<<<<<<<<]>>>>>>>>>

[
  [-]+
  <<<<<<<<<<<<,

  # Decode opcodes with one preserved byte copy
  [->+>+<<]>>[-<<+>>]<
  >>+<<
  -------------------------------------------
  [
    -[
      -[
        -[
          --------------[
            --[
              -----------------------------
              >>>>>>>>>>>>+<<<<<<<<<<<<
              [
                >>>>>>>>>>>>[-]<<<<<<<<<<<<
                --
                >>>>>>>>>>>>>+<<<<<<<<<<<<<
                [
                  [-]>>[-]>>>>>>>>>>>[-]<<<<<<<<<<<<<
                ]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
  <

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

  # Count remaining bytes within this group
  <<<<<<
  -[->>>>>+>+<<<<<<]>>>>>>[-<<<<<<+>>>>>>]<
  >+<[[-]>[-]<]>
  [
    -<<[-]<<<
    [->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<
    [[-]<<<<->>>+>]
    >
  ]

  # Refuse another command when the high count reaches fifteen
  <<<<<<<
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

# Emit BFX magic and a separate binary version after validation
<<<<<<<<<<<<<[-]
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++.
++++.
++++++++++++++++++.
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

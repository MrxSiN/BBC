# BBC text source bootstrap framing
# PURPOSE Buffer source and emit a complete compiler input frame
# INPUT Text bytes until NUL or physical EOF
# OUTPUT Little endian length then original bytes then byte one
# FAILURE Overlarge text emits no bytes
# LIMIT At most seven thousand six hundred eighty text bytes
# shortcut: NUL ends text input; use length framing for binary sources
# LAYOUT Eight cell slots with an untouched zero sentinel
# CELLS Zero stored flag and one original text byte
# CELLS Two and three byte count low and high
# CELLS Four and five comparison scratch and restoration
# CELLS Six temporary flag and seven sticky size failure

>>>>>>>>>,
[
  # Test the high byte count against thirty
  >>[->+>+<<]>>[-<<+>>]<
  ------------------------------
  >>+<<[[-]>>[-]<<]>>
  [[-]>[-]+<<<<<<[-]>>>>>]
  <<<<<

  # Retain the text byte and advance only within the limit
  [
    <+>>+
    [->>+>+<<<]>>>[-<<<+>>>]<
    >>+<<[[-]>>[-]<<]>>
    [-<<<+>>>]
    <<<<[->>>>>>>>+<<<<<<<<]
    >[->>>>>>>>+<<<<<<<<]
    >>>>>>
  ]
  ,
]

# Suppress the complete frame if the size limit was exceeded
>>>>>+>[
  [-]<[-]>
]<[
  [-]<<<<.>.
  <<<
  <<<<<<<<[<<<<<<<<]
  >>>>>>>>
  [>.<>>>>>>>>]
  +.[-]
]

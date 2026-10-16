# Streamed Android source filter and wide count prototype
# Authoritative code is ordinary Brainfuck
# Source bytes use FF escaping as defined in the transport document
# Tape cell zero stores input error status
# Tape cell seven marks a completed command
# Tape cells eight nine ten store a little endian command count
# Tape cell eleven is a zero test flag
# Tape cells twelve thirteen hold temporary copies
# Tape cell fourteen marks a counter overflow
# Output is filtered commands followed by three count bytes and one status byte
# A nonzero status invalidates all preceding output
# No code generation or loop relocation occurs in this prototype
>,[[->+>+<<]>>[-<<+>>]<------------------------------------------->>>+<<<>>>[-<<<[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]>>+<<<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<>>>]>[-<+>]<<<<->>>[-<<<[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]>>+<<<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<>>>]>[-<+>]<<<<->>>[-<<<[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]>>+<<<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<>>>]>[-<+>]<<<<->>>[-<<<[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]>>+<<<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<>>>]>[-<+>]<<<<>>>[[-]<<<--------------[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<--[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<-----------------------------[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<--[->+>+<<]>>[-<<+>>]<>+<[[-]>[-]<]>[[-]<<<.>>>>>>+<<<<<<>>>]<<>>>]<<<[-]<[->+>+<<]>>[-<<+>>]<+>+<[[-]>[-]<]>[[-]<<,>>>+<<<[->+>+<<]>>[-<<+>>]<->+<[[-]>[-]<]>[[-]>[-]<]<<[->+>+<<]>>[-<<+>>]<-->+<[[-]>[-]<]>[[-]>[-]<]<<>>]<<,>>>[[-]<<<<+>[-]>>>]<<<>>>>>>[[-]>+[->>>>+>+<<<<<]>>>>>[-<<<<<+>>>>>]<<+>[[-]<[-]>]<[[-]<<+[->>>+>+<<<<]>>>>[-<<<<+>>>>]<<+>[[-]<[-]>]<[[-]<+[->>+>+<<<]>>>[-<<<+>>>]<<+>[[-]<[-]>]<[[-]>>>+<<<]]]<<<<]<<<<<<]>>>>>>>>>>>>>[[-]<<<<<<<<<<<<<<++>>>>>>>>>>>>>>]<<<<<<.>.>.<<<<<<<<<<.

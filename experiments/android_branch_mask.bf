# Convert brackets into harmless instruction slots for the native image patcher
# Input is a filtered command stream of at most ten accepted instructions
# This compiler stage only replaces loop brackets with increment operations
,[>[-]<[->+>+<<]>>[-<<+>>]<------------------------------------------------------------------------------------------->>[-]+<<[[-]>>[-]<<]>>[-<<<[-]+++++++++++++++++++++++++++++++++++++++++++>>>]<<[-]<[->+>+<<]>>[-<<+>>]<--------------------------------------------------------------------------------------------->>[-]+<<[[-]>>[-]<<]>>[-<<<[-]+++++++++++++++++++++++++++++++++++++++++++>>>]<<<.,]

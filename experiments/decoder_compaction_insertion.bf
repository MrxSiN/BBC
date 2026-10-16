# In core decoder source compaction experiment
# Save two count carry lanes before using nearby scratch
<[->>>>>>>>>>>>>>>>>>>>>>+<<<<<<<<<<<<<<<<<<<<<<]>
>>>[->>>>>>>>>>>>>>+<<<<<<<<<<<<<<]<<<
# Preserve the previous source byte and copy it for classification
<<<<[->+>>>>+<<<<<]>>>>>[-<<<<<+>>>>>]<<<<
# Compare the sentinel
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
-------------------------------------------
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
-
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
-
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
-
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
--------------
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
--
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
-----------------------------
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Compare one source command byte
--
[->>+>>>>+<<<<<<]>>[-<<+>>]+>>>>[<<<<[-]>>>>[-]]<<<<[->>+<<]<<
# Keep a matching byte or reclaim the ignored source record
[-]+>>>>[-<<<<[-]>>>>>>>>>>>>+<<<<<<<<]<<<<[-<[-]>>>>[<<<<+>>>>-]>>[-]<<<<<]>>>>>>>>>>>>[->>>>]<<<<<<<<<<<<<
# Restore the original count carry lanes
>>>>>>>>>>>>>>>>>[-<<<<<<<<<<<<<<+>>>>>>>>>>>>>>]<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>[-<<<<<<<<<<<<<<<<<<<<<<+>>>>>>>>>>>>>>>>>>>>>>]<<<<<<<<<<<<<<<<<<<<<

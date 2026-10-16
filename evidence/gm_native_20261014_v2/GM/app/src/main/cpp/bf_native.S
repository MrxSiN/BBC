.section .text.bf,"ax",%progbits
.balign 16
.global bf_row
.hidden bf_row
bf_row:
.incbin "D:/GitHub/brainfuckC/evidence/gm_native_20261014_v2/GM/app/src/main/cpp/row.elf"
.balign 16
.global bf_scope
.hidden bf_scope
bf_scope:
.incbin "D:/GitHub/brainfuckC/evidence/gm_native_20261014_v2/GM/app/src/main/cpp/scope.elf"
.section .note.GNU-stack,"",%progbits

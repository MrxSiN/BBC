.text
.global probe
probe:
 mov x10,xzr
 mov x11,x4
 mov x12,xzr
 mov x13,xzr
 mov x16,x6
 mov x14,xzr
 cmp x5,#32
 cmp x10,x5
 add x11,x4,x10
 ldrb w9,[x0,x12]
 strb w9,[x2,x13]
 cmp x12,x1
 cmp x13,x3
 sub x6,x6,#1
 add x12,x12,#1
 add x13,x13,#1
 sub x1,x16,x6
 str x13,[x7]
 mov w0,w14
 mov w14,#2
 ret

#!/usr/bin/env python3
"""Independent development-only Brainfuck interpreter. Never performs compilation."""
import sys

OPS=b'<>+-.,[]'

def execute(source:bytes, stdin:bytes=b'', *, max_steps=50_000_000, tape_len=65536, tape_snapshot=None):
    src=bytes(c for c in source if c in OPS)
    jump={}; stack=[]
    for pc,c in enumerate(src):
        if c==91: stack.append(pc)
        if c==93:
            if not stack: raise ValueError('unexpected ]')
            a=stack.pop();jump[a]=pc;jump[pc]=a
    if stack: raise ValueError('unclosed [')
    tape=bytearray(tape_len)
    p=pc=steps=ipos=0; result=bytearray()
    while pc<len(src):
        steps+=1
        if steps>max_steps: raise TimeoutError('step limit')
        c=src[pc]
        if c==62:p+=1
        elif c==60:p-=1
        elif c==43:tape[p]=(tape[p]+1)&255
        elif c==45:tape[p]=(tape[p]-1)&255
        elif c==46:result.append(tape[p])
        elif c==44:
            tape[p]=stdin[ipos] if ipos<len(stdin) else 0
            if ipos<len(stdin):ipos+=1
        elif c==91 and not tape[p]:pc=jump[pc]
        elif c==93 and tape[p]:pc=jump[pc]
        if not 0<=p<tape_len:raise IndexError('pointer out of tape')
        pc+=1
    if tape_snapshot is not None:tape_snapshot[:]=tape
    return bytes(result),steps

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: reference.py file.bf < stdin > stdout')
    data=sys.stdin.buffer.read(); stdout,steps=execute(open(sys.argv[1],'rb').read(),data)
    sys.stdout.buffer.write(stdout)

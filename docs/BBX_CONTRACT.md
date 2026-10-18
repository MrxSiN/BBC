# BBX portable boundary

Status: PROTOTYPE. This is BBC's portable boundary to the separate XAX project.

All integers below are unsigned little endian. One invocation compiles one
request. Transport bytes are data, never Brainfuck instructions.
BBX means Brainfuck Ballsdeep XAX. Save module records with the `.bbx`
extension. The format name is BBX; its version is a separate metadata byte.

## Request

`source_length:u16 || source:byte[source_length] || 01`

The required final byte is hex `01`. Length counts raw bytes, including NUL,
ignored text and whitespace. It must not exceed 65,535. A sender must reject
larger sources before encoding; splitting or wrapping the length is invalid.
The frontend reads precisely this frame; subsequent bytes belong to the caller
and are not part of this request. A missing or different terminator fails.
In particular, zero on physical EOF cannot masquerade as the terminator.

## Response

Success: `42 42 58 || version:u8 || 00 || instruction_count:u16 || instructions`

Failure: `42 42 58 || version:u8 || error:u8` and nothing else.

`42 42 58` is ASCII `BBX`. The initial supported version is binary `01`,
not ASCII `1`. Version is at offset 3, status at offset 4, count at offsets
5 and 6, and success payload begins at offset 7. A failure is exactly five
bytes. Error values:

| Value | Meaning |
|---|---|
| 0 | Success; exactly the stated number of instruction bytes follows |
| 1 | Missing or invalid request terminator, including truncated input |
| 2 | Unmatched brackets |
| 3 | Instruction count or nesting exceeds this frontend's supported limit |

If several errors occur, framing wins, then size, then unmatched brackets.
No output is emitted before the entire declared source and terminator have
been read and validation has finished. A failed output write is a transport
failure: the caller must not publish an incomplete response as a module.

## Initial implementation limits

`compiler/compiler.bf` accepts at most 3,840 filtered instructions and 255
nested loops. These are compiler resource limits, not language changes.
No optimization is performed. Every other source byte is ignored, including
raw NUL and FF. A hash character has no lexical significance. Brackets inside
annotations still participate in validation.

The compiler uses a zeroed 65,536-byte tape. It reserves a sentinel slot and
sixteen cells per stored instruction plus one working slot. At the instruction
limit its working slot starts at 61,456 and ends at 61,471. The compiler's own
executable stream must fit these same limits; compiling that stream alone is
not native self-hosting.

## Compatibility

This replaces the prototype `BFI1` header (`42 46 49 31`). Existing records
must be recompiled; renaming their file extension does not convert them.
Request framing, status meanings, counts and source-language semantics are
unchanged. No native XAX importer has been released, so there is no deployed
adapter compatibility path to retain. Do not accept the old magic as BBX.
Future incompatible records require a new version byte; compatible metadata
extensions also require an explicit documented framing rule. No extension
mechanism is added until a concrete use requires it.

## Import requirements

An XAX importer must check the three magic bytes, supported version, exact
response length, status, supported limits, all payload bytes and bracket
balance before constructing a graph.
It must reject error records and trailing or missing response bytes. A BBX
module fixes the semantics in [the profile](BRAINFUCK_PROFILE.md); it carries
no target selection or capability permission. The importer must reject a
target that cannot enforce this profile and the decision buffer contract.

See [XAX integration](XAX_INTEGRATION.md) for the inspected construction APIs
and what has actually been implemented.

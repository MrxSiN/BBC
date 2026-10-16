"""Raw byte transport only. No Brainfuck parsing or code generation.

A 0x00 byte is the BF runtime's EOF value, so compiler stdin is stuffed:
  raw 0x00 -> FF 01
  raw 0xFF -> FF 02
All other raw bytes pass through unchanged. The BF compiler itself validates
escapes, recognizes commands, checks brackets, and constructs the ELF.
"""

def encode_source(data: bytes) -> bytes:
    result = bytearray()
    for byte in data:
        if byte == 0:
            result.extend((255, 1))
        elif byte == 255:
            result.extend((255, 2))
        else:
            result.append(byte)
    return bytes(result)


def extract_artifact(stream: bytes) -> bytes:
    if not stream:
        raise ValueError('compiler returned no bytes')
    if stream[-1] != 0:
        raise ValueError(f'compiler rejected input (status {stream[-1]})')
    return stream[:-1]

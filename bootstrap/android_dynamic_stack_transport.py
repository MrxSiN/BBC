#!/usr/bin/env python3
"""Generic file-backed eight-byte stack service for a standard-BF pair matcher.

The Brainfuck stage, not this transport, requests next events, issues PUSH/POP,
chooses pair output, tests empty stack, and rejects malformed nesting. The
transport only stores opaque bytes; it neither reads BF source nor matches tags.
Input event files are nine-byte records (event tag, eight opaque bytes).
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_STAGE=ROOT/'build/android_dynamic_stack_pairs_x86_64_linux.elf'
SCANNER=ROOT/'build/android_100m_rle_scan_framed_x86_64_linux.elf'
BRIDGE=ROOT/'build/android_pair_event_bridge_x86_64_linux.elf'

def read_exact(stream,n:int)->bytes:
    buf=bytearray()
    while len(buf)<n:
        b=stream.read(n-len(buf))
        if not b:raise ValueError('truncated BF stack device request')
        buf.extend(b)
    return bytes(buf)


def pair_events(events:Path, output:Path, *, stage:Path=DEFAULT_STAGE,
                max_pairs:int|None=None)->dict:
    if max_pairs is not None and max_pairs<0:raise ValueError('negative output quota')
    output.parent.mkdir(parents=True,exist_ok=True)
    events_size=events.stat().st_size
    if events_size%9:raise ValueError('event transport length not multiple of nine')
    file_fd,temp_name=tempfile.mkstemp(prefix='.bf-stack-pairs-',dir=output.parent)
    temp_path=Path(temp_name)
    process=None
    try:
        with events.open('rb') as event_file, tempfile.TemporaryFile(mode='w+b') as store, os.fdopen(file_fd,'wb') as target:
            process=subprocess.Popen([str(stage)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,bufsize=0)
            assert process.stdout is not None and process.stdin is not None
            depth=0;peak=0;sent=0;pairs=0;terminated=False
            while not terminated:
                operation=read_exact(process.stdout,1)
                if operation==b'R':
                    event=event_file.read(9)
                    if not event:event=b'\0'*9
                    elif len(event)!=9:raise ValueError('truncated event file')
                    else:sent+=1
                    process.stdin.write(event)
                elif operation==b'P':
                    opaque=read_exact(process.stdout,8)
                    store.seek(depth*8);store.write(opaque)
                    depth+=1;peak=max(peak,depth)
                elif operation==b'O':
                    if depth:
                        depth-=1;store.seek(depth*8)
                        data=store.read(8)
                        if len(data)!=8:raise RuntimeError('stack backing file failure')
                        process.stdin.write(b'\1'+data)
                    else:process.stdin.write(b'\0'*9)
                elif operation==b'M':
                    opening_closing=read_exact(process.stdout,16)
                    if max_pairs is not None and pairs>=max_pairs:
                        raise ValueError('pair output exceeds caller resource policy')
                    target.write(b']'+opening_closing);pairs+=1
                elif operation==b'E':
                    process.stdin.write(b'\1' if depth==0 else b'\0')
                elif operation==b'D':
                    status=read_exact(process.stdout,1)
                    if status!=b'\0':raise ValueError('Brainfuck bracket stage rejected mismatched nesting')
                    if process.stdout.read(1):raise ValueError('BF pairing stage output after completion')
                    if event_file.read(1):raise ValueError('unexpected trailing BF bracket events')
                    terminated=True
                else:raise ValueError(f'invalid BF stack protocol operation: {operation.hex()}')
            process.stdin.close()
            if process.wait()!=0:raise RuntimeError('BF bracket stage exited unsuccessfully')
            target.flush();os.fsync(target.fileno())
        temp_path.replace(output)
        return {'bracket_event_records':sent,'matched_pairs':pairs,'maximum_observed_depth':peak,
                'stack_storage':'GROWING_FILE_BACKED_8_BYTE_LIFO',
                'compiler_pairing_control':'STANDARD_BRAINFUCK',
                'fixed_nesting_depth_limit':None,'android_machine_code_generated':False}
    finally:
        if process is not None and process.poll() is None:
            process.kill();process.wait()
        temp_path.unlink(missing_ok=True)



def pair_source_dynamic(source:Path, output:Path, *, max_raw_bytes:int|None=None,
                        max_pairs:int|None=None)->dict:
    """Compose two BF scanner/bridge stages and the BF-controlled stack device.

    Python only forwards byte streams, checks framing, and hosts generic memory.
    No Python source classification or bracket matching is performed.
    The existing BF scanner has 32-bit command positions; this is an explicit
    input range constraint, independent of the dynamically sized pairing stack.
    """
    try:
        from .android_100m_transport import compress_bytes
    except ImportError:
        from android_100m_transport import compress_bytes
    with tempfile.TemporaryFile() as wire, tempfile.TemporaryFile() as events, tempfile.TemporaryFile() as widened:
        with source.open('rb') as infile:
            raw_bytes=compress_bytes(infile,wire,mode=1,max_bytes=max_raw_bytes)
        wire.seek(0)
        first=subprocess.run([str(SCANNER)],stdin=wire,stdout=events,stderr=subprocess.PIPE,timeout=240)
        if first.returncode or first.stderr:
            raise RuntimeError('BF source scanner process failed')
        scanner_bytes=events.tell()
        if scanner_bytes<10 or (scanner_bytes-10)%5:
            raise ValueError('malformed Brainfuck source scanner frame')
        events.seek(0)
        second=subprocess.run([str(BRIDGE)],stdin=events,stdout=widened,stderr=subprocess.PIPE,timeout=240)
        if second.returncode or second.stderr:
            raise RuntimeError('BF scanner bridge process failed')
        bridge_bytes=widened.tell()
        if bridge_bytes!=((scanner_bytes-10)//5)*9+2:
            raise ValueError('BF bridge output frame size mismatch')
        widened.seek(bridge_bytes-2)
        if widened.read(2)!=b'\0\0':
            raise ValueError('BF source scanner or bridge rejected input')
        # Copy only the BF produced nine-byte opaque event records.
        # pair_events handles the final output transaction atomically.
        with tempfile.TemporaryDirectory(prefix='bf-pair-events-') as folder:
            events_path=Path(folder)/'events.bin'
            with events_path.open('wb') as materialized:
                widened.seek(0)
                remaining=bridge_bytes-2
                while remaining:
                    chunk=widened.read(min(1<<20,remaining))
                    if not chunk:raise ValueError('short widened event stream')
                    materialized.write(chunk);remaining-=len(chunk)
            result=pair_events(events_path,output,max_pairs=max_pairs)
        result.update({'source_raw_bytes':raw_bytes,
                       'scanner_bracket_occurrences':(scanner_bytes-10)//5,
                       'scanner_position_width_bits':32,
                       'pair_record_position_width_bits':64,
                       'scanner_position_ceiling_unchanged':True,
                       'android_elf_generated':False,
                       'android_device_executed':False})
        return result


def main():
    parser=argparse.ArgumentParser(description='BF-controlled dynamic file-backed stack pairing')
    parser.add_argument('events',type=Path)
    parser.add_argument('-o','--output',type=Path,required=True)
    parser.add_argument('--stage',type=Path,default=DEFAULT_STAGE)
    parser.add_argument('--max-pairs',type=int)
    a=parser.parse_args()
    print(json.dumps(pair_events(a.events,a.output,stage=a.stage,max_pairs=a.max_pairs),indent=2))
if __name__=='__main__':main()

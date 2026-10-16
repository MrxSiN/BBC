#!/usr/bin/env python3
"""Offline audit of archived Android-native BF compiler bootstrap witnesses.

This can verify hashes, compiler-produced files and reference outputs. It does
NOT replay the target-device execution recorded by the ADB runner.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'tools')]
from source_check import check_source
from reference import execute

BASE=ROOT/'evidence/android_native_selfhost_20261013_v3'

def sha(blob): return hashlib.sha256(blob).hexdigest()

def audit():
    report=json.loads((BASE/'report.json').read_text())
    source=(ROOT/report['source']).read_bytes()
    bf=check_source(source)
    assert len(source)==report['source_bytes']
    assert len(bf)==report['bf_instructions']
    assert sha(source)==report['source_sha256']
    assert sha(bf)==report['filtered_sha256']
    assert len(bf)<=report['source_cap_commands']
    expected_len=208+64*len(bf)
    images=[]
    for stage in range(4):
        p=BASE/f'stage{stage}.elf'; image=p.read_bytes()
        assert len(image)==report['compiler_elf_bytes']==expected_len
        assert sha(image)==report['compiler_elf_sha256']
        assert image[:4]==b'\x7fELF' and struct.unpack_from('<H',image,18)[0]==183
        assert struct.unpack_from('<Q',image,96)[0]==len(image)
        if stage>0:
            assert (BASE/f'stage{stage}.stream').read_bytes()==image+b'\0'
            assert (BASE/f'stage{stage}.timing.stderr').is_file()
            assert report['stages'][stage-1]['sha256']==sha(image)
        images.append(image)
    assert all(image==images[0] for image in images)
    assert (ROOT/'compiler/android_core.bf.notes.md').is_file()
    assert report['independent_seeds_identical'] is True
    assert report['native_stage0_1_2_3_identical'] is True
    assert report['device_properties']['ro.product.cpu.abi']=='arm64-v8a'
    assert report['device_properties']['ro.build.version.sdk']=='37'
    passed=0
    for index,case in enumerate(report['corpus']):
        program=bytes.fromhex(case['source_hex']); data=bytes.fromhex(case['input_hex'])
        image=(BASE/f'case{index}.elf').read_bytes()
        assert image==(BASE/f'case{index}.stream').read_bytes()[:-1]
        assert (BASE/f'case{index}.stream').read_bytes()[-1]==0
        assert sha(image)==case['elf_sha256']
        ops=bytes(c for c in program if c in b'><+-.,[]')
        assert len(image)==208+64*len(ops)
        try: output,_=execute(program,data,max_steps=400000); status=0
        except IndexError: output,status=b'',2
        assert status==case['status']
        assert output.hex()==case['stdout_hex']
        assert (BASE/f'case{index}.stdout').read_bytes()==output
        assert int((BASE/f'case{index}.exitcode').read_text().strip())==status
        assert (BASE/f'case{index}.stderr').read_bytes()==b''
        assert (BASE/f'case{index}.elf').read_bytes()==image
        passed+=1
    for name in ('scanner','optimizer'):
        p=ROOT/('experiments/android_source_scan.bf' if name=='scanner' else 'experiments/android_compact_optimize.bf')
        assert sha(p.read_bytes())==report['optional_stage_sources'][name]
        stream=(BASE/f'{name}.stream').read_bytes()
        image=(BASE/f'{name}.elf').read_bytes()
        assert image==stream[:-1] and stream[-1]==0
        assert sha(image)==report['optional_stage_artifacts'][name]['elf_sha256']
        assert sha(stream)==report['optional_stage_artifacts'][name]['stream_sha256']
    assert len(report['rejections'])==7
    for i,case in enumerate(report['rejections']):
        raw=(BASE/f'reject{i}.stream').read_bytes()
        assert len(raw)==case['output_bytes'] and raw[-1]==case['status']!=0
    return {'classification':'ARCHIVED_DEVICE_EVIDENCE_OFFLINE_AUDITED',
            'device_execution_replayed_in_this_environment':False,
            'native_compiler_stages_checked':4,'native_program_output_cases_checked':passed,
            'malformed_source_records_checked':len(report['rejections']),
            'compiler_bf_instructions':len(bf),'compiler_image_bytes':len(images[0]),
            'compiler_image_sha256':sha(images[0]),
            'source_sha256':sha(source),
            'recorded_device':report['device_properties']}

if __name__=='__main__':
    result=audit()
    print(json.dumps(result,indent=2))

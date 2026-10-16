#!/usr/bin/env python3
"""Execute pinned Linux-native BF stages against archived Android GM traces."""
from pathlib import Path
import hashlib
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'evidence/gm_native_20261014_v4/pipeline'
BINS = ROOT / 'build/iteration54_linux/stages'
HASHES = {
    'android_source_scan': '3f3a5a216c386e5cf051c2f67ab261f6cadc6c5250ce75e35b0d758cd2d9f06f',
    'policy_rle': '007c119abca55c4b1de6fa789e15594891db31b22f518d1ed79b762a7f01eccd',
    'policy_resolve': 'dfd8cdcbbfb3355410b6c3fe67329f30146f70bee6878eb3dad5c5b16d24e4de',
    'policy_optimize': '36d6822d23cce8c472e1437b179bd3e597d2e0edb273366a31e0da13f81447a8',
}

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    from sys import path
    path.insert(0,str(ROOT))
    from bootstrap.transport import encode_source
    evidence = []
    for name, input_path, expected_path in (
        ('android_source_scan',None,'scanner.output'),
        ('policy_rle','scanner.output','policy_rle.output'),
        ('policy_resolve','policy_rle.output','policy_resolve.output'),
    ):
        binary = ((ROOT/'build/iteration54_linux/native_parity/android_source_scan.elf')
                  if name == 'android_source_scan' else BINS/(name+'.elf'))
        assert sha(binary.read_bytes()) == HASHES[name]
        if input_path is None:
            source = (ROOT/'evidence/gm_native_20261014_v4/GM/brainfuck/src/scope.bf').read_bytes()
            payload = encode_source(source)
        else:
            payload = (BASE/input_path).read_bytes()
            if name == 'policy_rle': payload = payload[:-4]
        r = subprocess.run([str(binary)], input=payload, capture_output=True, check=True, timeout=30)
        reference = (BASE/expected_path).read_bytes()
        assert r.stdout == reference, f'{name}: native output differs from Android trace'
        print(f'PASS Linux native BF {name} exact archived-stage parity', flush=True)
        evidence.append({'stage':name,'elf_sha256':HASHES[name],
                         'input_sha256':sha(payload),'output_sha256':sha(r.stdout)})
    output=ROOT/'evidence/iteration54_linux_native_stage_parity.json'
    output.write_text(json.dumps({'classification':'LINUX_NATIVE_BF_STAGE_REPLAY_OF_ARCHIVED_ANDROID_TRACE',
                                 'stages':evidence,'fresh_android_device_execution':False},indent=2)+'\n')
    print('PASS 3 Linux-native BF stages')

if __name__=='__main__':main()

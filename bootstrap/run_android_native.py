#!/usr/bin/env python3
"""ADB byte transport for the BF-owned, self-hosted Android compiler pipeline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

try:
    from .transport import encode_source, extract_artifact
except ImportError:
    from transport import encode_source, extract_artifact

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / 'evidence/android_native_selfhost_20261013_v3'
REMOTE = '/data/local/tmp/bfc_native_pipeline'
TRANSPORT_RETRIES = 0


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checked(command):
    global TRANSPORT_RETRIES
    for attempt in range(4):
        result = subprocess.run([str(x) for x in command], capture_output=True, timeout=180)
        if result.returncode == 0: return result
        detail = (result.stderr + result.stdout).decode(errors='replace')
        transient = any(x in detail.lower() for x in ('device offline', 'device not found', "' not found", 'error: closed',
                          'transport error', 'protocol fault', 'no devices', 'connection reset'))
        if not str(command[0]).lower().endswith('adb.exe') or not transient or attempt == 3:
            raise RuntimeError(f'Command failed ({result.returncode}): {detail.strip()}')
        TRANSPORT_RETRIES += 1; time.sleep(0.5)


class NativeAndroidCompiler:
    def __init__(self, serial, work, adb=r'D:\Android\platform-tools\adb.exe', proof=None):
        self.adb = [adb, '-s', serial]
        self.work = Path(work); self.work.mkdir(parents=True, exist_ok=True)
        proof_dir = Path(proof) if proof is not None else PROOF
        proof = json.loads((proof_dir / 'report.json').read_text())
        if digest(ROOT / proof['source']) != proof['source_sha256']:
            raise ValueError('Android BF compiler source differs from self-hosting evidence')
        if digest(proof_dir / 'stage2.elf') != proof['compiler_elf_sha256']:
            raise ValueError('Android native compiler differs from self-hosting evidence')
        self.shell('mkdir -p ' + REMOTE)
        for name, path in [('compiler', proof_dir/'stage2.elf'), ('scanner', proof_dir/'scanner.elf'),
                           ('optimizer', proof_dir/'optimizer.elf')]:
            if name != 'compiler':
                src = ROOT / ('experiments/android_source_scan.bf' if name == 'scanner' else 'experiments/android_compact_optimize.bf')
                if digest(src) != proof['optional_stage_sources'][name]:
                    raise ValueError(f'{name} source differs from native build evidence')
                if path.read_bytes() != extract_artifact((proof_dir / (name+'.stream')).read_bytes()):
                    raise ValueError(f'{name} binary differs from native compiler output')
                expected = proof['optional_stage_artifacts'][name]
                if (digest(path) != expected['elf_sha256'] or
                        digest(proof_dir/(name+'.stream')) != expected['stream_sha256']):
                    raise ValueError(f'{name} artifact/stream differs from the native build manifest')
            self.push(path, name); self.shell(f'chmod 700 {REMOTE}/{name}')

    def run(self, command):
        return run_checked(command)

    def shell(self, command): return self.run(self.adb + ['shell', '-T', command])

    def push(self, path, name):
        self.run(self.adb + ['push', path, REMOTE + '/' + name])
        if self.shell(f'sha256sum {REMOTE}/{name}').stdout.decode().split()[0] != digest(path):
            raise ValueError('device byte transport changed the input')

    def stage(self, name, payload):
        path = self.work / (name + '.input'); path.write_bytes(payload); self.push(path, 'input')
        self.shell(f'{REMOTE}/{name} < {REMOTE}/input > {REMOTE}/output')
        path = self.work / (name + '.output')
        self.run(self.adb + ['pull', REMOTE + '/output', path])
        return path.read_bytes()

    def compile(self, source, compact=True):
        if len(source) > 1048576: raise ValueError('raw source byte transport cap exceeded')
        wire = encode_source(source)
        image = extract_artifact(self.stage('compiler', wire))
        if compact:
            scanned = self.stage('scanner', wire)
            if len(scanned) < 4 or scanned[-1] != 0:
                raise ValueError('BF source scanner rejected input')
            commands = scanned[:-4]
            if int.from_bytes(scanned[-4:-1], 'little') != len(commands):
                raise ValueError('BF scanner byte framing mismatch')
            image = extract_artifact(self.stage('optimizer', commands + b'\0' + image + b'\0'))
        return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path); parser.add_argument('output', type=Path)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--no-compact', action='store_true')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bfc_native_', dir=args.output.parent) as tmp:
        compiler = NativeAndroidCompiler(args.serial, tmp, args.adb)
        image = compiler.compile(args.source.read_bytes(), not args.no_compact)
        p = Path(tmp) / 'accepted.elf'; p.write_bytes(image); os.replace(p, args.output)
    print(f'Native BF Android compilation: {args.output} ({len(image)} bytes)')


if __name__ == '__main__': main()

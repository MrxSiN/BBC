"""Opaque byte transport for the standard-BF callable Android policy stages."""
import hashlib
import json
from pathlib import Path
import subprocess
import platform

try:
    from .run_android_native import NativeAndroidCompiler, REMOTE
    from .transport import encode_source, extract_artifact
    from .linux_policy_native import LinuxPolicyNative
except ImportError:
    from run_android_native import NativeAndroidCompiler, REMOTE
    from transport import encode_source, extract_artifact
    from linux_policy_native import LinuxPolicyNative

ROOT = Path(__file__).resolve().parents[1]
STAGES = ('policy_rle', 'policy_resolve', 'policy_optimize', 'policy_affine',
          'policy_oneshot', 'policy_clear56', 'policy_operands', 'policy_codegen', 'policy_elf',
          'policy_valuefold55', 'policy_oneshot55', 'policy_codegen55')


class PolicyCompiler:
    def __init__(self, work, serial=None, proof=None, backend="auto"):
        self.work = Path(work)
        self.work.mkdir(parents=True, exist_ok=True)
        self.device = NativeAndroidCompiler(serial, self.work, proof=proof) if serial else None
        if backend not in ('auto', 'linux-seed', 'linux-native', 'legacy-seed'):
            raise ValueError('unsupported policy stage execution backend')
        if serial and backend != 'auto':
            raise ValueError('device execution uses the Android-native backend')
        linux_backend = ('linux-seed' if backend == 'auto' and
                         platform.system() == 'Linux' else backend)
        self.linux = (LinuxPolicyNative(self.work,
                      mode='native' if linux_backend == 'linux-native' else 'seed')
                      if not serial and linux_backend in ('linux-seed', 'linux-native')
                      else None)
        self.inventory = {}
        for name in STAGES:
            source = ROOT / 'experiments' / (name + '.bf')
            info = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            if self.linux:
                self.linux.compile_stage(name, source.read_bytes())
                info.update(self.linux.inventory[name])
            if self.device:
                image = self.device.compile(source.read_bytes(), compact=False)
                path = self.work / (name + '.elf')
                path.write_bytes(image)
                self.device.push(path, name)
                self.device.shell(f'chmod 700 {REMOTE}/{name}')
                info['android_native_elf_sha256'] = hashlib.sha256(image).hexdigest()
            self.inventory[name] = info
        if self.linux:
            self.linux.compile_stage('android_source_scan',
                 (ROOT / 'experiments/android_source_scan.bf').read_bytes())
        (self.work / 'stages.json').write_text(json.dumps(self.inventory, indent=2) + '\n')

    def stage(self, name, payload):
        if self.device:
            output = self.device.stage(name, payload)
        elif self.linux:
            output = self.linux.stage(name, payload)
        else:
            source = ROOT / 'experiments' / (name + '.bf')
            result = subprocess.run([str(ROOT / 'build/android_optimization/seed.exe'),
                                     str(source), '10000000000'], input=payload,
                                    capture_output=True, check=True, timeout=240)
            output = result.stdout
        (self.work / (name + '.output')).write_bytes(output)
        return output

    def compile(self, source, affine=False, valuefold=False, canonical_clears=False):
        if valuefold and not affine:
            raise ValueError('valuefold requires the affine policy pipeline')
        if len(source) > 1048576:
            raise ValueError('raw policy transport byte cap exceeded')
        if self.device:
            scanned = self.device.stage('scanner', encode_source(source))
        elif self.linux:
            scanned = self.linux.stage('android_source_scan', encode_source(source))
        else:
            result = subprocess.run([str(ROOT / 'build/android_optimization/seed.exe'),
                                     str(ROOT / 'experiments/android_source_scan.bf')],
                                    input=encode_source(source), capture_output=True,
                                    check=True, timeout=60)
            scanned = result.stdout
        if len(scanned) < 4 or scanned[-1] or int.from_bytes(scanned[-4:-1], 'little') != len(scanned)-4:
            raise ValueError('BF scanner rejected source or returned invalid framing')
        payload = self.stage('policy_rle', scanned[:-4])
        if canonical_clears:
            payload = self.stage('policy_clear56', payload)
            if len(payload) < 2 or payload[-2:] != b'\0\0':
                raise ValueError('BF clear-loop canonicalization rejected policy')
        for name in ('policy_resolve', 'policy_optimize') + (('policy_affine', 'policy_valuefold55', 'policy_oneshot55') if valuefold else ('policy_affine', 'policy_oneshot') if affine else ()):
            payload = self.stage(name, payload)
            if len(payload) < 2 or payload[-2:] != b'\0\0':
                raise ValueError(f'BF {name} rejected policy')
        payload = self.stage('policy_operands', payload)
        if len(payload) < 2 or payload[-2:] != b'\0\0':
            raise ValueError('BF operand encoder rejected policy')
        code = self.stage('policy_codegen55' if valuefold else 'policy_codegen', payload)
        extract_artifact(code)
        return extract_artifact(self.stage('policy_elf', code))

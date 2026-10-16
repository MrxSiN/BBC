"""Run policy compiler stages as Linux-native machine code produced by Brainfuck.

The installed self-hosted Linux BF compiler emits each stage's ELF.  This
module transports raw input/output bytes; it never parses policy records,
optimizes BF, encodes AArch64 instructions or edits emitted machine bytes.
"""
import hashlib
from pathlib import Path
import subprocess
import shutil

try:
    from .transport import encode_source, extract_artifact
except ImportError:
    from transport import encode_source, extract_artifact

ROOT = Path(__file__).resolve().parents[1]
MAX_STAGE_COMMANDS = 16128


class LinuxPolicyNative:
    def __init__(self, work, compiler=None, *, mode="seed"):
        if mode not in ('seed', 'native'):
            raise ValueError('unknown Linux BF execution mode')
        self.mode = mode
        self.work = Path(work)
        self.work.mkdir(parents=True, exist_ok=True)
        self.compiler = Path(compiler or ROOT / 'build/compiler_x86_64_linux.elf').resolve()
        source_proof = ROOT / 'evidence/selfhost.json'
        import json
        proof = json.loads(source_proof.read_text())
        digest = hashlib.sha256(self.compiler.read_bytes()).hexdigest()
        if digest != proof['artifact_elf_sha256']:
            raise ValueError('Linux BF compiler differs from recorded self-hosted ELF')
        self.inventory = {}
        if self.mode == 'seed':
            self.seed = self.work / 'independent_bf_interpreter'
            source = ROOT / 'bootstrap/policy_seed_runs.c'
            subprocess.run(['cc', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            str(source), '-o', str(self.seed)], check=True, timeout=35)

    def compile_stage(self, name, source):
        source = bytes(source)
        commands = sum(source.count(bytes([c])) for c in b'><+-.,[]')
        if not 0 < commands <= MAX_STAGE_COMMANDS:
            raise ValueError(f'{name}: BF compiler input bound exceeded')
        if self.mode == 'seed':
            self.inventory[name] = {
                'source_sha256': hashlib.sha256(source).hexdigest(),
                'stage_execution': 'C_RLE_SEED_INTERPRETS_STANDARD_BF',
                'source_commands': commands,
            }
            return ROOT / 'experiments' / (name + '.bf')
        process = subprocess.run([str(self.compiler)], input=encode_source(source),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 check=True, timeout=120)
        elf = extract_artifact(process.stdout)
        if not elf.startswith(b'\x7fELF\x02\x01') or elf[18:20] != b'\x3e\x00':
            raise ValueError(f'{name}: native BF compiler emitted invalid ELF')
        path = self.work / (name + '.elf')
        path.write_bytes(elf)
        path.chmod(0o700)
        self.inventory[name] = {
            'source_sha256': hashlib.sha256(source).hexdigest(),
            'linux_native_elf_sha256': hashlib.sha256(elf).hexdigest(),
            'linux_native_elf_bytes': len(elf),
            'source_commands': commands,
        }
        return path

    def stage(self, name, payload):
        binary = ((ROOT / 'experiments' / (name + '.bf')) if self.mode == 'seed'
                  else (self.work / (name + '.elf')))
        if not binary.is_file():
            raise ValueError(f'{name}: uncompiled Brainfuck stage')
        command = ([str(self.seed), str(binary), '10000000000'] if self.mode == 'seed'
                   else [str(binary)])
        result = subprocess.run(command, input=payload, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=True, timeout=240)
        return result.stdout

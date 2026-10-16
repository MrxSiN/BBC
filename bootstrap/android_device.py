"""ADB byte transport for independent BF seed execution and native witnesses."""
import subprocess
import time

from run_android_loops import ROOT, STAGES
from run_android_optimized import OPTIMIZERS

REMOTE = '/data/local/tmp/brainfuck-opt'
BUILD = ROOT / 'build/android_optimization'
TRANSPORT_RETRIES = 0


def run(command, **kwargs):
    global TRANSPORT_RETRIES
    command = [str(part) for part in command]
    for attempt in range(6):
        try:
            return subprocess.run(command, capture_output=True, check=True, timeout=60, **kwargs)
        except subprocess.CalledProcessError as error:
            detail = (error.stderr + error.stdout).decode(errors='replace')
            transient = any(value in detail for value in (
                'device offline', "' not found", 'error: closed', 'protocol fault', 'transport error',
                'no devices/emulators found', 'connection reset'))
            if not command[0].lower().endswith('adb.exe') or not transient or attempt == 5:
                raise RuntimeError(f'Command failed ({error.returncode}): {detail.strip()}') from error
            TRANSPORT_RETRIES += 1
            services = subprocess.run([command[0], 'mdns', 'services'], capture_output=True, timeout=10)
            endpoints = [line.split()[-1] for line in services.stdout.decode().splitlines()
                         if '_adb-tls-connect._tcp' in line]
            if len(endpoints) == 1:
                subprocess.run([command[0], 'connect', endpoints[0]], capture_output=True, timeout=10)
                if len(command) > 2 and command[1] == '-s':command[2] = endpoints[0]
            time.sleep(2)


class DeviceRunner:
    def __init__(self, adb=r'D:\Android\platform-tools\adb.exe'):
        devices = run([adb, 'devices']).stdout.decode().splitlines()[1:]
        devices = [line.split()[0] for line in devices if line.endswith('\tdevice')]
        if len(devices) != 1:
            raise RuntimeError('Exactly one authorized Android device is required')
        self.adb = [adb, '-s', devices[0]]
        self.seed = 'seed'
        BUILD.mkdir(parents=True, exist_ok=True)
        self.shell(f'mkdir -p {REMOTE}')
        for seed in ('seed', 'seed_alt'):
            self.push(ROOT / 'build/android_benchmark' / seed, seed)
            self.shell(f'chmod 700 {REMOTE}/{seed}')
        for name, (source, _) in dict(STAGES, **OPTIMIZERS, core=('compiler/core.bf', '')).items():
            self.push(ROOT / source, f'{name}.bf')

    def shell(self, command):
        return run(self.adb + ['shell', '-T', command])

    def push(self, path, name):
        run(self.adb + ['push', path, f'{REMOTE}/{name}'])

    def __call__(self, stage, payload):
        path = BUILD / 'payload'
        path.write_bytes(payload)
        self.push(path, 'payload')
        limit = ' 10000000000' if stage == 'core' else ''
        self.shell(f'{REMOTE}/{self.seed} {REMOTE}/{stage}.bf{limit} < {REMOTE}/payload > {REMOTE}/stage.out')
        path = BUILD / 'stage.out'
        run(self.adb + ['pull', f'{REMOTE}/stage.out', path])
        return path.read_bytes()

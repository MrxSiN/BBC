"""Local independent BF execution; transports bytes without compiling in Python."""
import subprocess
import re
from run_android_loops import ROOT, STAGES
from run_android_optimized import OPTIMIZERS


class LocalSeedRunner:
    def __init__(self):
        self.seed = 'seed'

    def __call__(self, stage, payload):
        source = dict(STAGES, **OPTIMIZERS, core=('compiler/core.bf', ''))[stage][0]
        process = subprocess.run([str(ROOT / 'build/android_optimization' / (self.seed + '.exe')),
                                  str(ROOT / source), '10000000000'],
                                 input=payload, capture_output=True, check=True, timeout=180)
        if not re.fullmatch(rb'STEPS=\d+\r?\n', process.stderr):
            raise ValueError(f'{stage}: unexpected seed diagnostics')
        return process.stdout

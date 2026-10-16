"""Windows CRT must preserve every BF input/output byte, including Ctrl-Z."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
build = ROOT / 'build/android_optimization'
source = build / 'byte_echo.bf'
source.write_bytes(b',.')
for seed in ('seed', 'seed_alt'):
    for data in [b''] + [bytes([value]) for value in range(256)]:
        result = subprocess.run([str(build / (seed + '.exe')), str(source)],
                                input=data, capture_output=True, check=True)
        assert result.stdout == (data or b'\0'), (seed, data, result.stdout)
print('PASS 514 Windows seed byte and EOF comparisons')

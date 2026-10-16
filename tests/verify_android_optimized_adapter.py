"""The transport installs only successful BF-produced, provenance-checked images."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
build = ROOT / 'build/android_optimization'
source, target = build / 'adapter_input.bf', build / 'adapter_output.elf'
command = [sys.executable, str(ROOT / 'bootstrap/run_android_optimized.py'), str(source), str(target)]
source.write_bytes(b',[>+<-]>.')
subprocess.run(command, check=True, capture_output=True)
expected = target.read_bytes()
source.write_bytes(b'ignored words\n,[>+<-]>.')
subprocess.run(command, check=True, capture_output=True)
assert target.read_bytes() == expected
for invalid in (b'[', b'+' * 11):
    source.write_bytes(invalid)
    result = subprocess.run(command, capture_output=True)
    assert result.returncode != 0 and target.read_bytes() == expected
print('PASS optimized adapter comment invariance and two atomic rejection cases')

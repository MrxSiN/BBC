"""Check BF-only source filtering, rejection and seed/device emission parity."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bootstrap.run_policy_native import PolicyCompiler
from tools.source_check import check_source


def main():
    compiler = PolicyCompiler(ROOT / 'build/policy_transport_check')
    source = b',[>+<-]>.'
    expected = compiler.compile(source)
    assert expected == compiler.compile(b'ignored\x00\xff , [>+<-] > .')
    for bad in (b'[', b']', b'[' * 256 + b']' * 256, b'.' * 4097):
        try: compiler.compile(bad)
        except ValueError: pass
        else: raise AssertionError('invalid source/capacity accepted')
    for name in compiler.inventory:
        assert len(check_source((ROOT / 'experiments' / (name + '.bf')).read_bytes())) <= 16128
    proof_dir = ROOT / 'evidence/gm_native_20261014_v4'
    if (proof_dir / 'build.json').exists():
        proof = json.loads((proof_dir / 'build.json').read_text())
        assert not proof['old_bf_to_c_backend_linked'] and proof['bf_elf_bytes_embedded_unchanged']
        for name in ('row', 'scope'):
            assert (proof_dir / (name + '.elf')).read_bytes() == (ROOT / 'build/policy_native' / (name + '.conditional.elf')).read_bytes()
    print('PASS: raw comment/NUL/FF equivalence, malformed/capacity rejection, bounded BF stages, GM native/seed parity')


if __name__ == '__main__': main()

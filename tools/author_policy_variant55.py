"""Development-only authoring of the two opt-in native policy BF stages.

The BF code executes the policy transformation and AArch64 emission. This
helper only assembles and saves BF source; it is never part of a compile run.
"""
import inspect
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'build'))
import author_policy_stages as base


def write_stage(name, edits):
    source = inspect.getsource(getattr(base, name))
    for original, replacement in edits:
        assert source.count(original) == 1, (name, original)
        source = source.replace(original, replacement)
    namespace = vars(base).copy()
    exec(compile(source, '<stage55 authoring>', 'exec'), namespace)
    namespace[name]()


def main():
    write_stage('oneshot', [
        ("for op in b'+-,A0':", "for op in b'+-,A0K':"),
        ("b.save('policy_oneshot',", "b.save('policy_oneshot55',")])
    write_stage('codegen', [
        ("    b.eq(16, ord('F'), 7, 8, 9); b.known = None", "    def constant_store():\n        b.add(37, -8)  # previously W17 for an affine multiply; now W9\n        for i in range(37, 41):b.var(i)\n        memory(False)\n    b.eq(16, ord('K'), 7, 8, 9); b.known = None\n    b.once(7, constant_store); b.known = None\n    b.eq(16, ord('F'), 7, 8, 9); b.known = None"),
        ("b.save('policy_codegen',", "b.save('policy_codegen55',")])

if __name__=='__main__':main()

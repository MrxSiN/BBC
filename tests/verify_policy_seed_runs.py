#!/usr/bin/env python3
"""Differential-test independent BF interpreters (not code generators)."""
from pathlib import Path
import random
import json
import hashlib
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-output',type=Path)
    args=parser.parse_args()
    rng = random.Random(20261014)
    cases = [b'',b'+.',b'-.',b',.,.',b'+++[>++++<-]>.',b'+[<]',
             b'+++[-].',b'+++[+]>.',b'[',b']',b'[-<+>]',b'+[->+<]>.']
    for _ in range(140):
        prefix = b'+' * rng.randrange(22)
        body = rng.choice([b'[->+<]',b'[-]',b'[+]',b'[->++<]',
                           b'[->>+<<]',b'[->+>+<<]',b'[>+<-]', b''])
        cases.append(prefix + body + b'>.<<.')
    with tempfile.TemporaryDirectory(prefix='bfseed_') as directory:
        work = Path(directory)
        binaries = {}
        for label, src in [('canonical','bootstrap/seed_interpreter.c'),
                           ('rle','bootstrap/policy_seed_runs.c')]:
            executable = work / label
            subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',
                            str(ROOT/src),'-o',str(executable)],
                           check=True,timeout=30)
            binaries[label] = executable
        path = work / 'fixture.bf'
        for index,source in enumerate(cases):
            path.write_bytes(source)
            results = []
            for executable in binaries.values():
                out = subprocess.run([str(executable),str(path),'3000000'],
                                     input=b'\x00\xff',capture_output=True,timeout=5)
                results.append((out.returncode,out.stdout))
            assert results[0] == results[1], (index,source,results)
    if args.evidence_output:
        args.evidence_output.parent.mkdir(parents=True,exist_ok=True)
        proof={'classification':'INDEPENDENT_C_INTERPRETER_BF_EXECUTION_DIFFERENTIAL',
               'cases_passed':len(cases),'checked':'stdout_bytes_and_exit_status',
               'code_generation_by_C_interpreter':False,
               'canonical_seed_source_sha256':hashlib.sha256((ROOT/'bootstrap/seed_interpreter.c').read_bytes()).hexdigest(),
               'run_accelerated_source_sha256':hashlib.sha256((ROOT/'bootstrap/policy_seed_runs.c').read_bytes()).hexdigest()}
        args.evidence_output.write_text(json.dumps(proof,indent=2)+'\n')
    print(f'PASS {len(cases)} independent BF interpreter differentials')

if __name__ == '__main__':main()

#!/usr/bin/env python3
"""C/Rust native baseline versus self-hosted Brainfuck native on one equal algorithm.

Category B microbenchmark, not a universal language ranking. Compilers of C/Rust
are test baseline tools only, never components of the production BF compiler.
"""
import argparse
import hashlib
import json
import os
import pathlib
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = {'nested_affine': (15,17), 'nested_affine_stress': (100,101)}
INPUT = bytes([173])
REPETITIONS = 13


def run(args, **kwargs):
    return subprocess.run(args, check=True, timeout=120, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)


def run_sample(exe):
    start=time.perf_counter_ns()
    proc=run([str(exe)], input=INPUT)
    elapsed=time.perf_counter_ns()-start
    if proc.stdout != EXPECTED:
        raise AssertionError(f'invalid output from {exe}: {proc.stdout!r} {proc.stderr[:200]!r}')
    return elapsed / 1e6


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--case',choices=CASES,default='nested_affine_stress')
    opts=args.parse_args()
    a,b = CASES[opts.case]
    global EXPECTED
    EXPECTED=bytes([(INPUT[0]*a*b)&255])
    src=ROOT/f'benchmarks/programs/{opts.case}.bf'
    result_path=ROOT/f'benchmarks/results/{opts.case}.json'
    cc = shutil.which('cc') or shutil.which('gcc')
    if cc is None: raise SystemExit('C compiler unavailable: cannot run native C baseline')
    rustc = shutil.which('rustc')
    with tempfile.TemporaryDirectory(prefix='bf-native-bench-') as tmp:
        folder=pathlib.Path(tmp)
        bf=folder/'bf.elf'; c=folder/'c'; rust=folder/'rust'
        start=time.perf_counter_ns()
        generated=run([sys.executable,str(ROOT/'bootstrap/run_compiler.py'),str(src),str(bf)], cwd=ROOT)
        bf_compile_ms=(time.perf_counter_ns()-start)/1e6
        start=time.perf_counter_ns()
        run([cc, '-O3','-std=c11','-o',str(c),f'-DINNER_A={a}', f'-DINNER_B={b}',str(ROOT/'benchmarks/baselines/nested_affine.c')])
        c_compile_ms=(time.perf_counter_ns()-start)/1e6
        build={'brainfuck':{'exe':bf,'compile_ms':bf_compile_ms},'c':{'exe':c,'compile_ms':c_compile_ms}}
        if rustc:
            start=time.perf_counter_ns()
            run([rustc,'-O']+(['--cfg','bf_stress'] if opts.case=='nested_affine_stress' else [])+['-o',str(rust),str(ROOT/'benchmarks/baselines/nested_affine.rs')])
            build['rust']={'exe':rust,'compile_ms':(time.perf_counter_ns()-start)/1e6}
        # Equal execution protocol; vary run order between rounds.
        timings={k:[] for k in build}
        for i in range(REPETITIONS):
            for k in (list(build) if i%2==0 else list(reversed(build))):
                timings[k].append(run_sample(build[k]['exe']))
        sizes={k:{'binary_bytes':o['exe'].stat().st_size,'compile_ms':round(o['compile_ms'],3),
                  'raw_ms':[round(v,6) for v in timings[k]],
                  'median_ms':round(statistics.median(timings[k]),6)} for k,o in build.items()}
        fastest=min(v['median_ms'] for k,v in sizes.items() if k!='brainfuck')
        ratio=sizes['brainfuck']['median_ms']/fastest
        kernel=platform.uname()
        cpu='unknown'
        cpuinfo=pathlib.Path('/proc/cpuinfo')
        if cpuinfo.exists():
            for line in cpuinfo.read_text().splitlines():
                if line.startswith('model name'):
                    cpu=line.split(':',1)[1].strip();break
        report={'date':'2026-10-12','classification':'MEASURED: single Category B algorithm, Linux host, subprocess wall time including process startup',
              'status':'UNMET' if ratio>0.9999 else 'TENTATIVE_MET_WITHOUT_STATISTICAL_PROOF',
              'target_max_ratio':0.9999,'measured_ratio':round(ratio,6),
              'baseline_availability':{'c':True,'rust':bool(rustc)},
              'compiler_source_sha256':hashlib.sha256((ROOT/'compiler/core.bf').read_bytes()).hexdigest(),
              'workload_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
              'input_hex':INPUT.hex(),'output_hex':EXPECTED.hex(),
              'warmup_policy':'none','iterations':REPETITIONS, 'workload':opts.case, 'cpu':cpu,
              'kernel':kernel.release,'platform':platform.platform(),
              'cc':run([cc,'--version']).stdout.decode(errors='replace').splitlines()[0],
              'rustc':run([rustc,'--version']).stdout.decode(errors='replace').strip() if rustc else None,
              'data':sizes,
              'limitations':['one loop-heavy workload only','subprocess startup dominates fast baseline','C/Rust may optimize loops algebraically','uncontrolled CPU governor and background load','no confidence intervals','not Android or Windows benchmark','not a full application workload','no hardware performance counters']}
    result_path.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS identical BF/C'+('/Rust' if rustc else '')+' output')
    print(f"native BF median {sizes['brainfuck']['median_ms']:.4f} ms; C median {sizes['c']['median_ms']:.4f} ms; ratio to fastest baseline {ratio:.2f}x")
    if not rustc: print('Rust UNMEASURED: rustc unavailable')
    return report


if __name__=='__main__': main()

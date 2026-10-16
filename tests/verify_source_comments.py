#!/usr/bin/env python3
"""Verify safe ignored Brainfuck source annotations under two BF interpreters.

Compiler source is *executed* with and without annotations using identical
input; this is not evidence of user-source comment compaction in the backend.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'bootstrap'))
from source_check import check_source, source_digests
from transport import encode_source, extract_artifact


def main():
    source = (ROOT / 'compiler/core.bf').read_bytes()
    clean = check_source(source)
    assert len(source) == 15559 and len(clean) == 14859
    assert source != clean
    assert source_digests(source)[1] == 'fbb5db5a140f5b890d47915e69b975a91ea2a780681574c23f0069a5f57546af'
    # Positive and negative cases. A # does not turn Brainfuck opcodes into
    # comments. A genuine BF interpreter will execute them.
    for candidate, expected in (
        (b'# This prose is harmless\n[-]', b'[-]'),
        (b'  # Indented note\n+ # Safe note\n', b'+'),
        (b'[-] # Inline note\n', b'[-]'),
        (b'\t# Tape cell zero\r\n+\n', b'+'),
    ):
        assert check_source(candidate) == expected
    # Mutations applied to the real source must also fail, not just toy input.
    try:
        check_source(source.replace(b'# ELF startup', b'# ELF startup - unsafe', 1))
    except ValueError:
        pass
    else:
        raise AssertionError('unsafe edit to the authoritative BF comment was accepted')
    bad = (
        b'# An unsafe period.\n+',
        b'# Unsafe hyphen - is real BF\n+',
        b'+ # Inline brackets [ are real BF\n',
        b'++ # Two commas,,\n',
        b'[-]]',
        b'[[\n',
        b'x+',
    )
    for candidate in bad:
        try:
            check_source(candidate)
        except ValueError:
            continue
        raise AssertionError(f'unsafe comment or bracket structure accepted: {candidate!r}')
    cases = [b'', b'+++++.', b',.[-]', b'[->+<]>.', b'not an instruction +.\x00\xff']
    hashes = []
    with tempfile.TemporaryDirectory(prefix='bf-source-comment-') as td:
        work = pathlib.Path(td)
        full = work / 'annotated.bf'; full.write_bytes(source)
        stripped = work / 'stripped.bf'; stripped.write_bytes(clean)
        for seed_path in ('bootstrap/seed_interpreter.c', 'bootstrap/seed_interpreter_alt.c'):
            seed = work / pathlib.Path(seed_path).stem
            subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',
                            str(ROOT / seed_path),'-o',str(seed)], check=True, capture_output=True)
            for program in cases:
                encoded = encode_source(program)
                outputs = []
                for compiler in (full, stripped):
                    observed = subprocess.run([str(seed), str(compiler), '100000000000'],
                                              input=encoded, capture_output=True,
                                              timeout=90, check=True)
                    outputs.append(observed.stdout)
                assert outputs[0] == outputs[1], (seed_path, program)
                artifact = extract_artifact(outputs[0])
                assert len(artifact) == 215 + 32*sum(byte in b'><+-.,[]' for byte in program)
                hashes.append(hashlib.sha256(artifact).hexdigest())
    report = {
        'date':'2026-10-12',
        'classification':'EXECUTED source-comment safety and two-seed semantic invariance; production user-comment compaction implemented',
        'raw_source_sha256':source_digests(source)[0],
        'filtered_instruction_sha256':source_digests(source)[1],
        'raw_source_bytes':len(source),
        'instruction_bytes':len(clean),
        'ignored_comment_bytes':len(source)-len(clean),
        'positive_lint_cases':4,
        'rejected_lint_cases':len(bad),
        'bootstrap_seeds_tested':2,
        'identical_output_comparisons':2*len(cases),
        'compilation_result_sha256s':hashes,
        'limitations':[
            'The source linter validates ignored annotations but is not a production compiler frontend',
            'Compiler input now discards comment bytes and has a 16128-command capacity limit',
            'Complete compiler memory-region separation is not formally proven',
        ],
    }
    (ROOT / 'evidence/source_comments.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS 4 valid annotation cases, {len(bad)} unsafe cases rejected, '
          f'{2*len(cases)} independent BF source-comment invariance checks')


if __name__ == '__main__':
    main()

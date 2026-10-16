#!/usr/bin/env python3
"""Derive a readable view of canonical Brainfuck; never generate executable source.

Single authority: compiler/core.bf. Comments live in its hash-bound companion file.
No annotation or generated view is input to the compiler.
"""
import argparse
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'compiler/core.bf'
NOTES = ROOT / 'compiler/core.bf.notes.md'
VIEW = ROOT / 'docs/ANNOTATED_VIEW.md'
if __package__:
    from .source_check import check_source, source_digests
else:
    from source_check import check_source, source_digests


def annotated_view() -> str:
    source = SOURCE.read_bytes()
    code = check_source(source)
    notes = NOTES.read_text(encoding='utf-8')
    digest, filtered_digest = source_digests(source)
    if (f'Source SHA-256: `{digest}`' not in notes or
            f'Filtered instruction SHA-256: `{filtered_digest}`' not in notes):
        raise ValueError('annotation revision or executable instruction digest is stale')
    ranges = [(int(a), int(b), description) for a, b, description in
              re.findall(r'^\| `(\d+):(\d+)` \| (.+) \|$', notes, re.M)]
    if not ranges or ranges[0][0] != 0 or ranges[-1][1] != len(code):
        raise ValueError('annotations do not cover canonical source')
    for idx, (start, end, _) in enumerate(ranges):
        if end <= start or (idx and start != ranges[idx - 1][1]):
            raise ValueError('annotation ranges overlap, have gaps, or are empty')
    lines = [
        '# Annotated compiler — generated, not source', '',
        f'Source SHA-256: `{digest}`',
        f'Filtered instruction SHA-256: `{filtered_digest}`', '',
        'Generated from `compiler/core.bf` and the hash-locked notes. This is for reading, not compiling.',
        'Every offset refers to the raw BF command stream. The compiler ignores this whole file.', ''
    ]
    for start, end, description in ranges:
        part = code[start:end].decode('ascii')
        lines += [
            f'## Instructions {start}–{end - 1}', '', description, '',
            f'{end - start} BF commands in this region.', '',
            'Start of region:', '', '```brainfuck', part[:160], '```', '',
            'End of region:', '', '```brainfuck', part[-160:], '```', ''
        ]
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if the derived view is stale')
    args = parser.parse_args()
    content = annotated_view()
    if args.check:
        if not VIEW.exists() or VIEW.read_text(encoding='utf-8') != content:
            raise SystemExit('derived annotated view is stale; run tools/annotate.py')
        print('Source purity, annotation ranges, SHA and generated view: PASS')
    else:
        VIEW.write_text(content, encoding='utf-8')
        print(f'Updated {VIEW.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

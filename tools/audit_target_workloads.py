#!/usr/bin/env python3
"""Offline, read-only compatibility audit for pinned third-party Brainfuck sources.

This does not compile, translate, or optimize Brainfuck. It checks source streams
against the current compiler's documented input limit, and is development-only.
Pass --root /path/to/clones (containing directories named like the four repos)
to verify actual files against the pinned GitHub audit.
"""
import argparse
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = b'><+-.,[]'


def scan(blob: bytes) -> dict:
    count = depth = maximum = 0
    first_unmatched_close = None
    for offset, b in enumerate(blob):
        if b not in COMMANDS:
            continue
        count += 1
        if b == 91:
            depth += 1
            maximum = max(maximum, depth)
        elif b == 93:
            depth -= 1
            if depth < 0 and first_unmatched_close is None:
                first_unmatched_close = offset
    return {
        'raw_bytes': len(blob), 'filtered_commands': count,
        'max_loop_depth': maximum,
        'brackets_balanced': depth == 0 and first_unmatched_close is None,
        'first_unmatched_close': first_unmatched_close,
    }


def audit(data: dict, clones: Path | None = None) -> dict:
    limit = data['command_capacity']
    result = {'classification': 'SOURCE COMPATIBILITY ONLY; NOT COMPILED', 'command_capacity': limit, 'repos': []}
    for repo in data['repositories']:
        name = repo['repo'].split('/')[-1]
        entry = {'repo': repo['repo'], 'source_commit': repo['source_commit'], 'files': []}
        for p in repo['programs']:
            info = dict(p)
            info['capacity_status'] = ('UNKNOWN' if p['filtered_commands'] is None else
                                       'EXCEEDS_LIMIT' if p['filtered_commands'] > limit else 'WITHIN_LIMIT')
            if clones is not None:
                path = (clones / name / p['path']).resolve()
                anchor = (clones / name).resolve()
                if not path.is_relative_to(anchor):
                    raise ValueError(f'unsafe source path: {path}')
                if not path.is_file():
                    info['local_audit'] = 'MISSING'
                else:
                    blob = path.read_bytes()
                    measured = scan(blob)
                    obj_sha = hashlib.sha1(b'blob ' + str(len(blob)).encode('ascii') + b'\0' + blob).hexdigest()
                    if p.get('git_blob_sha1') is not None and obj_sha != p['git_blob_sha1']:
                        raise ValueError(f'{path}: Git blob identity differs from audited revision')
                    expected = {k: p[k] for k in ('raw_bytes', 'filtered_commands', 'max_loop_depth')}
                    for k, v in expected.items():
                        if v is not None and measured[k] != v:
                            raise ValueError(f'{path}: {k} changed from audited revision: {v} -> {measured[k]}')
                    if not measured['brackets_balanced']:
                        raise ValueError(f'{path}: unmatched brackets')
                    info['local_audit'] = 'MATCHES_PINNED_COUNTS' if p['filtered_commands'] is not None else 'NEWLY_MEASURED'
                    info['observed'] = measured
                    info['capacity_status'] = ('EXCEEDS_LIMIT' if measured['filtered_commands'] > limit else 'WITHIN_LIMIT')
            entry['files'].append(info)
        result['repos'].append(entry)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, help='parent directory of local repository clones')
    ap.add_argument('--output', type=Path, help='optional audit JSON path')
    args = ap.parse_args()
    data = json.loads((ROOT/'status/TARGET_WORKLOADS.json').read_text())
    report = audit(data, args.root)
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered)


if __name__ == '__main__':
    main()

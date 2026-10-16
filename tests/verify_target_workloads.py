#!/usr/bin/env python3
"""Offline gate: preserve the pinned four-repo compatibility classification."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from audit_target_workloads import audit, scan

m = json.loads((ROOT/'status/TARGET_WORKLOADS.json').read_text())
assert m['command_capacity'] == 16128
assert len(m['repositories']) == 4
assert sum(len(x['programs']) for x in m['repositories']) == 12
r = audit(m)
assert len(r['repos']) == 4
all_programs = [p for x in r['repos'] for p in x['files']]
assert len([p for p in all_programs if p['capacity_status']=='EXCEEDS_LIMIT']) == 11
assert len([p for p in all_programs if p['capacity_status']=='UNKNOWN']) == 1
assert scan(b'ignored +++[->+<]') == dict(raw_bytes=17,filtered_commands=9,max_loop_depth=1,
                                      brackets_balanced=True,first_unmatched_close=None)
assert scan(b']ab') ['brackets_balanced'] is False
assert scan(b'[[') ['brackets_balanced'] is False
with tempfile.TemporaryDirectory() as folder:
    # Source parser is read-only, enforces relative paths, compares pinned byte/count evidence.
    p=Path(folder)/'TestRepo'/'src'/'test.bf'
    p.parent.mkdir(parents=True)
    p.write_bytes(b'++[--]')
    sample={'command_capacity':16128,'repositories':[{'repo':'any/TestRepo','source_commit':'fixture',
       'programs':[{'path':'src/test.bf','raw_bytes':6,'filtered_commands':6,'max_loop_depth':1}]}]}
    assert audit(sample,Path(folder))['repos'][0]['files'][0]['local_audit']=='MATCHES_PINNED_COUNTS'
    p.write_bytes(b'++[--]more+')
    try: audit(sample,Path(folder))
    except ValueError: pass
    else: raise AssertionError('changed source was not detected')
print('PASS 4 repositories, 12 tracked BF sources, 11 confirmed capacity failures, fixture mutations rejected')

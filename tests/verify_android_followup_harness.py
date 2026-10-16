#!/usr/bin/env python3
"""Check log completeness and paired timing statistics without a device."""
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks'))
from android_apk_followup import parse
from android_device_followup import interval


def main():
    names = ['legacy ordinary class', 'brainfuck ordinary class', 'legacy derived ad row',
             'brainfuck derived ad row', 'legacy scope', 'brainfuck scope',
             'cached verdict (the addView path)']
    log = '\n'.join('1791861000.000 100 100 I System.out: ' + name +
                    ' p50 1.00 p95 2.00 p99 3.00 us' for name in names)
    assert set(parse(log)) == set(names)
    assert parse(log)['brainfuck scope'] == {'p50_us': 1.0, 'p95_us': 2.0, 'p99_us': 3.0}
    for invalid in (log.replace('brainfuck scope', 'missing case'), '', log.replace(' p99 ', ' absent ')):
        try:
            parse(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('incomplete benchmark accepted')
    # Inverse timing ratio, with the fastest baseline selected on every resample.
    times = {'bf': [2] * 31, 'c': [1] * 31, 'rust': [4] * 31}
    assert interval(times, 'bf', ['c', 'rust'], random.Random(1)) == [0.5, 0.5]
    assert interval(times, 'c', ['bf', 'rust'], random.Random(1)) == [2.0, 2.0]
    print('PASS: complete/malformed APK logs and fastest-baseline timing ratios')


if __name__ == '__main__':
    main()

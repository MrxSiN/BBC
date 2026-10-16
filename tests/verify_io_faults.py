#!/usr/bin/env python3
"""Verify Linux syscall error handling in generated Brainfuck executables.

Injected read/write EINTR must retry and deliver exactly one byte.
Nonblocking EAGAIN still fails. SIGPIPE retains its Linux default. The fault
injector is test infrastructure, not part of the production BF compiler.
"""
import fcntl
import errno
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
from linux_syscall_inject import run_injected

COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'
EVIDENCE = ROOT / 'evidence/io_faults.json'


def compile_binary(source: bytes, directory: pathlib.Path) -> pathlib.Path:
    run = subprocess.run([str(COMPILER)], input=encode_source(source),
                         capture_output=True, check=True, timeout=25)
    executable = directory / (hashlib.sha256(source).hexdigest()[:12] + '.elf')
    executable.write_bytes(extract_artifact(run.stdout))
    executable.chmod(0o700)
    return executable


def close_descriptor(fd):
    def close_it():
        os.close(fd)
    return close_it


def main():
    if sys.platform != 'linux':
        raise SystemExit('Linux-only raw syscall fault characterization')
    if not COMPILER.exists():
        raise SystemExit('missing native compiler; run tests/verify_selfhost.py')
    observations = []
    with tempfile.TemporaryDirectory(prefix='bf-faults-') as temp:
        directory = pathlib.Path(temp)
        reader = compile_binary(b'+,.', directory)
        writer = compile_binary(b'+.', directory)
        baseline = subprocess.run([str(reader)], input=b'Z', capture_output=True, timeout=3)
        assert baseline.returncode == 0 and baseline.stdout == b'Z'
        observations.append({'case': 'ordinary_io', 'native_exit': 0,
                             'observed_output_hex': baseline.stdout.hex(),
                             'classification': 'normal I/O confirmed'})

        # read(0) returns -EBADF when fd 0 is closed. The cell is
        # cleared before the syscall, but the error must exit(4), not act as EOF.
        bad_input = subprocess.run([str(reader)], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   preexec_fn=close_descriptor(0), timeout=3)
        assert bad_input.returncode == 4 and bad_input.stdout == b'', ('closed_stdin', bad_input.returncode, bad_input.stdout)
        observations.append({'case': 'closed_stdin',
                             'native_exit': bad_input.returncode,
                             'observed_output_hex': bad_input.stdout.hex(),
                             'classification': 'PASS: read error exits(4), not EOF'})

        # write(1) on a closed fd returns -EBADF; the native program
        # must report failure with exit(3), never silently succeed.
        bad_output = subprocess.run([str(writer)], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    preexec_fn=close_descriptor(1), timeout=3)
        assert bad_output.returncode == 3 and bad_output.stdout == b'', ('closed_stdout', bad_output.returncode)
        observations.append({'case': 'closed_stdout',
                             'native_exit': bad_output.returncode,
                             'classification': 'PASS: failed write exits(3), not silent success'})

        # Nonblocking stdout full: write(1) returns -EAGAIN without output.
        pipe_r, pipe_w = os.pipe()
        try:
            os.set_blocking(pipe_w, False)
            filled = 0
            while True:
                try:
                    filled += os.write(pipe_w, b'X' * 4096)
                except BlockingIOError:
                    break
            saturated = subprocess.run([str(writer)], stdin=subprocess.DEVNULL,
                                       stdout=pipe_w, stderr=subprocess.PIPE, timeout=3)
        finally:
            os.close(pipe_w)
        received = bytearray()
        while True:
            chunk = os.read(pipe_r, 8192)
            if not chunk:
                break
            received.extend(chunk)
        os.close(pipe_r)
        unwritten = received == b'X' * filled
        assert saturated.returncode == 3 and unwritten, ('nonblocking_stdout_full', saturated.returncode, unwritten)
        observations.append({'case': 'nonblocking_stdout_full',
                             'native_exit': saturated.returncode,
                             'pipe_initial_bytes': filled,
                             'pipe_final_bytes': len(received),
                             'output_byte_unwritten': unwritten,
                             'classification': 'PASS: EAGAIN exits(3), reports unwritten output byte; no retry'})

        # A nonblocking empty stdin with a live writer yields -EAGAIN.
        pipe_r, pipe_w = os.pipe()
        try:
            os.set_blocking(pipe_r, False)
            would_block = subprocess.run([str(reader)], stdin=pipe_r,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, timeout=3)
        finally:
            os.close(pipe_r)
            os.close(pipe_w)
        assert would_block.returncode == 4 and would_block.stdout == b'', ('nonblocking_stdin_empty', would_block.returncode)
        observations.append({'case': 'nonblocking_stdin_empty',
                             'native_exit': would_block.returncode,
                             'observed_output_hex': would_block.stdout.hex(),
                             'classification': 'PASS: read EAGAIN exits(4), not EOF; no retry'})

        # Inject a single EINTR without executing the original write. A real
        # retry is required; treating EINTR as success cannot pass this test.
        code, payload, attempts = run_injected(writer, syscall_number=1, injected_errno=errno.EINTR)
        assert (code, payload, attempts) == (0, b"\x01", 2), (code, payload, attempts)
        observations.append({'case': 'injected_write_eintr', 'native_exit': code,
                             'syscall_attempts': attempts, 'observed_output_hex': payload.hex(),
                             'classification': 'PASS: interrupted write retried, exactly one byte delivered'})

        # EAGAIN still fails immediately; no spinning on a nonblocking pipe.
        code, payload, attempts = run_injected(writer, syscall_number=1, injected_errno=errno.EAGAIN)
        assert (code, payload, attempts) == (3, b'', 1), (code, payload, attempts)
        observations.append({'case': 'injected_write_eagain', 'native_exit': code,
                             'syscall_attempts': attempts, 'observed_output_hex': payload.hex(),
                             'classification': 'PASS: write EAGAIN remains exit(3)'})

        # EINTR is injected without consuming input. Native read must retry.
        code, payload, attempts = run_injected(reader, syscall_number=0, injected_errno=errno.EINTR, stdin=b'Z')
        assert (code, payload, attempts) == (0, b'Z', 2), (code, payload, attempts)
        observations.append({'case': 'injected_read_eintr', 'native_exit': code,
                             'syscall_attempts': attempts, 'observed_output_hex': payload.hex(),
                             'classification': 'PASS: interrupted read retried, exactly one byte consumed'})

        code, payload, attempts = run_injected(reader, syscall_number=0, injected_errno=errno.EINTR, stdin=b'')
        assert (code, payload, attempts) == (0, b'\x00', 2), (code, payload, attempts)
        observations.append({'case': 'injected_read_eintr_then_eof', 'native_exit': code,
                             'syscall_attempts': attempts, 'observed_output_hex': payload.hex(),
                             'classification': 'PASS: interrupted read retried; EOF still stores zero'})

        # The Linux kernel SIGPIPE path is tested separately from EAGAIN.
        pipe_r, pipe_w = os.pipe()
        os.close(pipe_r)
        try:
            broken = subprocess.run([str(writer)], stdin=subprocess.DEVNULL,
                                    stdout=pipe_w, stderr=subprocess.PIPE, timeout=3)
        finally:
            os.close(pipe_w)
        assert broken.returncode == -13, ('broken_pipe', broken.returncode)
        observations.append({'case': 'broken_pipe',
                             'native_exit': broken.returncode,
                             'classification': 'PASS: kernel default SIGPIPE on Linux; process terminates via signal'})

    defects = [o['case'] for o in observations if o['classification'].startswith('DEFECT:')]
    report = {
        'date': '2026-10-12',
        'scope': 'Direct Linux syscall failure paths in native BF executables',
        'compiler_source_sha256': hashlib.sha256((ROOT / 'compiler/core.bf').read_bytes()).hexdigest(),
        'native_compiler_sha256': hashlib.sha256(COMPILER.read_bytes()).hexdigest(),
        'classification': 'EXECUTED: ten Linux I/O cases; both read and write retry EINTR; both EAGAIN cases fail fast; not a general asynchronous I/O guarantee.',
        'cases_executed': len(observations),
        'known_defect_cases': defects,
        'observations': observations,
    }
    EVIDENCE.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(observations)} Linux I/O fault assertions; {len(defects)} silent-failure defects')
    for item in observations:
        print(f"  {item['case']}: return {item['native_exit']}; {item['classification']}")


if __name__ == '__main__':
    main()

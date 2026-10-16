#!/usr/bin/env python3
"""Run the BF-owned AArch64 DSO compiler on a host that cannot execute Linux x86-64.

Every compiler stage of the iteration-59 pipeline is a standard-Brainfuck program
(``experiments/<name>.bf``). The pinned x86-64 Linux builds of those stages cannot
run on Windows, so this transport compiles the same BF sources on an AArch64
Android device with the self-hosted native BF compiler (``run_android_native``)
and executes each stage there through ``adb shell -T`` with binary-clean pipes.

Python here only moves bytes: it redirects stage process launches, it does not
generate code. Output is the same ``bfc_call_v1`` DSO as ``android_dynamic_callable59``.

    python -m bootstrap.android_device_stages --serial SERIAL policy.bf -o policy.so

``--annotated`` drops whole-line ``#`` comments first (YouTubeHideAds annotated
source: a line whose first non-blank character is ``#`` is documentation, even
when it contains command characters).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from .run_android_native import NativeAndroidCompiler, REMOTE

ROOT = Path(__file__).resolve().parents[1]
ADB = r'D:\Android\platform-tools\adb.exe'
STAGE_DIR = REMOTE + '/stages'
SUFFIX = '_x86_64_linux'


def stage_source(executable: Path) -> Path | None:
    """The BF source of a pinned stage executable, or None for anything else."""
    if executable.suffix != '.elf' or ROOT not in executable.resolve().parents:
        return None
    source = ROOT / 'experiments' / (executable.stem.removesuffix(SUFFIX) + '.bf')
    return source if source.is_file() else None


def strip_annotations(source: bytes) -> bytes:
    return b''.join(line for line in source.splitlines(keepends=True) if not line.lstrip().startswith(b'#'))


class DeviceStages:
    """Compile each stage once per source digest on the device; launch it there."""

    def __init__(self, serial: str, work: Path, adb: str = ADB):
        self.adb = [adb, '-s', serial]
        self.compiler = NativeAndroidCompiler(serial, work, adb)
        self.compiler.shell('mkdir -p ' + STAGE_DIR)
        self.ready: dict[Path, str] = {}

    def remote(self, executable: Path) -> str | None:
        source = stage_source(Path(executable))
        if source is None:
            return None
        if source not in self.ready:
            data = source.read_bytes()
            name = f'{STAGE_DIR}/{source.stem}-{hashlib.sha256(data).hexdigest()[:16]}'
            present = subprocess.run(self.adb + ['shell', '-T', f'test -x {name} && echo ok'], capture_output=True)
            if present.stdout.strip() != b'ok':
                image = self.compiler.compile(data)
                local = self.compiler.work / (source.stem + '.elf')
                local.write_bytes(image)
                self.compiler.run(self.adb + ['push', str(local), name])
                self.compiler.shell(f'chmod 700 {name}')
            self.ready[source] = name
        return self.ready[source]

    def command(self, args):
        """The device path of the BF build behind ``[stage.elf]``, or None for any other command."""
        if isinstance(args, (list, tuple)) and len(args) == 1:
            return self.remote(Path(args[0]))
        return None


class SocketProcess:
    """A ``Popen`` look-alike whose child runs on the device behind a TCP socket.

    Windows ``adb shell`` rewrites LF/CRLF in both directions, so stage bytes travel
    through ``adb forward`` to toybox ``nc -l`` instead, which is byte-exact.
    """

    _port = 47100

    def __init__(self, stages: 'DeviceStages', remote: str, stdin=None, stdout=None, stderr=None, **_):
        import socket, threading, time
        SocketProcess._port += 1
        port = SocketProcess._port
        status = f'{STAGE_DIR}/status-{port}'
        adb = stages.adb
        subprocess.run(adb + ['forward', f'tcp:{port}', f'tcp:{port}'], check=True, capture_output=True)
        launch = f"rm -f {status}; nc -l -s 127.0.0.1 -p {port} sh -c '{remote}; echo $? > {status}'"
        self._server = _POPEN(adb + ['shell', '-T', launch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # adb forward accepts locally even when nothing listens yet; wait for the LISTEN socket.
        listening = f':{port:04X} 00000000:0000 0A'
        for _ in range(200):
            table = _RUN(adb + ['shell', '-T', 'cat /proc/net/tcp /proc/net/tcp6'], capture_output=True).stdout.decode()
            if listening in table:
                break
            time.sleep(0.05)
        else:
            raise RuntimeError('device stage listener did not start')
        for _ in range(100):
            try:
                self._socket = socket.create_connection(('127.0.0.1', port), timeout=2)
                break
            except OSError:
                time.sleep(0.05)
        else:
            raise RuntimeError('device stage socket did not open')
        self._socket.settimeout(None)
        self._adb, self._port_number, self._status = adb, port, status
        self.args, self.returncode, self.stderr = [remote], None, None
        self.stdin = self._socket.makefile('wb', buffering=0) if stdin is subprocess.PIPE else None
        self.stdout = self._socket.makefile('rb', buffering=0) if stdout is subprocess.PIPE else None
        self._pumps = []
        if stdin not in (None, subprocess.PIPE, subprocess.DEVNULL):
            def feed(source=stdin):
                # No half-close: adb forward tears down both directions on it. Every
                # stage protocol ends with an in-band terminator frame instead.
                while block := source.read(1 << 16):
                    self._socket.sendall(block)
            self._pumps.append(threading.Thread(target=feed, daemon=True))
        if stdout not in (None, subprocess.PIPE, subprocess.DEVNULL):
            def drain(target=stdout):
                while block := self._socket.recv(1 << 16):
                    target.write(block)
            self._pumps.append(threading.Thread(target=drain, daemon=True))
        for pump in self._pumps:
            pump.start()
        if stderr is subprocess.PIPE:
            import io
            self.stderr = io.BytesIO()

    def close_stdin(self):
        pass  # see feed(): EOF is in-band

    def wait(self, timeout=None):
        if self.returncode is None:
            for pump in self._pumps:
                pump.join(timeout)
            if self.stdin is not None:
                self.close_stdin()
            if self.stdout is None:
                while self._socket.recv(1 << 16):
                    pass
            self._server.wait(timeout)
            self._socket.close()
            code = _RUN(self._adb + ['shell', '-T', f'cat {self._status}'], capture_output=True).stdout.strip()
            self.returncode = int(code) if code.isdigit() else 255
            _RUN(self._adb + ['forward', '--remove', f'tcp:{self._port_number}'], capture_output=True)
        return self.returncode

    def poll(self):
        return self.returncode

    def communicate(self, input=None, timeout=None):
        data = b''
        if input:
            self.stdin.write(input)
        if self.stdin is not None:
            self.close_stdin()
        if self.stdout is not None:
            chunks = []
            while block := self.stdout.read(1 << 16):
                chunks.append(block)
            data = b''.join(chunks)
        self.wait(timeout)
        return data, b''

    def kill(self):
        self._socket.close()
        self._server.kill()

    terminate = kill

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.wait()


_POPEN, _RUN = subprocess.Popen, subprocess.run


def install(stages: DeviceStages) -> None:
    """Route every pinned-stage launch in this process to the device."""

    class Popen(_POPEN):
        def __new__(cls, args, *rest, **options):
            remote = stages.command(args)
            if remote is None:
                return _POPEN(args, *rest, **options)
            return SocketProcess(stages, remote, **options)

    def routed_run(args, *rest, input=None, capture_output=False, check=False, timeout=None, **options):
        remote = stages.command(args)
        if remote is None:
            return _RUN(args, *rest, input=input, capture_output=capture_output, check=check, timeout=timeout, **options)
        # Batch stages: adb push/pull are byte-exact and give the stage a real EOF.
        work = stages.compiler.work
        local_in, local_out = work / 'stage.in', work / 'stage.out'
        source = options.get('stdin')
        if input is not None:
            local_in.write_bytes(input)
        elif source not in (None, subprocess.DEVNULL, subprocess.PIPE):
            source.seek(0) if source.seekable() and source.tell() else None
            local_in.write_bytes(source.read())
        else:
            local_in.write_bytes(b'')
        stages.compiler.run(stages.adb + ['push', str(local_in), STAGE_DIR + '/in'])
        code = _RUN(stages.adb + ['shell', '-T', f'{remote} < {STAGE_DIR}/in > {STAGE_DIR}/out; echo $?'],
                    capture_output=True).stdout.strip()
        stages.compiler.run(stages.adb + ['pull', STAGE_DIR + '/out', str(local_out)])
        out = local_out.read_bytes()
        target = options.get('stdout')
        if target not in (None, subprocess.PIPE, subprocess.DEVNULL) and not capture_output:
            target.write(out)
            out = None
        elif not capture_output and target is not subprocess.PIPE:
            out = None
        result = subprocess.CompletedProcess([remote], int(code) if code.isdigit() else 255, out, b'')
        if check and result.returncode:
            raise subprocess.CalledProcessError(result.returncode, [remote], result.stdout, b'')
        return result

    subprocess.Popen, subprocess.run = Popen, routed_run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--adb', default=ADB)
    parser.add_argument('--annotated', action='store_true')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.bfc-device-', dir=args.output.parent) as folder:
        work = Path(folder)
        source = args.source
        if args.annotated:
            source = work / 'source.bf'
            source.write_bytes(strip_annotations(args.source.read_bytes()))
        install(DeviceStages(args.serial, work, args.adb))
        from .android_dynamic_callable59 import compile_shared
        record = compile_shared(source, args.output, timeout=900)
    record['stage_host'] = 'android-aarch64-device-via-adb'
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

"""Linux/x86-64 syscall-result fault injection for generated ELF tests only.

PTRACE_SYSCALL changes one target syscall into getpid, then replaces its return
value with -errno. The kernel never performs the target operation on that
attempt. A retry has to execute the actual syscall and produce its real effect.
No compiled executable is patched. This is not production compiler logic.
"""
import ctypes
import errno
import os
import platform
import signal

PTRACE_TRACEME = 0
PTRACE_GETREGS = 12
PTRACE_SETREGS = 13
PTRACE_SYSCALL = 24
PTRACE_SETOPTIONS = 0x4200
PTRACE_O_TRACESYSGOOD = 1
SYSCALL_STOP = signal.SIGTRAP | 0x80
SYS_GETPID = 39


class Registers(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in (
        'r15 r14 r13 r12 rbp rbx r11 r10 r9 r8 rax rcx rdx rsi rdi '
        'orig_rax rip cs eflags rsp ss fs_base gs_base ds es fs gs').split()]


_LIBC = ctypes.CDLL(None, use_errno=True)
_LIBC.ptrace.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]
_LIBC.ptrace.restype = ctypes.c_long


def ptrace(operation, pid, data=0):
    value = ctypes.c_void_p(data) if isinstance(data, int) else data
    result = _LIBC.ptrace(operation, pid, None, value)
    if result == -1:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))
    return result


def run_injected(binary, *, syscall_number, injected_errno, stdin=b''):
    """Return (exit_code, stdout, target_syscall_attempts) after one injected error."""
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('ptrace syscall testing needs Linux x86-64')
    if syscall_number not in (0, 1) or injected_errno not in (errno.EINTR, errno.EAGAIN):
        raise ValueError('unexpected fault injection request')
    input_r, input_w = os.pipe()
    output_r, output_w = os.pipe()
    os.write(input_w, stdin)
    os.close(input_w)
    pid = os.fork()
    if pid == 0:
        try:
            os.close(output_r)
            os.dup2(input_r, 0)
            os.dup2(output_w, 1)
            os.close(input_r)
            os.close(output_w)
            ptrace(PTRACE_TRACEME, 0)
            os.kill(os.getpid(), signal.SIGSTOP)
            os.execv(str(binary), [str(binary)])
        finally:
            os._exit(127)
    os.close(input_r)
    os.close(output_w)
    injected = False
    pending = False
    on_entry = True
    delivery = 0
    attempts = 0
    try:
        _, status = os.waitpid(pid, 0)
        if not os.WIFSTOPPED(status) or os.WSTOPSIG(status) != signal.SIGSTOP:
            raise RuntimeError('traced process did not stop before exec')
        ptrace(PTRACE_SETOPTIONS, pid, PTRACE_O_TRACESYSGOOD)
        for _ in range(100):
            ptrace(PTRACE_SYSCALL, pid, delivery)
            delivery = 0
            _, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break
            if not os.WIFSTOPPED(status):
                raise RuntimeError('unexpected ptrace child state')
            stopped = os.WSTOPSIG(status)
            if stopped != SYSCALL_STOP:
                # The first exec trap is SIGTRAP and must not be delivered.
                delivery = 0 if stopped == signal.SIGTRAP else stopped
                continue
            regs = Registers()
            ptrace(PTRACE_GETREGS, pid, ctypes.byref(regs))
            if on_entry:
                if regs.orig_rax == syscall_number:
                    attempts += 1
                    if not injected:
                        regs.orig_rax = SYS_GETPID
                        ptrace(PTRACE_SETREGS, pid, ctypes.byref(regs))
                        pending = True
            elif pending:
                regs.rax = (-injected_errno) & 0xffffffffffffffff
                ptrace(PTRACE_SETREGS, pid, ctypes.byref(regs))
                injected = True
                pending = False
            on_entry = not on_entry
        else:
            raise RuntimeError('traced program did not terminate within 100 stops')
        if not injected or pending:
            raise RuntimeError('target syscall was not injected')
        exit_code = os.waitstatus_to_exitcode(status)
        output = bytearray()
        while True:
            chunk = os.read(output_r, 4096)
            if not chunk:
                break
            output.extend(chunk)
        return exit_code, bytes(output), attempts
    except BaseException:
        try:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        except ProcessLookupError:
            pass
        raise
    finally:
        os.close(output_r)

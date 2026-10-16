/* Strong C baseline: no libc/startup, same byte/EOF/error contract as BF.
 * Syscall register binding is target ABI glue, not Brainfuck compilation.
 */
#include <stdint.h>

static inline long syscall3(long number, long a, long b, long c) {
    register long x0 __asm__("x0") = a;
    register long x1 __asm__("x1") = b;
    register long x2 __asm__("x2") = c;
    register long x8 __asm__("x8") = number;
    __asm__ volatile("svc 0" : "+r"(x0) : "r"(x1), "r"(x2), "r"(x8) : "memory", "cc");
    return x0;
}

__attribute__((noreturn)) void _start(void) {
    uint8_t source = 0, result = 0;
    long size = syscall3(63, 0, (long)&source, 1);
    long status = 0;
    if (size != 0 && size != 1) status = 4;
    else {
#ifdef DIRECT_ECHO
        uint8_t *output = &source;
#else
        while (source) { result++; source--; }
        uint8_t *output = &result;
#endif
        if (syscall3(64, 1, (long)output, 1) != 1) status = 3;
    }
    syscall3(93, status, 0, 0);
    __builtin_unreachable();
}

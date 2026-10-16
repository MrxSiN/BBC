/* Independent optimized C baseline for the BF comma loop byte contract. */
#include <stdint.h>
static inline long call(long number, long a, long b, long c) {
    register long x0 __asm__("x0") = a, x1 __asm__("x1") = b;
    register long x2 __asm__("x2") = c, x8 __asm__("x8") = number;
    __asm__ volatile("svc 0" : "+r"(x0) : "r"(x1), "r"(x2), "r"(x8) : "memory", "cc");
    return x0;
}
__attribute__((noreturn)) void _start(void) {
    uint8_t byte = 0;
    long status = 0, size;
    for (;;) {
        do { size = call(63, 0, (long)&byte, 1); } while (size == -4);
        if (size != 0 && size != 1) { status = 4; break; }
        if (size == 0 || byte == 0) break;
        do { size = call(64, 1, (long)&byte, 1); } while (size == -4);
        if (size != 1) { status = 3; break; }
    }
    call(93, status, 0, 0);
    __builtin_unreachable();
}

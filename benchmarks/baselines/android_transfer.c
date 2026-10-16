/* Same wrapping-byte transfer as examples/android_loop_demo.bf. */
#include <stdint.h>
#include <unistd.h>

int main(void) {
    uint8_t source = 0, result = 0;
    ssize_t size = read(0, &source, 1);
    if (size < 0) return 4;
    while (source) { result++; source--; }
    return write(1, &result, 1) == 1 ? 0 : 3;
}

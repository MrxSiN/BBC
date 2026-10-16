#include <stdint.h>
#include <stdio.h>
#ifndef INNER_A
#define INNER_A 15
#endif
#ifndef INNER_B
#define INNER_B 17
#endif
int main(void) {
    int input = getchar();
    uint8_t outer = (input == EOF ? 0 : (uint8_t)input);
    uint8_t middle = 0, inner = 0, result = 0;
    while (outer != 0) {
        middle = (uint8_t)(middle + INNER_A);
        while (middle != 0) {
            inner = (uint8_t)(inner + INNER_B);
            while (inner != 0) {
                result = (uint8_t)(result + 1);
                inner = (uint8_t)(inner - 1);
            }
            middle = (uint8_t)(middle - 1);
        }
        outer = (uint8_t)(outer - 1);
    }
    return putchar(result) == EOF ? 1 : 0;
}

/* TEST ONLY host x86 policy substitutes for the ART/JNI assertion harness.
 * This fixture must never be distributed as a Brainfuck-compiled policy.
 */
#include <stdint.h>
#include <stddef.h>
#ifndef CASE_ID
#error CASE_ID must be specified by the host test harness
#endif

uint64_t bfc_call_v1(const uint8_t *input, uint64_t input_len,
                     uint8_t *out, uint64_t out_cap, uint8_t *tape,
                     uint64_t tape_len, uint64_t gas, uint64_t *used) {
    (void)gas; (void)input; (void)input_len; (void)out; (void)out_cap; (void)tape;
    *used = 0;
    if (!tape_len) return 3;
#if CASE_ID == 0
    (void)input; (void)input_len; (void)out; (void)out_cap; (void)tape;
    return 0;
#elif CASE_ID == 1
    for (uint64_t i = 0; i < 3; ++i) {
        if (*used >= out_cap) return 2;
        out[(*used)++] = i < input_len ? input[i] : 0;
    }
    return 0;
#elif CASE_ID == 2
    tape[1] = (uint8_t)(tape[1] + 1);
    if (out_cap == 0) return 2;
    out[(*used)++] = tape[1]; return 0;
#elif CASE_ID == 3
    tape[2] = 6;
    if (out_cap == 0) return 2;
    out[(*used)++] = tape[2]; return 0;
#elif CASE_ID == 4
    return 3;
#elif CASE_ID == 5
    ++tape[0];
    return 2;
#elif CASE_ID == 6
    tape[0] = 3;
    return 1;
#elif CASE_ID == 7
    return 0;
#elif CASE_ID == 8
    ++tape[0];
    if (out_cap == 0) return 2;
    out[(*used)++] = tape[0]; return 0;
#else
#error unknown host test case
#endif
}

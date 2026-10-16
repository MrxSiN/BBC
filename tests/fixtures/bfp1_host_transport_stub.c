/* TEST ONLY: native host transport probe, not a Brainfuck compiler or BF policy. */
#include <stdint.h>
uint64_t bfc_call_v1(const uint8_t *input,uint64_t input_len,
                     uint8_t *output,uint64_t capacity,uint8_t *tape,
                     uint64_t tape_count,uint64_t gas,uint64_t *used) {
    (void)gas;
    if (!tape_count || !used) return 3;
    tape[0]=(uint8_t)(tape[0]+1);
    uint64_t count=input_len<capacity ? input_len : capacity;
    for (uint64_t i=0;i<count;i++) output[i]=input[i];
    *used=count;
    return input_len>capacity ? 2 : 0;
}

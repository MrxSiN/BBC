/* Existing GM policy core, measured in process with its original bounded ABI. */
#define _POSIX_C_SOURCE 200809L
#include "bf_engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static uint64_t now(void) {
    struct timespec stamp;
    if (clock_gettime(CLOCK_MONOTONIC, &stamp)) exit(1);
    return (uint64_t)stamp.tv_sec * 1000000000 + stamp.tv_nsec;
}

int main(int argc, char **argv) {
    if (argc != 3) return 64;
    char *end;
    long program = strtol(argv[1], &end, 10);
    if (end == argv[1] || *end || program < 0 || program >= bf_program_count) return 64;
    FILE *file = fopen(argv[2], "rb");
    if (!file) return 66;
    uint8_t input[BF_IN_CAP], output[BF_OUT_CAP];
    size_t input_size = fread(input, 1, sizeof(input), file);
    if (ferror(file) || fgetc(file) != EOF || fclose(file)) return 74;
    size_t length = 0;
    uint32_t ticks;
    unsigned checksum = 0;
    for (unsigned i = 0; i < 20000; i++) {
        if (bf_run((int)program, input, input_size, output, sizeof(output), &length, &ticks)) return 65;
        __asm__ volatile("" ::: "memory");
    }
    uint64_t start = now();
    for (unsigned i = 0; i < 20000; i++) {
        if (bf_run((int)program, input, input_size, output, sizeof(output), &length, &ticks)) return 65;
        for (size_t j = 0; j < length; j++) checksum += output[j];
        __asm__ volatile("" ::: "memory");
    }
    uint64_t elapsed = now() - start;
    printf("{\"ns_per_call\":%.3f,\"checksum\":%u,\"output_hex\":\"", elapsed / 20000.0, checksum);
    for (size_t j = 0; j < length; j++) printf("%02x", output[j]);
    printf("\",\"ticks\":%u}\n", ticks);
    return 0;
}

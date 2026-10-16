/* Test/benchmark loader and original GM baseline; contains no BF compiler logic. */
#define _POSIX_C_SOURCE 200809L
#include "bf_engine.h"
#include <elf.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

typedef struct { uint64_t status, ticks; } result;
typedef result (*native_fn)(const uint8_t *, size_t, uint8_t *, size_t,
                            uint8_t *, size_t, uint64_t, size_t *);
static native_fn compiled;
static size_t needed;
static int program;

static uint64_t now(void) {
    struct timespec stamp;
    if (clock_gettime(CLOCK_MONOTONIC, &stamp)) exit(1);
    return (uint64_t)stamp.tv_sec*1000000000+stamp.tv_nsec;
}

static void load(const char *path) {
    int fd = open(path, O_RDONLY);
    struct stat info;
    if (fd < 0 || fstat(fd, &info) || info.st_size < 196 || info.st_size > 262144) exit(66);
    void *image = mmap(NULL, (size_t)info.st_size, PROT_READ|PROT_EXEC, MAP_PRIVATE, fd, 0);
    close(fd);
    if (image == MAP_FAILED) { perror("mmap"); exit(71); }
    const Elf64_Ehdr *e = image;
    const Elf64_Phdr *p = (const Elf64_Phdr *)((const uint8_t *)image+64);
    const uint8_t *tag = (const uint8_t *)image+120;
    if (memcmp(e->e_ident, "\177ELF\2\1\1", 7) || e->e_type != ET_DYN || e->e_machine != EM_AARCH64 ||
        e->e_entry != 128 || e->e_phoff != 64 || e->e_phnum != 1 || e->e_phentsize != 56 ||
        p->p_type != PT_LOAD || p->p_flags != (PF_R|PF_X) || p->p_offset || p->p_vaddr ||
        p->p_filesz != (uint64_t)info.st_size || p->p_memsz != p->p_filesz ||
        memcmp(tag, "BFP1", 4) || tag[6] > 1) exit(65);
    needed = tag[6] ? tag[4]+256u*tag[5] : 65536u;
    if (!needed || needed > 65536u) exit(65);
    compiled = (native_fn)((const uint8_t *)image+128);
}

static int native_run(const uint8_t *in, size_t length, uint8_t *out, size_t cap,
                      size_t *out_len, uint32_t *ticks) {
    uint8_t tape[65536];
    memset(tape, 0, needed);
    uint64_t budget = BF_BUDGET_BASE+(uint64_t)length*BF_BUDGET_PER_BYTE;
    result r = compiled(in, length, out, cap, tape, needed, budget, out_len);
    *ticks = (uint32_t)r.ticks;
    if (r.status) *out_len = 0;
    return (int)r.status;
}

static int reference_run(const uint8_t *in, size_t length, uint8_t *out, size_t cap,
                         size_t *out_len, uint32_t *ticks) {
    return bf_run(program, in, length, out, cap, out_len, ticks);
}

int main(int argc, char **argv) {
    if (argc != 5) return 64;
    char *end;
    long parsed = strtol(argv[1], &end, 10);
    if (end == argv[1] || *end || parsed < 0 || parsed >= bf_program_count) return 64;
    program = (int)parsed; load(argv[2]);
    FILE *file = fopen(argv[3], "rb");
    if (!file) return 66;
    uint8_t *input = malloc(BF_IN_CAP), actual[BF_OUT_CAP], expected[BF_OUT_CAP];
    if (!input) return 71;
    size_t length = fread(input, 1, BF_IN_CAP, file);
    if (ferror(file) || fgetc(file) != EOF || fclose(file)) return 74;
    size_t a_len, e_len;
    uint32_t a_ticks, e_ticks;
    int a_status = native_run(input, length, actual, sizeof(actual), &a_len, &a_ticks);
    int e_status = reference_run(input, length, expected, sizeof(expected), &e_len, &e_ticks);
    if (a_status != e_status || a_len != e_len || memcmp(actual, expected, a_len)) {
        fprintf(stderr,"mismatch native=%d,%zu,%u reference=%d,%zu,%u\n",
                a_status,a_len,a_ticks,e_status,e_len,e_ticks); return 65;
    }
    if (!strcmp(argv[4], "check")) {
        printf("{\"status\":%d,\"output_hex\":\"", a_status);
        for (size_t i=0;i<a_len;i++) printf("%02x", actual[i]);
        printf("\",\"native_ticks\":%u,\"reference_ticks\":%u,\"tape_bytes\":%zu}\n", a_ticks,e_ticks,needed);
        return 0;
    }
    if (!strcmp(argv[4], "fuzz")) {
        uint32_t state = 20261014;
        for (unsigned i = 0; i < 4096; i++) {
            length = i % 256;
            for (size_t j = 0; j < length; j++) {
                state ^= state << 13; state ^= state >> 17; state ^= state << 5;
                input[j] = (uint8_t)state;
            }
            if ((i & 1) && length >= 8) { input[0] = 1; input[2] = program ? 32 : 16; }
            a_status = native_run(input,length,actual,sizeof(actual),&a_len,&a_ticks);
            e_status = reference_run(input,length,expected,sizeof(expected),&e_len,&e_ticks);
            if (a_status != e_status || a_len != e_len || memcmp(actual,expected,a_len)) {
                fprintf(stderr,"fuzz mismatch case=%u native=%d,%zu reference=%d,%zu\n",
                        i,a_status,a_len,e_status,e_len); return 65;
            }
        }
        printf("{\"random_frame_checks\":4096}\n"); free(input); return 0;
    }
    int (*run)(const uint8_t *,size_t,uint8_t *,size_t,size_t *,uint32_t *) =
        !strcmp(argv[4],"bf") ? native_run : !strcmp(argv[4],"c") ? reference_run : NULL;
    if (!run) return 64;
    unsigned checksum = 0;
    for (unsigned i=0;i<20000;i++) {
        if (run(input,length,actual,sizeof(actual),&a_len,&a_ticks)) return 65;
        __asm__ volatile("" ::: "memory");
    }
    uint64_t start = now();
    for (unsigned i=0;i<20000;i++) {
        if (run(input,length,actual,sizeof(actual),&a_len,&a_ticks)) return 65;
        for (size_t j=0;j<a_len;j++) checksum += actual[j];
        __asm__ volatile("" ::: "memory");
    }
    printf("{\"variant\":\"%s\",\"ns_per_call\":%.3f,\"checksum\":%u}\n",
           argv[4],(now()-start)/20000.0,checksum);
    free(input);
    return 0;
}

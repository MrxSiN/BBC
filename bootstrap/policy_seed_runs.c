/* Development-only BF interpreter with run-length dispatch.
 * It NEVER translates Brainfuck into machine code; code generation and
 * optimisation decisions belong to the BF programs being interpreted.
 * Boundaries and 8-bit arithmetic agree with the canonical seed executor.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { unsigned char opcode, affine; uint32_t count; size_t jump; } Op;
static int valid(int c) {
    return c == '<' || c == '>' || c == '+' || c == '-' ||
           c == '.' || c == ',' || c == '[' || c == ']';
}
static int fail(const char *msg, int status) { fprintf(stderr, "%s\n", msg); return status; }
int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) return fail("usage: policy_seed_runs source.bf [steps]", 64);
    uint64_t cap_steps = argc == 3 ? strtoull(argv[2], NULL, 10) : UINT64_C(2000000000);
    FILE *f = fopen(argv[1], "rb");
    if (!f) return fail("source file unavailable", 66);
    size_t allocated = 16384, n = 0, depth = 0;
    Op *ops = malloc(allocated * sizeof *ops);
    size_t *stack = malloc(allocated * sizeof *stack);
    if (!ops || !stack) return fail("out of memory", 71);
    for (int ch; (ch = fgetc(f)) != EOF;) {
        if (!valid(ch)) continue;
        if (n && (ch == '<' || ch == '>' || ch == '+' || ch == '-') &&
            ops[n-1].opcode == ch && ops[n-1].count < UINT32_MAX) {
            ++ops[n-1].count;
            continue;
        }
        if (n == allocated) {
            if (allocated > SIZE_MAX / 2 / sizeof *ops) return fail("oversized source", 71);
            allocated *= 2;
            Op *more = realloc(ops, allocated * sizeof *ops);
            if (!more) return fail("out of memory", 71);
            ops = more;
            size_t *st = realloc(stack, allocated * sizeof *stack);
            if (!st) return fail("out of memory", 71);
            stack = st;
        }
        ops[n] = (Op){(unsigned char)ch, 0, 1, 0};
        if (ch == '[') stack[depth++] = n;
        if (ch == ']') {
            if (!depth) return fail("unmatched closing bracket", 65);
            size_t open = stack[--depth];
            ops[open].jump = n;
            ops[n].jump = open;
            /* Recognize a BF linear loop, not a new source operator. A fast
             * loop must return to the same pointer and decrement/increment
             * the source once. Only ordinary operations appear in its body.
             */
            int64_t relative = 0;
            unsigned source_delta = 0;
            int fold = 1;
            for (size_t j = open + 1; j < n; ++j) {
                switch (ops[j].opcode) {
                case '>': relative += ops[j].count; break;
                case '<': relative -= ops[j].count; break;
                case '+': if (!relative) source_delta =
                                (source_delta + ops[j].count) & 255; break;
                case '-': if (!relative) source_delta =
                                (source_delta - ops[j].count) & 255; break;
                default: fold = 0; break;
                }
                if (!fold || relative > 65535 || relative < -65535) {
                    fold = 0; break;
                }
            }
            if (fold && !relative && (source_delta == 255 || source_delta == 1))
                ops[open].affine = source_delta == 255 ? 1 : 2;
        }
        n++;
    }
    if (ferror(f) || fclose(f)) return fail("source read error", 74);
    if (depth) return fail("unmatched opening bracket", 65);
    unsigned char *tape = calloc(65536, 1);
    if (!tape) return fail("out of memory", 71);
    size_t ptr = 0;
    uint64_t steps = 0;
    static char output_buffer[65536];
    setvbuf(stdout, output_buffer, _IOFBF, sizeof output_buffer);
    for (size_t pc = 0; pc < n; pc++) {
        const Op r = ops[pc];
        if (steps > cap_steps || r.count > cap_steps - steps) return fail("step limit reached", 124);
        steps += r.count;
        switch (r.opcode) {
        case '>':
            if (r.count > 65535 - ptr) return fail("pointer overflow", 2);
            ptr += r.count; break;
        case '<':
            if (r.count > ptr) return fail("pointer underflow", 2);
            ptr -= r.count; break;
        case '+': tape[ptr] = (uint8_t)(tape[ptr] + r.count); break;
        case '-': tape[ptr] = (uint8_t)(tape[ptr] - r.count); break;
        case '.': if (putchar(tape[ptr]) == EOF) return 74; break;
        case ',': { int c = getchar(); tape[ptr] = c == EOF ? 0 : (uint8_t)c; break; }
        case '[':
            if (!tape[ptr]) { pc = r.jump; break; }
            if (r.affine) {
                unsigned times = r.affine == 1 ? tape[ptr] : (256 - tape[ptr]);
                uint64_t body_steps = 1; /* the closing bracket */
                int64_t relative = 0;
                /* Check address bounds without changing any tape cells. */
                for (size_t j = pc + 1; j < r.jump; ++j) {
                    const Op body = ops[j];
                    body_steps += body.count;
                    if (body.opcode == '>') relative += body.count;
                    if (body.opcode == '<') relative -= body.count;
                    if (relative < 0 && (uint64_t)(-relative) > ptr)
                        return fail("pointer underflow", 2);
                    if (relative > 0 && (uint64_t)relative > 65535 - ptr)
                        return fail("pointer overflow", 2);
                }
                if (times && (body_steps > (cap_steps - steps) / times))
                    return fail("step limit reached", 124);
                steps += body_steps * times;
                relative = 0;
                for (size_t j = pc + 1; j < r.jump; ++j) {
                    const Op body = ops[j];
                    if (body.opcode == '>') relative += body.count;
                    else if (body.opcode == '<') relative -= body.count;
                    else if (body.opcode == '+') {
                        size_t at = (size_t)((int64_t)ptr + relative);
                        tape[at] = (uint8_t)(tape[at] + body.count * times);
                    } else if (body.opcode == '-') {
                        size_t at = (size_t)((int64_t)ptr + relative);
                        tape[at] = (uint8_t)(tape[at] - body.count * times);
                    }
                }
                pc = r.jump;
            }
            break;
        case ']': if (tape[ptr]) pc = r.jump; break;
        }
    }
    if (fflush(stdout) == EOF) return 74;
    fprintf(stderr, "STEPS=%llu\n", (unsigned long long)steps);
    free(ops); free(stack); free(tape);
    return 0;
}

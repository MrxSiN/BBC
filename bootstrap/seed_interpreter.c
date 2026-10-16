/* Independent BF seed executor. Development/bootstrap tool, never a compiler.
 * Implements only eight Brainfuck operations, fixed 64-KiB 8-bit tape,
 * zero on stdin EOF and checked pointer movement.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

/* Diagnostic instrumentation is absent from the released seed executable.
 * The optional audit build still executes BF; it never generates native code.
 * Source bytes supplied as hex are a read-only test oracle, not compiler input.
 */
static int isbf(int c);

#ifdef BF_TAPE_AUDIT
#ifndef BF_DECODE_END
#error "The source-region offset must be supplied by the audit harness"
#endif
#ifndef BF_COMPILE_END
#error "The last compiler source-region offset must be supplied by the audit harness"
#endif
#define BF_SOURCE_BASE 68
#define BF_SOURCE_STRIDE 4
#define BF_MAX_SOURCE 16128
#ifndef BF_HEADER_BEGIN
#error "Header start offset required by tape auditor"
#endif
#ifndef BF_HEADER_END
#error "Header end offset required by tape auditor"
#endif

typedef struct {
    uint64_t instructions;
    uint64_t tape_operations;
    uint64_t writes;
    uint64_t source_lane_writes;
    size_t low, high;
} TapeAuditPhase;

static int from_hex(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static size_t audit_source_length;
static uint8_t audit_source[BF_MAX_SOURCE];

static int audit_init(const char *hex) {
    size_t n = strlen(hex);
    if (n & 1 || n / 2 > BF_MAX_SOURCE * 4) return 0;
    audit_source_length = 0;
    for (size_t i = 0; i < n / 2; i++) {
        int hi = from_hex(hex[2*i]), lo = from_hex(hex[2*i+1]);
        if (hi < 0 || lo < 0) return 0;
        uint8_t byte = (uint8_t)((hi << 4) | lo);
        /* BF input has no raw NUL sentinel. Escape-decoded NUL and FF
         * are both stored as SOH (01), a noninstruction. */
        if (isbf(byte)) {
            if (audit_source_length == BF_MAX_SOURCE) return 0;
            audit_source[audit_source_length++] = byte;
        }
    }
    return 1;
}

static int audit_source_cells(const uint8_t *tape) {
    for (size_t i = 0; i < audit_source_length; i++) {
        size_t at = BF_SOURCE_BASE + BF_SOURCE_STRIDE*i;
        if (tape[at] != audit_source[i]) {
            fprintf(stderr, "AUDIT_FAIL source_byte=%zu cell=%zu got=%02x expected=%02x\n",
                    i, at, tape[at], audit_source[i]);
            return 0;
        }
    }
    return 1;
}
#endif

/* Decoder insertion ownership audit. Only enabled for the historical BF prototype.
 * The interpreter does not perform source filtering or compilation here.
 */
#ifdef BF_PATCH_AUDIT
#ifndef BF_PATCH_START
#error "BF_PATCH_START is required for the experimental decoder audit"
#endif
#ifndef BF_PATCH_END
#error "BF_PATCH_END is required for the experimental decoder audit"
#endif
static size_t patch_audit_visits, patch_audit_preserved;
static size_t patch_entry_ptr;
static uint8_t patch_preceding_high, patch_following_high;
static int patch_audit_active;

static int patch_audit_check(const uint8_t *tape, size_t ptr, size_t pc) {
    if (pc == BF_PATCH_START) {
        if (patch_audit_active || ptr < 1 || ptr + 21 >= 65536) return 0;
        patch_entry_ptr = ptr;
        patch_preceding_high = tape[ptr-1];
        patch_following_high = tape[ptr+3];
        /* Two remote lanes are temporary backups, never persistent state. */
        if (tape[ptr+17] != 0 || tape[ptr+21] != 0) return 0;
        patch_audit_active = 1;
        patch_audit_visits++;
    } else if (pc == BF_PATCH_END) {
        if (!patch_audit_active || (ptr != patch_entry_ptr && ptr + 4 != patch_entry_ptr)) return 0;
        /* Compaction retires the next record and may clear its high count.
         * When no record is retired, both count lanes must be unchanged.
         */
        int retained = ptr == patch_entry_ptr;
        if (tape[patch_entry_ptr-1] != patch_preceding_high ||
            (retained && tape[patch_entry_ptr+3] != patch_following_high) ||
            (!retained && tape[patch_entry_ptr+3] != 0 &&
             tape[patch_entry_ptr+3] != patch_following_high) ||
            tape[patch_entry_ptr+17] != 0 || tape[patch_entry_ptr+21] != 0) {
            fprintf(stderr, "PATCH_AUDIT count_before=%u,%u count_after=%u,%u scratch=%u,%u retired=%d\n",
                    patch_preceding_high, patch_following_high,
                    tape[patch_entry_ptr-1], tape[patch_entry_ptr+3],
                    tape[patch_entry_ptr+17], tape[patch_entry_ptr+21], !retained);
            return 0;
        }
        patch_audit_active = 0;
        patch_audit_preserved++;
    }
    return 1;
}
#endif

static int isbf(int c) {
    return c == '>' || c == '<' || c == '+' || c == '-' ||
           c == '.' || c == ',' || c == '[' || c == ']';
}
int main(int argc, char **argv) {
#ifdef _WIN32
    if (_setmode(_fileno(stdin), _O_BINARY) == -1 ||
        _setmode(_fileno(stdout), _O_BINARY) == -1) return 74;
#endif
#ifdef BF_TAPE_AUDIT
    if (argc != 4 || !audit_init(argv[3])) {
        fprintf(stderr, "usage: auditseed compiler.bf step-limit expected-decoded-source-hex\n");
        return 64;
    }
#else
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "usage: bfseed compiler.bf [step-limit]\n");
        return 64;
    }
#endif
    uint64_t max_steps = argc >= 3 ? strtoull(argv[2], NULL, 10) : 2000000000ULL;
    FILE *in = fopen(argv[1], "rb");
    if (!in) { perror("open source"); return 66; }
    size_t capacity=16384, length=0, depth=0;
    unsigned char *code=malloc(capacity);
    if (!code) return 71;
    for (int c; (c=fgetc(in))!=EOF;) {
        if (!isbf(c)) continue;
        if (length == capacity) {
            if (capacity > SIZE_MAX/2) return 71;
            capacity *= 2;
            unsigned char *p=realloc(code,capacity);
            if (!p) return 71;
            code=p;
        }
        code[length++]=(unsigned char)c;
    }
    fclose(in);
    size_t *jump=calloc(length ? length : 1, sizeof(*jump));
    size_t *stack=malloc((length ? length : 1)*sizeof(*stack));
    if (!jump || !stack) return 71;
    for (size_t i=0; i<length; i++) {
        if (code[i]=='[') stack[depth++]=i;
        if (code[i]==']') {
            if (!depth) { fprintf(stderr,"unmatched close bracket\n"); return 65; }
            size_t open=stack[--depth];jump[open]=i;jump[i]=open;
        }
    }
    if (depth) { fprintf(stderr,"unmatched open bracket\n"); return 65; }
    uint8_t *tape=calloc(65536,1);
    if (!tape) return 71;
    static char outbuf[65536];
    setvbuf(stdout,outbuf,_IOFBF,sizeof(outbuf));
    size_t ptr=0;
    uint64_t steps=0;
#ifdef BF_TAPE_AUDIT
    TapeAuditPhase phases[2] = {{0}};
    for (size_t i = 0; i < 2; i++) phases[i].low = 65536;
    int decoder_checked = 0;
    size_t header_entries = 0, header_exits = 0;
#endif
    for (size_t pc=0; pc<length; pc++) {
        if (++steps>max_steps) { fprintf(stderr,"step limit reached\n"); return 124; }
#ifdef BF_PATCH_AUDIT
        if (!patch_audit_check(tape, ptr, pc)) {
            fprintf(stderr, "PATCH_AUDIT_FAIL pc=%zu ptr=%zu visits=%zu preserved=%zu\n",
                    pc, ptr, patch_audit_visits, patch_audit_preserved);
            return 90;
        }
#endif

#ifdef BF_TAPE_AUDIT
        /* Header scratch contract is separate from source-buffer decoding.
         * This branch only exists in the instrumented interpreter build. */
        if (pc == BF_HEADER_BEGIN || pc == BF_HEADER_END) {
            if (ptr != 60 || tape[61] != 0) {
                fprintf(stderr, "AUDIT_FAIL header_scratch pc=%zu ptr=%zu scratch=%u\n",
                        pc, ptr, tape[61]);
                return 90;
            }
            if (pc == BF_HEADER_BEGIN) header_entries++;
            else header_exits++;
        }
        /* Check source bytes at phase boundaries. Codegen temporarily writes
         * source-byte cells; requiring them to stay unchanged at every step
         * would reject the correct compiler. */
        if (!decoder_checked && pc == BF_DECODE_END) {
            if (!audit_source_cells(tape)) return 90;
            decoder_checked = 1;
        }
        size_t phase_idx = pc < BF_DECODE_END ? 0 : 1;
        TapeAuditPhase *phase = &phases[phase_idx];
        phase->instructions++;
        if (ptr < phase->low) phase->low = ptr;
        if (ptr > phase->high) phase->high = ptr;
        if (code[pc] != '>' && code[pc] != '<') phase->tape_operations++;
        if (code[pc] == '+' || code[pc] == '-' || code[pc] == ',') phase->writes++;
        if (decoder_checked &&
            (code[pc] == '+' || code[pc] == '-' || code[pc] == ',') &&
            ptr >= BF_SOURCE_BASE &&
            (ptr - BF_SOURCE_BASE) % BF_SOURCE_STRIDE == 0 &&
            (ptr - BF_SOURCE_BASE) / BF_SOURCE_STRIDE < audit_source_length) {
            phase->source_lane_writes++;
        }
#endif
        switch (code[pc]) {
            case '>': if (ptr==65535) {fprintf(stderr,"pointer overflow\n");return 2;}ptr++;break;
            case '<': if (!ptr) {fprintf(stderr,"pointer underflow\n");return 2;}ptr--;break;
            case '+': tape[ptr]++;break;
            case '-': tape[ptr]--;break;
            case '.': if (putchar(tape[ptr])==EOF) return 74;break;
            case ',': {int c=getchar();tape[ptr]=c==EOF?0:(uint8_t)c;break;}
            case '[': if (!tape[ptr]) pc=jump[pc];break;
            case ']': if (tape[ptr]) pc=jump[pc];break;
        }
    }
    if (fflush(stdout)==EOF) return 74;
#ifdef BF_TAPE_AUDIT
    if (!decoder_checked || !audit_source_cells(tape)) {
        fprintf(stderr, "AUDIT_FAIL decoder_missing_or_source_corrupted\n");
        return 92;
    }
    for (size_t i = 0; i < 2; i++) {
        fprintf(stderr, "TAPE_AUDIT phase=%zu steps=%llu accesses=%llu writes=%llu source_lane_writes=%llu low=%zu high=%zu\n",
                i, (unsigned long long)phases[i].instructions,
                (unsigned long long)phases[i].tape_operations,
                (unsigned long long)phases[i].writes,
                (unsigned long long)phases[i].source_lane_writes,
                phases[i].low, phases[i].high);
    }
    fprintf(stderr, "TAPE_AUDIT preserved_source_bytes=%zu\n", audit_source_length);
    if (header_entries != 1 || header_exits != 1) {
        fprintf(stderr, "AUDIT_FAIL header_phase_count entries=%zu exits=%zu\n",
                header_entries, header_exits);
        return 90;
    }
    fprintf(stderr, "HEADER_SCRATCH_AUDIT entries=%zu exits=%zu pointer=60 scratch=0\n",
            header_entries, header_exits);
#endif
#ifdef BF_PATCH_AUDIT
    if (patch_audit_active || patch_audit_preserved != patch_audit_visits) {
        fprintf(stderr, "PATCH_AUDIT_FAIL incomplete decoder pass\n");
        return 91;
    }
    fprintf(stderr, "PATCH_AUDIT visits=%zu conserved=%zu\n",
            patch_audit_visits, patch_audit_preserved);
#endif
    fprintf(stderr,"STEPS=%llu\n",(unsigned long long)steps);
    free(tape);free(jump);free(stack);free(code);
    return 0;
}

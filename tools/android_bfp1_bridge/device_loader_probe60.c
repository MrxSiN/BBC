/* Android AArch64 loader/ABI acceptance for Brainfuck-emitted callable DSOs.
 * This is a host-side test executable: it does not compile or interpret BF.
 * Build with the Android NDK and execute on a real arm64 Android system.
 */
#include <dlfcn.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef uint64_t (*bfc_entry)(const uint8_t *, uint64_t, uint8_t *, uint64_t,
                              uint8_t *, uint64_t, uint64_t, uint64_t *);

static int expect(int condition, const char *what) {
    if (!condition) fprintf(stderr, "FAIL %s\n", what);
    return condition ? 0 : 1;
}
static int check_run(bfc_entry fn, const char *label,
                     const uint8_t *input, uint64_t input_size,
                     uint8_t *output, uint64_t output_cap,
                     uint8_t *tape, uint64_t tape_size, uint64_t gas,
                     uint64_t expected_status, const uint8_t *expected_output,
                     uint64_t expected_size, uint8_t tape0, uint8_t tape1,
                     uint8_t tape2) {
    uint64_t used = UINT64_MAX;
    uint64_t status = fn(input, input_size, output, output_cap,
                         tape, tape_size, gas, &used);
    int bad = 0;
    bad += expect(status == expected_status, "policy status");
    bad += expect(used == expected_size, "output-used count");
    if (used <= output_cap && used == expected_size && used != 0)
        bad += expect(memcmp(output, expected_output, (size_t)used) == 0,
                      "output bytes");
    bad += expect(tape[0] == tape0, "tape cell 0");
    if (tape_size > 1) bad += expect(tape[1] == tape1, "tape cell 1");
    if (tape_size > 2) bad += expect(tape[2] == tape2, "tape cell 2");
    if (!bad) printf("PASS %s status=%" PRIu64 " used=%" PRIu64 "\n",
                     label, status, used);
    return bad;
}
int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: probe case absolute-policy-so\n");
        return 64;
    }
    void *handle = dlopen(argv[2], RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        fprintf(stderr, "FAIL dlopen: %s\n", dlerror());
        return 65;
    }
    dlerror();
    bfc_entry call = (bfc_entry)dlsym(handle, "bfc_call_v1");
    const char *err = dlerror();
    if (err || !call) {
        fprintf(stderr, "FAIL dlsym: %s\n", err ? err : "null symbol");
        dlclose(handle);
        return 66;
    }
    uint8_t tape[64] = {0}, output[16] = {0};
    static const uint8_t input[] = {0x00, 0xff};
    static const uint8_t io[] = {0x00, 0xff, 0x00};
    static const uint8_t one[] = {1};
    static const uint8_t six[] = {6};
    int bad = 0;
    if (!strcmp(argv[1], "empty"))
        bad = check_run(call,"empty",input,2,output,16,tape,64,0,0,NULL,0,0,0,0);
    else if (!strcmp(argv[1], "io_eof"))
        bad = check_run(call,"io_eof",input,2,output,16,tape,64,0,0,io,3,0,0,0);
    else if (!strcmp(argv[1], "transfer"))
        bad = check_run(call,"transfer",input,2,output,16,tape,64,3,0,one,1,0,1,0);
    else if (!strcmp(argv[1], "nested"))
        bad = check_run(call,"nested",input,2,output,16,tape,64,10,0,six,1,0,0,6);
    else if (!strcmp(argv[1], "pointer_trap"))
        bad = check_run(call,"pointer_trap",input,2,output,16,tape,2,0,3,NULL,0,0,0,0);
    else if (!strcmp(argv[1], "output_full"))
        bad = check_run(call,"output_full",input,2,output,0,tape,64,0,2,NULL,0,1,0,0);
    else if (!strcmp(argv[1], "gas_trap"))
        bad = check_run(call,"gas_trap",input,2,output,16,tape,64,2,1,NULL,0,3,0,0);
    else if (!strcmp(argv[1], "zero_skip"))
        bad = check_run(call,"zero_skip",input,2,output,16,tape,64,0,0,NULL,0,0,0,0);
    else if (!strcmp(argv[1], "persistent")) {
        bad += check_run(call,"persistent_first",input,2,output,16,tape,64,0,0,one,1,1,0,0);
        static const uint8_t two[] = {2};
        bad += check_run(call,"persistent_second",input,2,output,16,tape,64,0,0,two,1,2,0,0);
    } else if (!strcmp(argv[1], "host_stub")) {
        /* Host-side stub transport validation, never BF-generated execution. */
        static const uint8_t copied[] = {0,255};
        bad = check_run(call,"host_stub",input,2,output,16,tape,64,0,0,copied,2,1,0,0);
    } else {
        fprintf(stderr,"FAIL unknown case: %s\n",argv[1]);
        bad = 1;
    }
    if (dlclose(handle) != 0) {
        fprintf(stderr,"FAIL dlclose\n");
        bad++;
    }
    return bad ? 1 : 0;
}

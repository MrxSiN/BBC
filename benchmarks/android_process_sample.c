/* Measure on the device, excluding ADB transport. Includes fork, exec and I/O. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static void fail(const char *what) { perror(what); exit(1); }
static uint64_t now(void) {
    struct timespec stamp;
    if (clock_gettime(CLOCK_MONOTONIC, &stamp)) fail("clock_gettime");
    return (uint64_t)stamp.tv_sec * 1000000000 + stamp.tv_nsec;
}

int main(int argc, char **argv) {
    if (argc < 3) return 64;
    char *end;
    long value = strtol(argv[1], &end, 10);
    if (*end || value < -1 || value > 255) return 64;
    int input[2], output[2];
    if (pipe(input) || pipe(output)) fail("pipe");
    unsigned char byte = (unsigned char)value;
    if (value >= 0 && write(input[1], &byte, 1) != 1) fail("input");
    close(input[1]);
    uint64_t start = now();
    pid_t child = fork();
    if (child < 0) fail("fork");
    if (!child) {
        if (dup2(input[0], 0) < 0 || dup2(output[1], 1) < 0) _exit(126);
        close(input[0]); close(output[0]); close(output[1]);
        execvp(argv[2], argv + 2);
        _exit(127);
    }
    close(input[0]); close(output[1]);
    unsigned char actual[2];
    size_t count = 0;
    while (count < sizeof(actual)) {
        ssize_t size = read(output[0], actual + count, sizeof(actual) - count);
        if (size < 0) { if (errno == EINTR) continue; fail("read"); }
        if (!size) break;
        count += (size_t)size;
    }
    close(output[0]);
    struct rusage usage;
    int status;
    while (wait4(child, &status, 0, &usage) < 0) {
        if (errno != EINTR) fail("wait4");
    }
    uint64_t elapsed = now() - start;
    if (!WIFEXITED(status) || WEXITSTATUS(status) || count != 1 ||
        actual[0] != (value < 0 ? 0 : byte)) {
        fprintf(stderr, "invalid sample: wait_status=%d output_bytes=%zu\n", status, count);
        return 65;
    }
    printf("%llu %ld\n", (unsigned long long)elapsed, usage.ru_maxrss);
    return 0;
}

/* A device-local warmed stream timer; each request's exact response is checked. */
#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static void fail(const char *what) { perror(what); exit(65); }
static uint64_t now(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) fail("clock");
    return (uint64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}
int main(int argc, char **argv) {
    if (argc < 2) return 64;
    signal(SIGPIPE, SIG_IGN);
    int input[2], output[2];
    if (pipe(input) || pipe(output)) fail("pipe");
    pid_t child = fork();
    if (child < 0) fail("fork");
    if (!child) {
        if (dup2(input[0], 0) < 0 || dup2(output[1], 1) < 0) _exit(126);
        close(input[0]); close(input[1]); close(output[0]); close(output[1]);
        execvp(argv[1], argv + 1); _exit(127);
    }
    close(input[0]); close(output[1]);
    unsigned char request[256], response[256];
    for (size_t i = 0; i < sizeof(request); i++) request[i] = (unsigned char)(i % 255 + 1);
    uint64_t samples[64];
    for (size_t batch = 0; batch < 128; batch++) {
        uint64_t started = now();
        size_t sent = 0, received = 0;
        while (sent < sizeof(request)) {
            ssize_t n = write(input[1], request + sent, sizeof(request) - sent);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) fail("request"); sent += (size_t)n;
        }
        while (received < sizeof(response)) {
            ssize_t n = read(output[0], response + received, sizeof(response) - received);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) fail("response"); received += (size_t)n;
        }
        uint64_t duration = now() - started;
        if (memcmp(request, response, sizeof(request))) fail("wrong response");
        if (batch >= 64) samples[batch - 64] = duration;
    }
    unsigned char stop = 0;
    if (write(input[1], &stop, 1) != 1) fail("stop"); close(input[1]);
    unsigned char extra;
    ssize_t extra_bytes;
    do { extra_bytes = read(output[0], &extra, 1); } while (extra_bytes < 0 && errno == EINTR);
    close(output[0]);
    int status;
    while (waitpid(child, &status, 0) < 0) { if (errno != EINTR) fail("wait"); }
    if (extra_bytes != 0 || !WIFEXITED(status) || WEXITSTATUS(status)) return 65;
    for (size_t i = 0; i < 64; i++) printf("%llu\n", (unsigned long long)samples[i]);
    return 0;
}

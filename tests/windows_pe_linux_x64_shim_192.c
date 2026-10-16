/*
 * Offline Windows PE native x64 execution test harness.
 * NOT a Windows loader, NOT part of the Brainfuck compiler.
 * Runs actual x64 instruction bytes in a Linux process with a small test-only
 * KERNEL32 import shim. No JIT, no BF compilation logic.
 * Only accepts the expanded fixed-layout 192-slot three-section test images.
 *
 * Exit status: 0 for ExitProcess(0), 99 for UD2 / SIGILL, 98 for harness error.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <setjmp.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <ucontext.h>

#define PE_BASE ((uintptr_t)0x140000000ULL)
#define PE_IMAGE_SIZE 0x13000U
#define PE_SIZE 3584U
static sigjmp_buf checkpoint;
static uint8_t input[1048576], output[1048576];
static size_t input_length, input_cursor, output_length;
static int outcome = 98;
static uintptr_t fault_ip;

static uint16_t read16(const uint8_t *s) {return (uint16_t)s[0] | (uint16_t)s[1]<<8;}
static uint32_t read32(const uint8_t *s) {return (uint32_t)s[0] | (uint32_t)s[1]<<8 | (uint32_t)s[2]<<16 | (uint32_t)s[3]<<24;}
static void on_signal(int signum, siginfo_t *info, void *ctx) {
    (void)info;
    fault_ip=(uintptr_t)((ucontext_t*)ctx)->uc_mcontext.gregs[REG_RIP];
    outcome = signum == SIGILL ? 99 : 98;
    siglongjmp(checkpoint, 1);
}
__attribute__((ms_abi, noreturn)) static void shim_exit(uint32_t status) {
    outcome = (int)(status & 255);
    siglongjmp(checkpoint, 1);
}
__attribute__((ms_abi)) static void *shim_stdhandle(int32_t which) {
    if (which == -11) return (void *)2;
    if (which == -10) return (void *)1;
    return (void *)(uintptr_t)-1;
}
__attribute__((ms_abi)) static uint32_t shim_read(void *handle, void *dst, uint32_t count,
    uint32_t *transferred, void *overlapped) {
    if (handle != (void *)1 || !dst || !transferred || overlapped) return 0;
    size_t available = input_length - input_cursor;
    size_t consumed = count < available ? count : available;
    memcpy(dst, input+input_cursor, consumed);
    input_cursor += consumed;
    *transferred = (uint32_t)consumed;
    return 1;
}
__attribute__((ms_abi)) static uint32_t shim_write(void *handle, const void *src,
    uint32_t count, uint32_t *transferred, void *overlapped) {
    if (handle != (void *)2 || !src || !transferred || overlapped ||
        count > sizeof(output) - output_length) return 0;
    memcpy(output+output_length, src, count);
    output_length += count;
    *transferred = count;
    return 1;
}
static int load_image(const uint8_t *image) {
    if (read16(image)!=0x5a4d || read32(image+0x3c)!=0x80 ||
        read32(image+0x80)!=0x00004550 || read16(image+0x84)!=0x8664 ||
        read16(image+0x86)!=3 || read16(image+0x98)!=0x20b) return -1;
    const uint8_t *opt = image+0x98;
    if (read32(opt+16)!=0x1000 || read32(opt+20)!=0x1000 ||
        read32(opt+32)!=0x1000 || read32(opt+36)!=0x200 ||
        read32(opt+56)!=PE_IMAGE_SIZE || read32(opt+60)!=0x200 ||
        read32(opt+24)!=0x40000000 || read32(opt+28)!=0x00000001) return -1;
    const uint8_t *sec=image+0x188;
    /* Reject unexpected section/relocation layouts instead of guessing. */
    if (memcmp(sec,".text",5)!=0 || read32(sec+8)!=0xA00 ||
        read32(sec+12)!=0x1000 || read32(sec+16)!=0xA00 ||
        read32(sec+20)!=0x200 ||
        memcmp(sec+40,".idata",6)!=0 || read32(sec+40+12)!=0x2000 ||
        read32(sec+40+20)!=0xC00 ||
        memcmp(sec+80,".tape",5)!=0 || read32(sec+80+12)!=0x3000 ||
        read32(sec+80+8)!=0x10000) return -1;
    uint8_t *memory=mmap((void*)PE_BASE,PE_IMAGE_SIZE,PROT_READ|PROT_WRITE|PROT_EXEC,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    if (memory==MAP_FAILED) return -1;
    memcpy(memory+0x1000,image+0x200,0xA00);
    memcpy(memory+0x2000,image+0xC00,0x200);
    /* Explicit test-only KERNEL32 IAT patch; this is not a PE loader. */
    void *fn[4]={(void*)shim_exit,(void*)shim_stdhandle,(void*)shim_read,(void*)shim_write};
    memcpy(memory+0x2000,fn,sizeof(fn));
    if (mprotect(memory+0x1000,0x1000,PROT_READ|PROT_EXEC)!=0 ||
        mprotect(memory+0x3000,0x10000,PROT_READ|PROT_WRITE)!=0) return -1;
    return 0;
}
int main(int argc,char **argv) {
    if (argc!=2) {fprintf(stderr,"usage: %s program.exe < input\n",argv[0]); return 98;}
    FILE *fp=fopen(argv[1],"rb");
    uint8_t image[PE_SIZE];
    if (!fp || fread(image,1,sizeof(image),fp)!=sizeof(image) || fgetc(fp)!=EOF) {
        if(fp)fclose(fp);
        fprintf(stderr,"invalid PE image size\n");return 98;
    }
    fclose(fp);
    input_length=fread(input,1,sizeof(input),stdin);
    if (!feof(stdin)) {fprintf(stderr,"input too large or unreadable\n");return 98;}
    if (load_image(image)) {fprintf(stderr,"PE test-harness layout mismatch\n");return 98;}
    struct sigaction action;memset(&action,0,sizeof(action));
    action.sa_sigaction=on_signal;action.sa_flags=SA_SIGINFO;sigemptyset(&action.sa_mask);
    sigaction(SIGILL,&action,NULL);sigaction(SIGSEGV,&action,NULL);
    sigaction(SIGBUS,&action,NULL);
    if (sigsetjmp(checkpoint,1)==0) {
        void (__attribute__((ms_abi)) *entry)(void)=(void*)PE_BASE+0x1000;
        entry();
        outcome=98; /* ExitProcess should never return. */
    }
    if (outcome == 99 || outcome == 98) fprintf(stderr,"fault IP=%#" PRIxPTR "\n",fault_ip);
    if (outcome == 0 && fwrite(output,1,output_length,stdout)!=output_length) return 98;
    return outcome;
}

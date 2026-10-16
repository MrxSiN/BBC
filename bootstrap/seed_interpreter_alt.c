/* Independent BF cold-bootstrap executor, not a compiler.
 * Keeps the original source bytes (including noncommands), discovers pairs
 * by a forward nesting scan rather than a bracket stack, and uses a switch
 * dispatch loop. A second executor is useful; two compilers are not.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

static int command(int c) {
    return c=='>' || c=='<' || c=='+' || c=='-' || c=='.' ||
           c==',' || c=='[' || c==']';
}
int main(int argc, char **argv) {
#ifdef _WIN32
    if (_setmode(_fileno(stdin), _O_BINARY) == -1 ||
        _setmode(_fileno(stdout), _O_BINARY) == -1) return 74;
#endif
    if (argc != 2 && argc != 3) return 64;
    FILE *file=fopen(argv[1],"rb");
    if (!file) return 66;
    if (fseek(file,0,SEEK_END)) return 74;
    long signed_size=ftell(file);
    if (signed_size<0 || fseek(file,0,SEEK_SET)) return 74;
    size_t len=(size_t)signed_size;
    if (len>SIZE_MAX/sizeof(size_t)-1) return 71;
    unsigned char *program=malloc(len+1);
    size_t *jump=malloc((len+1)*sizeof(*jump));
    unsigned char *memory=calloc(65536,1);
    if (!program || !jump || !memory) return 71;
    if (fread(program,1,len,file)!=len || fclose(file)) return 74;
    for (size_t at=0;at<len;at++) {
        if (program[at]==']') {
            /* Reject a closing bracket that is not paired during this pass. */
            size_t nesting=0;
            for (size_t pos=at; pos-- > 0;) {
                if (program[pos]==']') nesting++;
                if (program[pos]=='[') {
                    if (nesting) nesting--;
                    else { jump[at]=pos; goto paired_close; }
                }
            }
            return 65;
paired_close:;
        } else if (program[at]=='[') {
            size_t nesting=0;
            for (size_t pos=at+1;pos<len;pos++) {
                if (program[pos]=='[') nesting++;
                if (program[pos]==']') {
                    if (nesting) nesting--;
                    else {jump[at]=pos;goto paired_open;}
                }
            }
            return 65;
paired_open:;
        }
    }
    uint64_t limit = argc==3 ? strtoull(argv[2],NULL,10) : UINT64_MAX;
    uint64_t steps=0;
    size_t pointer=0;
    for (size_t pc=0;pc<len;pc++) {
        unsigned char op=program[pc];
        if (!command(op)) continue;
        if (++steps > limit) return 124;
        switch (op) {
          case '>': if (pointer==65535) return 2;pointer++;break;
          case '<': if (pointer==0) return 2;pointer--;break;
          case '+': memory[pointer]=(unsigned char)(memory[pointer]+1);break;
          case '-': memory[pointer]=(unsigned char)(memory[pointer]-1);break;
          case '.': if (putchar(memory[pointer])==EOF) return 74;break;
          case ',': {int value=getchar();memory[pointer]=value==EOF?0:(unsigned char)value;break;}
          case '[': if (!memory[pointer])pc=jump[pc];break;
          case ']': if (memory[pointer])pc=jump[pc];break;
        }
    }
    if (fflush(stdout)==EOF) return 74;
    fprintf(stderr,"STEPS=%llu\n",(unsigned long long)steps);
    free(memory);free(jump);free(program);
    return 0;
}

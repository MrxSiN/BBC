cmake_minimum_required(VERSION 3.22.1)
project(gmailbf C ASM)
add_library(gmailbf SHARED bf_native_jni.c bf_native.S)
target_compile_options(gmailbf PRIVATE -O3 -fvisibility=hidden -Wall -Wextra -Werror
    -fstack-protector-strong -D_FORTIFY_SOURCE=2)
target_link_options(gmailbf PRIVATE -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack
    -Wl,-z,max-page-size=16384)

cmake_minimum_required(VERSION 3.18.1)
project(brainfuckcc_bfp1_jni_bridge C)
add_library(brainfuckcc_bridge SHARED bfp1_jni_bridge.c)
target_compile_features(brainfuckcc_bridge PRIVATE c_std_11)
target_link_libraries(brainfuckcc_bridge PRIVATE dl)
# This builds ONLY the JNI host bridge. Policy .so machine code and ELF metadata
# are emitted by standard Brainfuck via bootstrap.android_dynamic_callable59.

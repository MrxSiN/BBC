/* Android JNI host transport for an already BF-compiled AArch64 policy DSO.
 * This code NEVER parses BF or produces native instructions. Android NDK is
 * needed to build this host bridge, not to build BF policy machine code.
 */
#include <jni.h>
#include <dlfcn.h>
#include <stdint.h>

/* x0 ... x7 follow standard AAPCS64 argument assignment. Return x0 is the
 * BFP1 status. The optional x1 budget-used value is NOT exposed here because
 * plain C return values do not reliably capture a second return register.
 */
typedef uint64_t (*bfp1_entry)(const uint8_t *, uint64_t, uint8_t *, uint64_t,
                               uint8_t *, uint64_t, uint64_t, uint64_t *);

/* Java API: static native int run(String libraryPath, byte[] input,
 * byte[] output, byte[] tape, long budget, long[] outputUsed);
 * Output and tape bytes are committed even if the BF policy returns a trap.
 * Negative results denote host-side failures, not BF status codes 0..3.
 */
JNIEXPORT jint JNICALL Java_org_brainfuckcc_Bfp1Bridge_run(
        JNIEnv *env, jclass cls, jstring library, jbyteArray input,
        jbyteArray output, jbyteArray tape, jlong gas, jlongArray used) {
    (void)cls;
    if (!library || !input || !output || !tape || !used || gas < 0 ||
        (*env)->GetArrayLength(env, used) < 1 ||
        (*env)->GetArrayLength(env, tape) < 1) return -1;
    /* The disjoint-array contract prevents accidental Java array aliasing. */
    if ((*env)->IsSameObject(env, input, output) ||
        (*env)->IsSameObject(env, input, tape) ||
        (*env)->IsSameObject(env, output, tape)) return -1;
    const char *path = (*env)->GetStringUTFChars(env, library, NULL);
    if (!path) return -4;
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    (*env)->ReleaseStringUTFChars(env, library, path);
    if (!handle) return -2;
    bfp1_entry call = (bfp1_entry)dlsym(handle, "bfc_call_v1");
    if (!call) { dlclose(handle); return -3; }
    const uint64_t in_len = (uint64_t)(*env)->GetArrayLength(env, input);
    const uint64_t out_len = (uint64_t)(*env)->GetArrayLength(env, output);
    const uint64_t tape_len = (uint64_t)(*env)->GetArrayLength(env, tape);
    /* A zero-length Java array may have no pinned address. Give the native
     * function a valid sentinel pointer, with the length/capacity still zero.
     * The BF policy is not allowed to dereference the sentinel in that case.
     */
    jbyte empty_input = 0, empty_output = 0;
    jbyte *src = in_len ? (*env)->GetByteArrayElements(env, input, NULL) : &empty_input;
    if (!src) { dlclose(handle); return -4; }
    jbyte *dst = out_len ? (*env)->GetByteArrayElements(env, output, NULL) : &empty_output;
    if (!dst) { if (in_len) (*env)->ReleaseByteArrayElements(env,input,src,JNI_ABORT);
                dlclose(handle); return -4; }
    jbyte *cells = (*env)->GetByteArrayElements(env, tape, NULL);
    if (!cells) { if (out_len) (*env)->ReleaseByteArrayElements(env,output,dst,JNI_ABORT);
                  if (in_len) (*env)->ReleaseByteArrayElements(env,input,src,JNI_ABORT);
                  dlclose(handle); return -4; }
    uint64_t wrote = 0;
    const uint64_t status = call((const uint8_t *)src,in_len,(uint8_t *)dst,out_len,
                                 (uint8_t *)cells,tape_len,(uint64_t)gas,&wrote);
    (*env)->ReleaseByteArrayElements(env,tape,cells,0);
    if (out_len) (*env)->ReleaseByteArrayElements(env,output,dst,0);
    if (in_len) (*env)->ReleaseByteArrayElements(env,input,src,JNI_ABORT);
    dlclose(handle);
    if (wrote > out_len || wrote > INT64_MAX) return -5;
    const jlong count = (jlong)wrote;
    (*env)->SetLongArrayRegion(env,used,0,1,&count);
    if ((*env)->ExceptionCheck(env)) return -4;
    if (status > 3) return -5;
    return (jint)status;
}

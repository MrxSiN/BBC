/* Platform boundary only: call BF-produced machine bytes embedded by the linker. */
#include <jni.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "generated/bf_abi.h"

extern const unsigned char bf_row[], bf_scope[];
typedef struct { uint64_t status, ticks; } result;
typedef result (*policy_fn)(const uint8_t *, size_t, uint8_t *, size_t,
                           uint8_t *, size_t, uint64_t, size_t *);

JNIEXPORT jint JNICALL
Java_my_MrxSiN_gmailhideads_policy_GmailPolicy_nativeRun(JNIEnv *env, jclass cls,
        jint program, jobject request, jint length, jobject response) {
    (void)cls;
    if (program < 0 || program > 1) return -4;
    if (!request || !response || length < 0 || length > BF_RUNTIME_IN_CAP) return -5;
    const uint8_t *in = (*env)->GetDirectBufferAddress(env, request);
    uint8_t *out = (*env)->GetDirectBufferAddress(env, response);
    jlong in_cap = (*env)->GetDirectBufferCapacity(env, request);
    jlong out_cap = (*env)->GetDirectBufferCapacity(env, response);
    if (!in || !out || in_cap < length || out_cap <= 0) return -5;
    uint8_t tape[32] = {0};
    size_t out_len = 0;
    const unsigned char *image = program == 0 ? bf_row : bf_scope;
    policy_fn fn = (policy_fn)(image + 128);
    result r = fn(in, (size_t)length, out,
                  out_cap < BF_RUNTIME_OUT_CAP ? (size_t)out_cap : BF_RUNTIME_OUT_CAP,
                  tape, sizeof(tape), BF_BUDGET_BASE + (uint64_t)length * BF_BUDGET_PER_BYTE,
                  &out_len);
    return r.status ? -(jint)r.status : (jint)out_len;
}

JNIEXPORT jint JNICALL
Java_my_MrxSiN_gmailhideads_policy_GmailPolicy_nativeAbi(JNIEnv *env, jclass cls) {
    (void)env; (void)cls;
    return (BF_ABI_MAJOR << 8) | BF_ABI_MINOR;
}

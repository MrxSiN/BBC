package org.brainfuckcc;

/** Host JNI transport smoke test using a TEST ONLY ELF policy stub. */
public final class Bfp1BridgeSmoke {
    public static void main(String[] args) {
        if (args.length != 1) throw new IllegalArgumentException("library path missing");
        byte[] tape = {0, 0};
        byte[] output = new byte[3];
        long[] used = {-1};
        int status = Bfp1Bridge.run(args[0],new byte[]{10,20,30},output,tape,100,used);
        if (status != 0 || used[0] != 3 || tape[0] != 1 ||
            output[0] != 10 || output[1] != 20 || output[2] != 30)
            throw new AssertionError("JNI basic copy or tape persistence failed");
        byte[] tiny = new byte[1];
        status = Bfp1Bridge.run(args[0],new byte[]{40,50},tiny,tape,0,used);
        if (status != 2 || used[0] != 1 || tiny[0] != 40 || tape[0] != 2)
            throw new AssertionError("JNI limited output or state reuse failed");
        status = Bfp1Bridge.run(args[0] + "_not_found",new byte[0],
                                tiny,tape,0,used);
        if (status != -2) throw new AssertionError("bad dlopen path accepted");
        status = Bfp1Bridge.run(args[0],new byte[0],tiny,tape,-1,used);
        if (status != -1) throw new AssertionError("negative budget accepted");
        // Empty input and output must not depend on JNI pinning a zero-byte array.
        used[0] = -7;
        status = Bfp1Bridge.run(args[0],new byte[0],new byte[0],tape,0,used);
        if (status != 0 || used[0] != 0 || tape[0] != 3)
            throw new AssertionError("zero-length JNI arrays failed");
        used[0] = -7;
        status = Bfp1Bridge.run(args[0],new byte[]{77},new byte[0],tape,0,used);
        if (status != 2 || used[0] != 0 || tape[0] != 4)
            throw new AssertionError("zero capacity did not report output full");
        byte[] alias = {1,2};
        if (Bfp1Bridge.run(args[0],alias,alias,tape,0,used) != -1)
            throw new AssertionError("JNI array alias permitted");
        if (Bfp1Bridge.run(args[0],new byte[0],new byte[0],new byte[0],0,used) != -1)
            throw new AssertionError("empty tape accepted");
        if (Bfp1Bridge.run(args[0],new byte[0],new byte[0],tape,0,new long[0]) != -1)
            throw new AssertionError("empty outputUsed accepted");
        if (Bfp1Bridge.run(args[0],new byte[0],new byte[0],tape,0,used) != 0)
            throw new AssertionError("zero-length repeated JNI call failed");
        System.out.println("PASS host JVM JNI bridge dlopen dlsym byte IO state output traps zero-buffers alias validation");
    }
}

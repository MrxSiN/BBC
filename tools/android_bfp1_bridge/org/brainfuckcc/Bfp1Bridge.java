package org.brainfuckcc;

/** Host-only Android adapter for one BF-compiled callable policy library.
 * A nonempty tape is supplied by the caller. Keep the same byte[] for
 * persistent state or pass a new, zero-filled array for isolated requests.
 * Output and tape are mutated. outputUsed[0] reports produced byte count.
 * The caller must use a loader-visible absolute library path.
 */
public final class Bfp1Bridge {
    static {
        String testPath = System.getProperty("brainfuckcc.bridge.absolutePath");
        if (testPath == null || testPath.length() == 0)
            System.loadLibrary("brainfuckcc_bridge");
        else
            System.load(testPath);
    }
    private Bfp1Bridge() {}

    /** BF statuses: 0 success, 1 gas exhausted, 2 output full,
     * 3 tape boundary. Host failures: -1 invalid parameters,
     * -2 dlopen failed, -3 missing symbol, -4 JNI allocation failed,
     * -5 corrupt result. Budget is charged at nonzero loop entries.
     */
    public static native int run(String libraryPath, byte[] input,
                                 byte[] output, byte[] tape,
                                 long budget, long[] outputUsed);
}

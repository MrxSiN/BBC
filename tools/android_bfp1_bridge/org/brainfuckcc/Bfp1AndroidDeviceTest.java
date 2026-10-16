package org.brainfuckcc;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

/** Android ART device gate for actual BF-generated callable policy libraries.
 * This class contains assertions and transport only, never compilation logic.
 * Also executed on Linux JVM against explicitly test-only native stubs.
 */
public final class Bfp1AndroidDeviceTest {
    private Bfp1AndroidDeviceTest() {}

    private static void run(String root, String name, byte[] input, int tapeSize,
                            int outputCap, long gas, int status, byte[] wanted,
                            int[] tapeCells, List<String> report, String prefix) {
        byte[] output = new byte[outputCap];
        byte[] tape = new byte[tapeSize];
        long[] used = {-777};
        int actual = Bfp1Bridge.run(root + "/" + prefix + name + ".so", input, output, tape, gas, used);
        if (actual != status || used[0] != wanted.length ||
            !Arrays.equals(Arrays.copyOf(output, wanted.length), wanted)) {
            throw new AssertionError(name + ": status=" + actual + " used=" + used[0] +
                                     " expectedStatus=" + status + " expectedUsed=" + wanted.length);
        }
        if (tapeCells.length > tapeSize) throw new AssertionError("invalid fixture tape contract");
        for (int i = 0; i < tapeCells.length; i++) {
            if ((tape[i] & 255) != tapeCells[i]) {
                throw new AssertionError(name + ": tape[" + i + "]=" + (tape[i] & 255) +
                                         " expected=" + tapeCells[i]);
            }
        }
        report.add("PASS JNI " + name);
    }

    /** Shared fixture assertions: shell ART uses plain names, APK uses libbfc_ names.
     * The APK must pass its own nativeLibraryDir; no test-only loader override.
     */
    public static List<String> verify(String root, String prefix) {
        List<String> report = new ArrayList<String>();
        byte[] input = {0, (byte)255};
        run(root, "empty", input, 64, 16, 0, 0, new byte[0], new int[]{0,0,0}, report, prefix);
        run(root, "io_eof", input, 64, 16, 0, 0,
            new byte[]{0,(byte)255,0}, new int[]{0,0,0}, report, prefix);
        run(root, "transfer", input, 64, 16, 3, 0,
            new byte[]{1}, new int[]{0,1,0}, report, prefix);
        run(root, "nested", input, 64, 16, 10, 0,
            new byte[]{6}, new int[]{0,0,6}, report, prefix);
        run(root, "pointer_trap", input, 2, 16, 0, 3,
            new byte[0], new int[]{0,0}, report, prefix);
        run(root, "output_full", input, 64, 0, 0, 2,
            new byte[0], new int[]{1,0,0}, report, prefix);
        run(root, "gas_trap", input, 64, 16, 2, 1,
            new byte[0], new int[]{3,0,0}, report, prefix);
        run(root, "zero_skip", input, 64, 16, 0, 0,
            new byte[0], new int[]{0,0,0}, report, prefix);

        byte[] tape = new byte[64];
        byte[] output = new byte[16];
        long[] used = {-1};
        String persistent = root + "/" + prefix + "persistent.so";
        for (int expected = 1; expected <= 2; expected++) {
            Arrays.fill(output, (byte)0);
            int status = Bfp1Bridge.run(persistent, input, output, tape, 0, used);
            if (status != 0 || used[0] != 1 || (output[0] & 255) != expected ||
                (tape[0] & 255) != expected)
                throw new AssertionError("persistent JNI state failed on call " + expected);
        }
        report.add("PASS JNI persistent");

        // Host transport negative gates, never exceptions disguised as BF success.
        if (Bfp1Bridge.run(root + "/missing.so", input, output, tape, 0, used) != -2)
            throw new AssertionError("missing shared object accepted");
        if (Bfp1Bridge.run(persistent, input, input, tape, 0, used) != -1)
            throw new AssertionError("aliased native byte arrays accepted");
        if (Bfp1Bridge.run(persistent, input, output, new byte[0], 0, used) != -1)
            throw new AssertionError("empty tape accepted");
        if (Bfp1Bridge.run(persistent, input, output, tape, -1, used) != -1)
            throw new AssertionError("negative budget accepted");
        report.add("PASS JNI transport_guards");
        report.add("PASS JNI suite 9 policy fixtures");
        return report;
    }

    public static void main(String[] args) {
        if (args.length != 2) throw new IllegalArgumentException("bridge path and fixture dir required");
        // The shell ART runner cannot rely on the application library namespace.
        System.setProperty("brainfuckcc.bridge.absolutePath", args[0]);
        for (String line : verify(args[1], "")) System.out.println(line);
    }
}

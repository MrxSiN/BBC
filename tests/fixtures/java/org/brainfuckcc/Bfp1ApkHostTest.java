package org.brainfuckcc;
import java.util.List;
/** Linux JVM test of the same APK-library naming and assertions; C STUBS ONLY. */
public final class Bfp1ApkHostTest {
    public static void main(String[] args) {
        if (args.length != 2) throw new AssertionError("bridge and library directory required");
        System.setProperty("brainfuckcc.bridge.absolutePath", args[0]);
        List<String> lines = Bfp1AndroidDeviceTest.verify(args[1], "libbfc_");
        if (lines.size() != 11) throw new AssertionError("missing APK JNI assertions");
        for (String line : lines) System.out.println(line.replace("PASS JNI ", "PASS APK "));
    }
}

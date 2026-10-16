package org.brainfuckcc;

import android.app.Activity;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;

/** Test-only installed APK gate for BF-generated shared objects.
 * The JNI bridge is host transport. All BF policy machine code is emitted by
 * the authoritative Brainfuck compiler and packaged unchanged.
 */
public final class Bfp1ApkAcceptanceActivity extends Activity {
    public static final String REPORT = "bfc62_result.txt";

    private void save(String data) throws Exception {
        File file = new File(getFilesDir(), REPORT);
        try (FileOutputStream out = new FileOutputStream(file, false)) {
            out.write(data.getBytes(StandardCharsets.US_ASCII));
            out.getFD().sync();
        }
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        String nonce = getIntent().getStringExtra("nonce");
        // No permissive fallback if a test invocation is missing its nonce.
        if (nonce == null || !nonce.matches("[a-f0-9]{32}")) {
            finish();
            return;
        }
        StringBuilder result = new StringBuilder("BFC62_APK_BEGIN " + nonce + "\n");
        try {
            String nativeDir = getApplicationInfo().nativeLibraryDir;
            List<String> lines = Bfp1AndroidDeviceTest.verify(nativeDir, "libbfc_");
            if (lines.size() != 11) throw new AssertionError("incomplete JNI suite");
            for (String line : lines) {
                if (!line.startsWith("PASS JNI ")) throw new AssertionError("invalid gate line");
                result.append("PASS APK ").append(line.substring(9)).append('\n');
            }
            result.append("BFC62_APK_END ").append(nonce).append('\n');
        } catch (Throwable error) {
            result.append("BFC62_APK_FAIL ").append(nonce).append(' ')
                  .append(error.getClass().getName()).append('\n');
        }
        try {
            save(result.toString());
        } catch (Exception error) {
            android.util.Log.e("BFC62", "Cannot save acceptance result", error);
        }
        finish();
    }
}

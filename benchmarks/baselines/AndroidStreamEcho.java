import java.io.FileDescriptor;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

/** Same unbuffered byte request/response and zero-or-EOF termination as ,[.,]. */
public final class AndroidStreamEcho {
    public static void main(String[] args) {
        FileInputStream input = new FileInputStream(FileDescriptor.in);
        FileOutputStream output = new FileOutputStream(FileDescriptor.out);
        byte[] byteValue = new byte[1];
        while (true) {
            int size;
            try { size = input.read(byteValue); }
            catch (IOException error) { System.exit(4); return; }
            if (size < 1 || byteValue[0] == 0) return;
            try { output.write(byteValue); }
            catch (IOException error) { System.exit(3); return; }
        }
    }
}

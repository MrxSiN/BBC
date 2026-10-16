public final class AndroidTransfer {
    public static void main(String[] args) throws Exception {
        int value = System.in.read();
        int source = value < 0 ? 0 : value;
        int result = 0;
        while (source != 0) {
            result = (result + 1) & 255;
            source--;
        }
        System.out.write(result);
        System.out.flush();
        if (System.out.checkError()) throw new java.io.IOException("output failed");
    }
}

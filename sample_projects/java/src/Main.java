package sample;

public class Main {
    /**
     * Greets with a message.
     */
    public static String greet(String name) {
        return "Hello, " + name + "!";
    }

    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        System.out.println(greet("World"));
    }
}

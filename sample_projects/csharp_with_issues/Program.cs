using System;

namespace Sample {
  public class Greeter {
    public string Introduce(string name) {
      // documented in README
      return $"Hello, {name}!";
    }
  }

  class Program {
    static void Main(string[] args) {
      // Intentionally missing documentation
      var g = new Greeter();
      Console.WriteLine(g.Introduce("World"));
    }
  }
}

using System;

namespace Sample {
  public class Greeter {
    public string Introduce(string name) {
      return $"Hello, {name}!";
    }
  }

  class Program {
    static void Main(string[] args) {
      var g = new Greeter();
      Console.WriteLine(g.Introduce("World"));
    }
  }
}

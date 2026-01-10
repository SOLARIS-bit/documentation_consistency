class Greeter {
  introduce(name) {
    // documented in README
    return `Hello, ${name}!`;
  }
}

function add(a, b) {
  // Intentionally missing documentation
  return a + b;
}

module.exports = { Greeter, add };

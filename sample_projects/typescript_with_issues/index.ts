export class Greeter {
  introduce(name: string): string {
    // documented in README
    return `Hello, ${name}!`;
  }
}

export function add(a: number, b: number): number {
  // Intentionally missing documentation
  return a + b;
}

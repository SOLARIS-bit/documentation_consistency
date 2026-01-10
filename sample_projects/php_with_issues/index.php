<?php
class Greeter {
  public function introduce($name) {
    // documented in README
    return "Hello, " . $name . "!";
  }
}

function add($a, $b) {
  // Intentionally missing documentation
  return $a + $b;
}
?>

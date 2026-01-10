package main

import "fmt"

type Calculator struct{}

func (c Calculator) Multiply(a int, b int) int {
    // Intentionally missing documentation
    return a * b
}

func Add(a int, b int) int {
    return a + b
}

func main() {
    fmt.Println(Add(2,3))
}

"""
Math utilities module.
"""

def add(a, b):
    """
    Add two numbers together.
    
    Args:
        a (int or float): First number
        b (int or float): Second number
    
    Returns:
        int or float: Sum of a and b
    """
    return a + b


def subtract(a, b):
    # Intentionally missing docstring
    return a - b


def multiply(a, b):
    # Intentionally missing docstring
    return a * b


def divide(a, b):
    """
    Divide two numbers.
    
    Args:
        a (int or float): Dividend
        b (int or float): Divisor
    
    Returns:
        float: Result of a / b
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

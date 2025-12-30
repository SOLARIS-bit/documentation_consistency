def add(a, b):
    """
    Add two numbers.

    Args:
        a (int or float): First number.
        b (int or float): Second number.

    Returns:
        int or float: Sum of a and b.
    """
    return a + b


def subtract(a, b):
    """
    Subtract two numbers.

    Args:
        a (int or float): First number.
        b (int or float): Second number.

    Returns:
        int or float: Result of a - b.
    """
    return a - b
def multiply(a, b):
    """
    Multiply two numbers.

    Args:
        a (int or float): First number.
        b (int or float): Second number.

    Returns:
        int or float: Product of a and b.
    """
    return a * b
def divide(a, b):
    """
    Divide two numbers.

    Args:
        a (int or float): First number.
        b (int or float): Second number.

    Returns:
        int or float: Result of a / b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b
def power(a, b):
    """
    Raise a to the power of b.

    Args:
        a (int or float): Base.
        b (int or float): Exponent.

    Returns:
        int or float: Result of a raised to the power of b.
    """
    return a ** b
def calculate_rocket_trajectory(speed, angle):
    """Calculates trajectory."""
    return speed * angle / 9.81
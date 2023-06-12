# pylint: disable=invalid-name, missing-docstring
def add_numbers(a, b):
    """Add two numbers."""
    return a + b
result = add_numbers(5, 10)
print(result)

def divide(a: int, b: int) -> int:
    return a / b
result = divide(10, '5')

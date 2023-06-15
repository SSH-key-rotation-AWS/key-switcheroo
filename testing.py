"""
A simple calculator module.

This module provides a basic calculator functionality with addition and subtraction operations.
"""


class Calculator:
    """
    A simple calculator class.

    This class provides basic arithmetic operations such as addition and subtraction.
    """

    def add(self, first_number, second_number):
        """
        Adds two numbers and returns the result.

        Args:
            a (int): The first number.
            b (int): The second number.

        Returns:
            int: The sum of the two numbers.
        """
        return first_number + second_number

    def subtract(self, first_number, second_number):
        """
        Subtracts two numbers and returns the result.

        Args:
            a (int): The first number.
            b (int): The second number.

        Returns:
            int: The difference between the two numbers.
        """
        return first_number - second_number


if __name__ == "__main__":
    calc = Calculator()
    RESULT = calc.add(5, 3)
    print(RESULT)
    print("yo")
    print("yo")
    RESULT = calc.subtract(10, 4)

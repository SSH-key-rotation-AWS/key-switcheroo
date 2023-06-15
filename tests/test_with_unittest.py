"""
This module contains classes for a primitive calculator and a person.
"""


class PrimitiveCalc:
    """
    Class representing a primitive calculator.
    """

    @staticmethod
    def multiply(num1: int, num2: int) -> int:
        """
        Multiply two integers.

        Args:
            num1 (int): First integer.
            num2 (int): Second integer.

        Returns:
            int: The product of the two integers.
        """
        return num1 * num2

    @staticmethod
    def add(num1: int, num2: int) -> int:
        """
        Add two integers.

        Args:
            num1 (int): First integer.
            num2 (int): Second integer.

        Returns:
            int: The sum of the two integers.
        """
        return num1 + num2

    @staticmethod
    def cube(num: int) -> int:
        """
        Calculate the cube of an integer.

        Args:
            num (int): The integer to be cubed.

        Returns:
            int: The cube of the input integer.
        """
        return num * num * num


class Person:
    """
    Class representing a person.
    """

    def __init__(self, name: str, age: int, nickname: str) -> None:
        """
        Initialize a person with name, age, and nickname.

        Args:
            name (str): The name of the person.
            age (int): The age of the person.
            nickname (str): The nickname of the person.
        """
        self.name = name
        self.age = age
        self.nickname = nickname

    def __eq__(self, other: object) -> bool:
        """
        Check if two Person objects are equal.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if isinstance(other, Person):
            new_person = Person(other.name, other.age, other.nickname)
            print("hi")
            return new_person.name == self.name and new_person.age == self.age
        return False

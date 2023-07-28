from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Serializer(ABC, Generic[T]):
    """A Serializer turns an object of type T into a string and back again from a string"""

    @abstractmethod
    def serialize(self, storable: T) -> str:
        """Turn some storable object of type T into a string, such that Serializer:deserialize \
        returns the same object


        Args:
            storable (T): The object to serialize

        Returns:
            str: The serialized object
        """

    @abstractmethod
    def deserialize(self, data_str: str) -> T:
        """Turn some string into an object of type T

        Args:
            data_str (str): The string to deserialize

        Returns:
            T: The deserialized object
        """

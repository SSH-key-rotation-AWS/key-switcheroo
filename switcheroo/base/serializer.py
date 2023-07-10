from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Serializer(ABC, Generic[T]):
    @abstractmethod
    def serialize(self, storable: T) -> str:
        pass

    @abstractmethod
    def deserialize(self, data_str: str) -> T:
        pass

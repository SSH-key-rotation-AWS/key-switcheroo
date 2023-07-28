from dataclasses import dataclass
from switcheroo.base import Serializer

@dataclass
class SomeClass:
    value: str

class SomeClassSerializer(Serializer[SomeClass]):

    def serialize(self, storable: SomeClass) -> str:
        return storable.value

    def deserialize(self, data_str: str) -> SomeClass:
        return SomeClass(data_str)

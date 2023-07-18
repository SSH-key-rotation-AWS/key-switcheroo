from pathlib import Path
from dataclasses import dataclass
from abc import ABC
import json
from switcheroo.base.data_store import Serializer


@dataclass
class Storable(ABC):
    #Storing uuid as a string for easy json serialization
    unique_id: str

    @property
    def relative_loc(self)->Path:
        """Relative location of a person in a storage system


        Returns:
            Path: Relative location of this person in a storage system as a pathlib.Path obj
        """
        return Path(self.unique_id)

@dataclass
class Person(Storable):
    """Dataclass representing a person to be used for testing
    """
    name: str
    age: int
    bio: str

@dataclass
class Figure(Storable):
    shape: str
    color: str
    size: int



class PersonSerializer(Serializer[Person]):
    """Serializer for the Person class - just to/from json
    """

    def serialize(self, storable: Person) -> str:
        return json.dumps(storable.__dict__)

    def deserialize(self, data_str: str) -> Person:
        data_obj =  json.loads(data_str)
        return Person(data_obj["unique_id"], data_obj["name"], data_obj["age"], data_obj["bio"])

class FigureSerializer(Serializer[Figure]):
    """Serializer for the Figure class - just to/from json
    """
    def serialize(self, storable: Figure) -> str:
        return json.dumps(storable.__dict__)

    def deserialize(self, data_str: str) -> Figure:
        data_obj = json.loads(data_str)
        return Figure(data_obj["unique_id"], data_obj["shape"], data_obj["color"], data_obj["size"])

from pathlib import Path
from dataclasses import dataclass, field
import uuid
import json
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from switcheroo.base.data_store import Serializer


def _str_uuid_factory():
    return str(uuid.uuid4())

@dataclass
class Person:
    """Dataclass representing a person to be used for testing
    """
    name: str
    age: int
    bio: str
    #Storing uuid as a string for easy json serialization
    unique_id: str = field(default_factory=_str_uuid_factory)

    @property
    def relative_loc(self)->Path:
        """Relative location of a person in a storage system


        Returns:
            Path: Relative location of this person in a storage system as a pathlib.Path obj
        """
        return Path(self.unique_id)

class PersonSerializer(Serializer[Person]):
    """Serializer for the Person class - just to/from json
    """

    def serialize(self, storable: Person) -> str:
        return json.dumps(storable.__dict__)

    def deserialize(self, data_str: str) -> Person:
        data_obj =  json.loads(data_str)
        return Person(data_obj["name"], data_obj["age"], data_obj["bio"], data_obj["unique_id"])

class HasFileMode(BaseMatcher[Path]):
    """Hamcrest matcher to check the file mode of a given pathlib.Path
    """
    def __init__(self, file_mode: int) -> None:
        """Creates the matcher

        Args:
            file_mode (int): the file mode to check for - the check treats the int as a \
            octal value - ie if 755 is passed in, the matcher looks for the permission 0o755
        """
        super().__init__()
        self._file_mode = file_mode

    def _matches(self, item: Path) -> bool:
        file_mode_str = oct(item.stat().st_mode) #Returns 0o100[mode] as a str
        file_mode = int(file_mode_str[5:]) #Get just [mode]
        return file_mode == self._file_mode

    def describe_to(self, description: Description) -> None:
        description.append_text(f"File mode which is {self._file_mode} in octal") \
                   .append_text(f"(0o{self._file_mode})")

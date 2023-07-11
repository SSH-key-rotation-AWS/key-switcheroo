from dataclasses import dataclass, field
import json
from getpass import getuser
from typing import IO, ClassVar
from datetime import datetime
from Crypto.PublicKey import RSA
from switcheroo.base import Serializer


class Key:  # pylint: disable=too-few-public-methods
    class PrivateComponent:
        def __init__(self, byte_data: bytes):
            self.byte_data = byte_data

    class PublicComponent:
        def __init__(self, byte_data: bytes):
            self.byte_data = byte_data

    def __init__(self, key_tuple: tuple[bytes, bytes] | None = None) -> None:
        super().__init__()
        if key_tuple is None:
            key_tuple = KeyGen.generate_private_public_key()
        self.private_key: Key.PrivateComponent = Key.PrivateComponent(key_tuple[0])
        self.public_key: Key.PublicComponent = Key.PublicComponent(key_tuple[1])


class PrivateKeySerializer(Serializer[Key.PrivateComponent]):
    def serialize(self, storable: Key.PrivateComponent) -> str:
        return storable.byte_data.decode()

    def deserialize(self, data_str: str) -> Key.PrivateComponent:
        return Key.PrivateComponent(data_str.encode())


class PublicKeySerializer(Serializer[Key.PublicComponent]):
    def serialize(self, storable: Key.PublicComponent) -> str:
        return storable.byte_data.decode()

    def deserialize(self, data_str: str) -> Key.PublicComponent:
        return Key.PublicComponent(data_str.encode())


class KeyGen:
    PRIVATE_KEY_NAME: str = "key"
    PUBLIC_KEY_NAME: str = f"{PRIVATE_KEY_NAME}-cert.pub"
    KEY_SIZE_BITS = 2048

    @classmethod
    def generate_private_public_key(cls) -> tuple[bytes, bytes]:
        "Generates a private and public RSA key"
        key = RSA.generate(cls.KEY_SIZE_BITS)
        private_key = key.export_key()
        public_key = key.public_key().export_key(format="OpenSSH")
        return private_key, public_key


@dataclass(frozen=True)
class KeyMetadata:
    FILE_NAME: ClassVar[str] = "metadata.json"
    created_by: str
    time_generated: datetime = field(default_factory=datetime.now)

    @classmethod
    def now(cls, created_by: str | None):
        """Returns a new metadata object

        Create a new key metadata, using now as the creation time

        Args:
            created_by (str): The user that created this key. Not required.
        """
        if created_by is None:
            created_by = ""
        return KeyMetadata(created_by=created_by, time_generated=datetime.now())

    @classmethod
    def now_by_executing_user(cls):
        """Returns a new metadata object
        
        Create a new key metadata, using now as the creation time and the current\
        executing user for the created_by field"""
        return KeyMetadata.now(created_by=getuser())

    def _get_serialized_obj(self):
        return {
            "time_generated": str(self.time_generated),
            "created_by": self.created_by,
        }

    def serialize(self, target: IO[str]):
        """
        Dump the key metadata into the provided target

        Args:
            target (IO[str]): Where to dump the data in JSON format
        """
        json.dump(
            self._get_serialized_obj(),
            target,
        )

    def serialize_to_string(self):
        """
        Serializes the key metadata to a JSON string that can later be parsed with from_io
        """
        return json.dumps(self._get_serialized_obj())

    @classmethod
    def from_io(cls, source: IO[str]):
        """Returns the parsed KeyMetadata

        Parse and return the KeyMetadata from the provided source

        Args:
            source (IO[str]): Where to get the JSON from
        Returns:
            metadata (KeyMetadata): The key metadata
        """
        return cls.from_string(source.read())

    @classmethod
    def from_string(cls, source: str):
        """Returns the parsed KeyMetadata

        Parse and return the KeyMetadata from the provided string source

        Args:
            source (str): The JSON in a string
        Returns:
            metadata (KeyMetadata): The key metadata
        """
        json_obj = json.loads(source)
        time_generated = datetime.strptime(
            json_obj["time_generated"], "%Y-%m-%d %H:%M:%S.%f"
        )
        created_by = json_obj["created_by"]
        return KeyMetadata(created_by, time_generated)


class KeyMetadataSerializer(Serializer[KeyMetadata]):
    def serialize(self, storable: KeyMetadata) -> str:
        return storable.serialize_to_string()

    def deserialize(self, data_str: str) -> KeyMetadata:
        return KeyMetadata.from_string(data_str)

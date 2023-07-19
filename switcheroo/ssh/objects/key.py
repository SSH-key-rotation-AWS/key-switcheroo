from dataclasses import dataclass, field
import json
from getpass import getuser
from typing import IO, ClassVar, Self
from datetime import datetime
from Crypto.PublicKey import RSA
from switcheroo.base import Serializer


class Key:  # pylint: disable=too-few-public-methods
    """Enclosing object for a public key and corresponding private key"""

    class PrivateComponent:
        def __init__(self, byte_data: bytes):
            self.byte_data = byte_data

    class PublicComponent:
        def __init__(self, byte_data: bytes):
            self.byte_data = byte_data

    def __init__(self, key_tuple: tuple[bytes, bytes] | None = None) -> None:
        """Initialize the Key instance

        Args:
            key_tuple (tuple[bytes, bytes] | None, optional): The key byte data as \
            (private key, public key). If no data is passed in, a new key is generated. \
            Defaults to None.
        """
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
    """Information about a key - who created it, and when it was generated"""

    FILE_NAME: ClassVar[str] = "metadata.json"
    created_by: str
    time_generated: datetime = field(default_factory=datetime.now)

    @classmethod
    def now(cls, created_by: str = "") -> Self:
        """Create a new KeyMetadata object, using now as the current time.

        Args:
            created_by (str): Who created the key. Defaults to empty.

        Returns:
            KeyMetadata: A new KeyMetadata instance with the provided information
        """
        return KeyMetadata(created_by=created_by, time_generated=datetime.now())

    @classmethod
    def now_by_executing_user(cls) -> Self:
        """Create a new KeyMetadata object, using now as the current time and the \
        executing user (called with getpass.getuser()) as the creator.

        Returns:
            KeyMetadata: A new KeyMetadata instance
        """
        return KeyMetadata.now(created_by=getuser())

    def _get_serialized_obj(self):
        return {
            "time_generated": str(self.time_generated),
            "created_by": self.created_by,
        }

    def serialize(self, target: IO[str]):
        """Dumps the key metadata into the provided target in JSON format

        Args:
            target (IO[str]): Where to dump the information
        """
        json.dump(
            self._get_serialized_obj(),
            target,
        )

    def serialize_to_string(self) -> str:
        """Serializes this object into a JSON-formatted string.

        Returns:
            str: The JSON-formatted representation of this string.
        """
        return json.dumps(self._get_serialized_obj())

    @classmethod
    def from_io(cls, source: IO[str]) -> Self:
        """Parses and return the KeyMetadata from the provided source

        Args:
            source (IO[str]): Where to get the JSON from

        Returns:
            KeyMetadata: The key metadata
        """
        return cls.from_string(source.read())

    @classmethod
    def from_string(cls, source: str) -> Self:
        """Parse and return the KeyMetadata from the provided string source

        Args:
            source (str): The JSON in a string

        Returns:
            KeyMetadata: The key metadata
        """
        json_obj = json.loads(source)
        time_generated = datetime.strptime(
            json_obj["time_generated"], "%Y-%m-%d %H:%M:%S.%f"
        )
        created_by = json_obj["created_by"]
        return KeyMetadata(created_by, time_generated)


class KeyMetadataSerializer(Serializer[KeyMetadata]):
    """A Serializer for KeyMetadata, to be used by a DataStore."""

    def serialize(self, storable: KeyMetadata) -> str:
        """See base class."""
        return storable.serialize_to_string()

    def deserialize(self, data_str: str) -> KeyMetadata:
        """See base class."""
        return KeyMetadata.from_string(data_str)

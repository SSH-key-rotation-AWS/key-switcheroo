from abc import ABC, abstractmethod
from ssh_key_rotator.custom_keygen import generate_private_public_key_in_file


class Publisher(ABC):
    """Abstract key publisher base class"""

    @abstractmethod
    def publish_new_key(self) -> str:
        """Abstract method for publishing a new public key"""

    @abstractmethod
    def rotate_keys(self):
        """Abstract method for rotating public keys"""


class S3Publisher(Publisher):
    """S3 Publisher class"""

    def publish_new_key(self) -> str:
        return ""

    def rotate_keys(self):
        pass


class LocalPublisher(Publisher):
    """Local Publisher class"""

    def publish_new_key(self) -> str:
        _, public_key = generate_private_public_key_in_file("~/.ssh/authorized_keys")
        return public_key.decode()

    def rotate_keys(self):
        pass

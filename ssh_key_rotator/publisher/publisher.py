from abc import ABC, abstractmethod
from custom_keygen import generate_private_public_key_in_file


class Publisher(ABC):
    @abstractmethod
    def publish_new_key(self):
        pass


class S3Publisher(Publisher):
    def publish_new_key(self):
        pass


class LocalPublisher(Publisher):
    def publish_new_key(self):
        generate_private_public_key_in_file()

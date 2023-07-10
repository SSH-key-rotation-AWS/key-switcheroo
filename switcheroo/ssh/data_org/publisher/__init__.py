from abc import ABC, abstractmethod
from pathlib import Path
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.data_stores import ssh_home_file_ds
from switcheroo import paths


class KeyPublisher(ABC):
    @abstractmethod
    def publish_public_key(self, key: Key.PublicComponent, host: str, user: str):
        pass

    @abstractmethod
    def publish_private_key(self, key: Key.PrivateComponent, host: str, user: str):
        pass

    @abstractmethod
    def publish_key_metadata(self, metadata: KeyMetadata, host: str, user: str):
        pass

    def publish_key(
        self,
        host: str,
        user: str,
        key: Key | None = None,
        metadata: KeyMetadata | None = None,
    ):
        # Lazy evaluation of default values
        if key is None:
            key = Key()
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        self.publish_public_key(key.public_key, host, user)
        self.publish_private_key(key.private_key, host, user)
        self.publish_key_metadata(metadata, host, user)


class FileKeyPublisher(KeyPublisher):
    def __init__(self, ssh_home: Path = paths.local_ssh_home()):
        self._ssh_home = ssh_home
        self._file_ds = ssh_home_file_ds(ssh_home)

    def publish_public_key(self, key: Key.PublicComponent, host: str, user: str):
        return self._file_ds.publish(
            item=key, location=paths.local_relative_public_key_loc(host, user)
        )

    def publish_private_key(self, key: Key.PrivateComponent, host: str, user: str):
        return self._file_ds.publish(
            item=key, location=paths.local_relative_private_key_loc(host, user)
        )

    def publish_key_metadata(self, metadata: KeyMetadata, host: str, user: str):
        return self._file_ds.publish(
            item=metadata, location=paths.local_relative_metadata_loc(host, user)
        )

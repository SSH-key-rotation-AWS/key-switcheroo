from abc import ABC, abstractmethod
from pathlib import Path
from switcheroo.base.data_store import FileDataStore
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.data_stores import sshify
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
        self, key: Key, host: str, user: str, metadata: KeyMetadata | None = None
    ):
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        self.publish_public_key(key.public_key, host, user)
        self.publish_private_key(key.private_key, host, user)
        self.publish_key_metadata(metadata, host, user)


class FileKeyPublisher(KeyPublisher):
    def __init__(self, ssh_home: Path):
        self._ssh_home = ssh_home
        self._file_ds = sshify(FileDataStore(ssh_home))

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

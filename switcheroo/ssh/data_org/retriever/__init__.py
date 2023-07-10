from abc import abstractmethod
from pathlib import Path
from switcheroo.base.data_store import FileDataStore
from switcheroo.ssh.data_stores import sshify
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh import AuthorizedKeysCmndProvider
from switcheroo import paths


class KeyRetriever(AuthorizedKeysCmndProvider):
    @abstractmethod
    def retrieve_private_key(self, host: str, user: str) -> Key.PrivateComponent:
        pass

    @abstractmethod
    def retrieve_public_key(self, host: str, user: str) -> Key.PublicComponent:
        pass

    @abstractmethod
    def retrieve_key_metadata(self, host: str, user: str) -> KeyMetadata:
        pass

    def retrieve_key(self, host: str, user: str) -> tuple[Key, KeyMetadata]:
        key = Key(
            (
                self.retrieve_private_key(host, user).byte_data,
                self.retrieve_public_key(host, user).byte_data,
            )
        )
        metadata = self.retrieve_key_metadata(host, user)
        return (key, metadata)


class FileKeyRetriever(KeyRetriever):
    def __init__(self, key_dir: Path) -> None:
        super().__init__()
        self._key_dir = key_dir
        self._file_ds = sshify(FileDataStore(key_dir))

    def retrieve_public_key(self, host: str, user: str) -> Key.PublicComponent:
        return self._file_ds.retrieve(
            location=paths.local_relative_public_key_loc(host, user),
            clas=Key.PublicComponent,
        )

    def retrieve_private_key(self, host: str, user: str) -> Key.PrivateComponent:
        return self._file_ds.retrieve(
            location=paths.local_relative_private_key_loc(host, user),
            clas=Key.PrivateComponent,
        )

    def retrieve_key_metadata(self, host: str, user: str) -> KeyMetadata:
        return self._file_ds.retrieve(
            location=paths.local_relative_metadata_loc(host, user), clas=KeyMetadata
        )

    @property
    def command(self) -> str:
        return f'-ds local --sshdir "{str(self._key_dir)}"'

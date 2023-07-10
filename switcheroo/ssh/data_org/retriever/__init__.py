from abc import abstractmethod
from typing import TypeVar
from pathlib import Path
from switcheroo.base.data_store import DataStore
from switcheroo.ssh.data_stores import ssh_home_file_ds
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.exceptions import SSHItem, SSHItemNotFoundException
from switcheroo.ssh import AuthorizedKeysCmndProvider
from switcheroo import paths

T = TypeVar("T")


def retrieve_or_throw(  # pylint: disable=too-many-arguments
    data_store: DataStore,
    location: Path,
    clas: type[T],
    ssh_item: SSHItem,
    user: str,
    host: str,
) -> T:
    result = data_store.retrieve(location, clas)
    if result is None:
        raise SSHItemNotFoundException(
            SSHItemNotFoundException.Data(
                requested_user=user, requested_host=host, requested_item=ssh_item
            )
        )
    return result


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
        self._key_datastore = ssh_home_file_ds(key_dir)

    def retrieve_public_key(self, host: str, user: str) -> Key.PublicComponent:
        return retrieve_or_throw(
            self._key_datastore,
            location=paths.local_relative_public_key_loc(host, user),
            clas=Key.PublicComponent,
            ssh_item="public key",
            host=host,
            user=user,
        )

    def retrieve_private_key(self, host: str, user: str) -> Key.PrivateComponent:
        return retrieve_or_throw(
            self._key_datastore,
            location=paths.local_relative_private_key_loc(host, user),
            clas=Key.PrivateComponent,
            ssh_item="private key",
            host=host,
            user=user,
        )

    def retrieve_key_metadata(self, host: str, user: str) -> KeyMetadata:
        return retrieve_or_throw(
            self._key_datastore,
            location=paths.local_relative_metadata_loc(host, user),
            clas=KeyMetadata,
            ssh_item="metadata",
            host=host,
            user=user,
        )

    @property
    def command(self) -> str:
        return f'-ds local --sshdir "{str(self._key_dir)}"'

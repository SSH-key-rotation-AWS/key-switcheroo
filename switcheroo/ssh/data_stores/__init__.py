from pathlib import Path
from typing import TypeVar
from switcheroo.base.data_store import DataStore, FileDataStore
from switcheroo.ssh.objects import (
    Key,
    KeyMetadata,
    PublicKeySerializer,
    PrivateKeySerializer,
    KeyMetadataSerializer,
)

T = TypeVar("T", bound=DataStore)


def sshify(data_store: T) -> T:
    """Registers all the serializers to have a datastore store ssh things

    Args:
        data_store (T): The datastore to register

    Returns:
        T: the datastore
    """
    data_store.register_serializer(Key.PrivateComponent, PrivateKeySerializer())
    data_store.register_serializer(Key.PublicComponent, PublicKeySerializer())
    data_store.register_serializer(KeyMetadata, KeyMetadataSerializer())
    if isinstance(data_store, FileDataStore):
        # Private keys require this file permission
        data_store.register_file_permissions(
            Key.PrivateComponent, FileDataStore.FilePermissions(0o600)
        )
    return data_store


def ssh_home_file_ds(root_dir: Path) -> FileDataStore:
    """Return a FileDataStore with it's root having private permissions - needed for ssh to work

    Args:
        root_dir (Path): The path to the root directory

    Returns:
        FileDataStore: The FileDataStore, rooted at the root argument
    """
    ssh_file_ds = FileDataStore(FileDataStore.RootInfo(location=root_dir, mode=0o755))
    return sshify(ssh_file_ds)

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
    data_store.register_serializer(Key.PrivateComponent, PrivateKeySerializer())
    data_store.register_serializer(Key.PublicComponent, PublicKeySerializer())
    data_store.register_serializer(KeyMetadata, KeyMetadataSerializer())
    if isinstance(data_store, FileDataStore):
        data_store.register_file_permissions(
            Key.PrivateComponent, FileDataStore.FilePermissions(0o600)
        )
    return data_store


def ssh_home_file_ds(root_dir: Path) -> FileDataStore:
    ssh_file_ds = FileDataStore(FileDataStore.RootInfo(location=root_dir, mode=0o755))
    return sshify(ssh_file_ds)

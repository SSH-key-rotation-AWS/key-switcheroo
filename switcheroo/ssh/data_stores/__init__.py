from switcheroo.base.data_store import DataStore, FileDataStore
from switcheroo.ssh.objects import (
    Key,
    KeyMetadata,
    PublicKeySerializer,
    PrivateKeySerializer,
    KeyMetadataSerializer,
)


def sshify(data_store: DataStore) -> DataStore:
    data_store.register_serializer(Key.PrivateComponent, PrivateKeySerializer())
    data_store.register_serializer(Key.PublicComponent, PublicKeySerializer())
    data_store.register_serializer(KeyMetadata, KeyMetadataSerializer())
    if isinstance(data_store, FileDataStore):
        data_store.register_file_permissions(
            Key.PrivateComponent, FileDataStore.FilePermissions(0o600)
        )
    return data_store

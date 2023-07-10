from switcheroo.base.data_store import DataStore
from switcheroo.ssh.objects import (
    Key,
    KeyMetadata,
    KeySerializer,
    KeyMetadataSerializer,
)


def sshify(data_store: DataStore) -> DataStore:
    data_store.register_serializer(Key.Component, KeySerializer())
    data_store.register_serializer(KeyMetadata, KeyMetadataSerializer())
    return data_store

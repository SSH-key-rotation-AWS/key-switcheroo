from abc import ABC, abstractmethod
from switcheroo.custom_keygen import KeyMetadata
from switcheroo.data_stores import FileSystemDataStore, DataStore, S3DataStore


class Publisher(ABC):
    """Abstract key publisher base class"""

    def __init__(self, host: str, user: str):
        self._host = host
        self._user = user

    @property
    def host(self) -> str:
        "The host under which to publish the key"
        return self._host

    @property
    def user_id(self) -> str:
        "The user under which to publish the key"
        return self._user

    @abstractmethod
    def _create_publishing_datastore(self) -> DataStore:
        "Returns a datastore that will be used to publish keys"

    def publish_new_key(self, data_store: DataStore | None = None) -> str:
        """Publishes a new key using the given datastore"""
        if data_store is None:
            data_store = self._create_publishing_datastore()
        return data_store.publish(self.host, self.user_id)

    def publish_new_key_with_metadata(
        self,
        data_store: DataStore | None = None,
        key_metadata: KeyMetadata | None = None,
    ) -> tuple[str, KeyMetadata]:
        "Publishes a new key with metadata using the given datastore"
        if data_store is None:
            data_store = self._create_publishing_datastore()
        return data_store.publish_with_metadata(
            self.host, self.user_id, metadata=key_metadata
        )


class S3Publisher(Publisher):
    """S3 Publisher class"""

    def __init__(self, bucket_name: str, host: str, user_id: str):
        super().__init__(host, user_id)
        self.bucket_name = bucket_name

    def _create_publishing_datastore(self) -> DataStore:
        return S3DataStore(self.bucket_name)


class LocalPublisher(Publisher):
    """Local Publisher class"""

    def _create_publishing_datastore(self) -> DataStore:
        return FileSystemDataStore(None)

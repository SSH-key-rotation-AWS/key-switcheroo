from pathlib import Path
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.base.data_store import FileDataStore
from switcheroo.base.data_store.s3 import S3DataStore
from switcheroo.ssh.data_stores import sshify
from switcheroo.ssh.data_org.publisher import KeyPublisher
from switcheroo import paths


class S3Publisher(KeyPublisher):
    def __init__(
        self, s3_bucket_name: str, root_ssh_dir: Path = paths.local_ssh_home()
    ):
        self._s3_bucket_name = s3_bucket_name
        self._file_ds = sshify(FileDataStore(root_ssh_dir))
        self._s3_ds = sshify(S3DataStore(s3_bucket_name))

    def publish_public_key(self, key: Key.Component, host: str, user: str):
        return self._s3_ds.publish(
            item=key, location=paths.cloud_public_key_loc(host, user)
        )

    def publish_private_key(self, key: Key.Component, host: str, user: str):
        return self._file_ds.publish(
            item=key, location=paths.local_relative_private_key_loc(host, user)
        )

    def publish_key_metadata(self, metadata: KeyMetadata, host: str, user: str):
        return self._s3_ds.publish(
            item=metadata, location=paths.cloud_metadata_loc(host, user)
        )

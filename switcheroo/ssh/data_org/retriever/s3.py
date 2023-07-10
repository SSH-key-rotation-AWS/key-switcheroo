from pathlib import Path
from switcheroo.base.data_store import FileDataStore
from switcheroo.base.data_store.s3 import S3DataStore
from switcheroo.ssh.data_org.retriever import KeyRetriever
from switcheroo.ssh.data_stores import sshify
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo import paths


class S3Retriever(KeyRetriever):
    def __init__(self, ssh_local_dir: Path, bucket_name: str) -> None:
        self._bucket_name = bucket_name
        self._ssh_local_dir = ssh_local_dir
        self._file_ds = sshify(FileDataStore(ssh_local_dir))
        self._s3_ds = sshify(S3DataStore(bucket_name))

    def retrieve_public_key(self, host: str, user: str) -> Key.Component:
        return self._s3_ds.retrieve(
            location=paths.cloud_public_key_loc(host, user), clas=Key.Component
        )

    def retrieve_private_key(self, host: str, user: str) -> Key.Component:
        return self._file_ds.retrieve(
            location=paths.local_private_key_loc(host, user, self._ssh_local_dir),
            clas=Key.Component,
        )

    def retrieve_key_metadata(self, host: str, user: str) -> KeyMetadata:
        return self._s3_ds.retrieve(
            location=paths.cloud_metadata_loc(host, user), clas=KeyMetadata
        )

    @property
    def command(self) -> str:
        return f"-ds s3 --bucket {self._bucket_name}"

from pathlib import Path
from switcheroo.base.data_store.s3 import S3DataStore
from switcheroo.ssh.data_org.retriever import KeyRetriever
from switcheroo.ssh.data_stores import sshify, ssh_home_file_ds
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.data_org.retriever import retrieve_or_throw
from switcheroo import paths


class S3Retriever(KeyRetriever):
    def __init__(self, ssh_local_dir: Path, bucket_name: str) -> None:
        self._bucket_name = bucket_name
        self._ssh_local_dir = ssh_local_dir
        self._file_ds = ssh_home_file_ds(ssh_local_dir)
        self._s3_ds = sshify(S3DataStore(bucket_name))

    def retrieve_public_key(self, host: str, user: str) -> Key.PublicComponent:
        return retrieve_or_throw(
            self._s3_ds,
            location=paths.cloud_public_key_loc(host, user),
            clas=Key.PublicComponent,
            ssh_item="public key",
            user=user,
            host=host,
        )

    def retrieve_private_key(self, host: str, user: str) -> Key.PrivateComponent:
        return retrieve_or_throw(
            self._file_ds,
            location=paths.local_private_key_loc(host, user, self._ssh_local_dir),
            clas=Key.PrivateComponent,
            ssh_item="private key",
            user=user,
            host=host,
        )

    def retrieve_key_metadata(self, host: str, user: str) -> KeyMetadata:
        return retrieve_or_throw(
            self._s3_ds,
            location=paths.cloud_metadata_loc(host, user),
            clas=KeyMetadata,
            ssh_item="metadata",
            user=user,
            host=host,
        )

    @property
    def command(self) -> str:
        return f"-ds s3 --bucket {self._bucket_name}"

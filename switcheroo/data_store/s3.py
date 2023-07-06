from pathlib import Path
import boto3
from switcheroo.data_store import DataStore
from switcheroo import paths
from switcheroo.custom_keygen import KeyGen, KeyMetadata


class S3DataStore(DataStore):
    "Store the public keys in an S3 bucket"

    def __init__(
        self, _s3_bucket_name: str, ssh_home: Path | None = None, temp: bool = False
    ):
        super().__init__(ssh_home=ssh_home, temp=temp)
        self._s3_bucket_name = _s3_bucket_name
        self._s3_client = boto3.client("s3")

    @property
    def s3_bucket_name(self):
        "The name of the bucket in which the keys are stored"
        return self._s3_bucket_name

    def get_sshd_config_line(self) -> str:
        return f"s3 {self.s3_bucket_name}"

    def retrieve(self, host: str, user: str):
        response = self._s3_client.get_object(
            Bucket=self.s3_bucket_name, Key=str(paths.cloud_public_key_loc(host, user))
        )
        ssh_key = response["Body"].read().decode()
        return ssh_key

    def publish(self, host: str, user: str) -> str:
        # Generate new public/private key pair
        private_key, public_key = KeyGen.generate_private_public_key()
        # Store the new public key in S3 bucket
        self._s3_client.put_object(
            Body=public_key,
            Bucket=self.s3_bucket_name,
            Key=str(paths.cloud_public_key_loc(host, user)),
        )

        # Store the private key on the local machine
        KeyGen.store_private_key(
            private_key=private_key,
            private_key_dir=paths.local_key_dir(host, user, home_dir=self.home_dir),
        )

        return public_key.decode()

    def publish_with_metadata(
        self, host: str, user: str, metadata: KeyMetadata | None
    ) -> tuple[str, KeyMetadata]:
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish(host, user)
        # Store the metadata in the same folder - metadata.json
        self._s3_client.put_object(
            Body=metadata.serialize_to_string(),
            Bucket=self.s3_bucket_name,
            Key=str(paths.cloud_metadata_loc(host, user)),
        )
        return public_key, metadata

    def __exit__(self, exc_t, exc_v, exc_tb):
        super().__exit__(None, None, None)
        if self._temp:
            objects = self._s3_client.list_objects_v2(Bucket=self.s3_bucket_name)[
                "Contents"
            ]
            delete_objects = [{"Key": bucket_obj["Key"]} for bucket_obj in objects]  # type: ignore
            self._s3_client.delete_objects(
                Bucket=self.s3_bucket_name,
                Delete={"Objects": delete_objects},  # type: ignore
            )

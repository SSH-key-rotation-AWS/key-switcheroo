"Data stores that specifies where a Server stores its keys"
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
import boto3
from switcheroo import paths
from switcheroo.custom_keygen import KeyGen, KeyMetadata


class DataStore(ABC):
    "A server uses a DataStore to get public keys from somewhere."

    def __init__(self, ssh_home: Path | None = None, temp: bool = False):
        # If temp is true, will reset the home_dir to a temp file upon usage as a context manager
        self.temp = temp
        # ssh_home is only relevant if not being used as a context manager
        self._dir: Path = paths.local_ssh_home() if ssh_home is None else ssh_home
        # To be used later if we decide to use this as a context manager, and temp is selected
        self._temp_dir: TemporaryDirectory[str] | None = None

    @property
    def home_dir(self) -> Path:
        """The folder where local files are stored"""
        if self.temp and self._temp_dir is not None:
            return Path(self._temp_dir.name)
        return self._dir

    @abstractmethod
    def get_sshd_config_line(self):
        "Return the config line that the server will add to the sshd_config"

    @abstractmethod
    def publish(self, host: str, user: str) -> str:
        """Publish a new public key for the given host and user"""

    @abstractmethod
    def publish_with_metadata(
        self, host: str, user: str, metadata: KeyMetadata | None
    ) -> tuple[str, KeyMetadata]:
        """Publish a new public key for the given host and user with metadata"""

    @abstractmethod
    def retrieve(self, host: str, user: str) -> str:
        """Retrieve the public key for the given host and user"""

    def __enter__(self):
        if self.temp:
            self._temp_dir: TemporaryDirectory[str] | None = TemporaryDirectory[
                str
            ](  # pylint: disable=consider-using-with
                prefix="ssh-keys-", dir=self._dir
            )

    def __exit__(self, exc_t, exc_v, exc_tb):
        if self.temp:
            assert self._temp_dir is not None
            self._temp_dir.__exit__(None, None, None)


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
        if self.temp:
            objects = self._s3_client.list_objects_v2(Bucket=self.s3_bucket_name)[
                "Contents"
            ]
            delete_objects = [{"Key": bucket_obj["Key"]} for bucket_obj in objects]  # type: ignore
            self._s3_client.delete_objects(
                Bucket=self.s3_bucket_name,
                Delete={"Objects": delete_objects},  # type: ignore
            )


class FileSystemDataStore(DataStore):
    "Stores keys in a file system"

    def get_sshd_config_line(self) -> str:
        return f"local {str(self.home_dir)}"

    def publish(self, host: str, user: str) -> str:
        _, public_key = KeyGen.generate_private_public_key_in_file(
            paths.local_key_dir(host, user, home_dir=self.home_dir)
        )
        return public_key.decode()

    def publish_with_metadata(
        self, host: str, user: str, metadata: KeyMetadata | None = None
    ) -> tuple[str, KeyMetadata]:
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish(host, user)
        metadata_file = paths.local_metadata_loc(host, user, home_dir=self.home_dir)
        with open(metadata_file, encoding="utf-8", mode="wt") as metadata_file:
            metadata.serialize(metadata_file)
        return public_key, metadata

    def retrieve(self, host: str, user: str) -> str:
        key_path = paths.local_public_key_loc(host, user, home_dir=self.home_dir)
        if not key_path.exists():
            return ""
        with open(key_path, mode="rt", encoding="utf-8") as key_file:
            return key_file.read()

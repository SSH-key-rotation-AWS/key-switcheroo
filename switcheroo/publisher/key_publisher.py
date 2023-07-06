from abc import ABC, abstractmethod
import os
from pathlib import Path
import shutil
import boto3
from switcheroo.custom_keygen import KeyGen, KeyMetadata
from switcheroo.util import get_user_path, get_username


def _ensure_ssh_home_exists():
    ssh_home = f"{get_user_path()}/.ssh"
    if not os.path.isdir(ssh_home):
        os.makedirs(ssh_home)


class Publisher(ABC):
    """Abstract key publisher base class"""

    @property
    @abstractmethod
    def publishing_location(self) -> Path:
        "Returns the location of where the directory the key will be in is, relative to the root"

    @abstractmethod
    def publish_new_key(self) -> str:
        """Abstract method for publishing a new public key"""

    @abstractmethod
    def publish_new_key_with_metadata(
        self, key_metadata: KeyMetadata | None
    ) -> tuple[str, KeyMetadata]:
        """Abstract method for publishing a new public key with metadata
        If no metadata is passed in, default metadata should be provided
        """


class S3Publisher(Publisher):
    """S3 Publisher class"""

    def __init__(self, bucket_name: str, host: str, user_id: str):
        self.bucket_name = bucket_name
        self.host = host
        self.user_id = user_id

    @property
    def publishing_location(self) -> Path:
        return Path(self.host) / self.user_id

    def publish_new_key(self) -> str:
        # Generate new public/private key pair
        private_key, public_key = KeyGen.generate_private_public_key()
        _ensure_ssh_home_exists()
        # Store the new public key in S3 bucket
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Body=public_key,
            Bucket=self.bucket_name,
            Key=str(self.publishing_location / KeyGen.PUBLIC_KEY_NAME),
        )

        # Store the private key on the local machine
        private_key_dir = f"{get_user_path()}/.ssh/{self.host}/{self.user_id}"
        if not os.path.isdir(private_key_dir):
            os.makedirs(private_key_dir)
        private_key_path = f"{private_key_dir}/{KeyGen.PRIVATE_KEY_NAME}"
        with open(private_key_path, "wb") as private_out:
            private_out.write(private_key)
        shutil.chown(private_key_path, user=get_username(), group=-1)
        os.chmod(private_key_path, 0o600)

        return public_key.decode()

    def publish_new_key_with_metadata(
        self, key_metadata: KeyMetadata | None = None
    ) -> tuple[str, KeyMetadata]:
        if key_metadata is None:
            key_metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish_new_key()
        s3_client = boto3.client("s3")
        # Store the metadata in the same folder - metadata.json
        s3_client.put_object(
            Body=key_metadata.serialize_to_string(),
            Bucket=self.bucket_name,
            Key=str(self.publishing_location / KeyMetadata.FILE_NAME),
        )
        return public_key, key_metadata


class LocalPublisher(Publisher):
    """Local Publisher class"""

    def __init__(self, host: str, user_id: str):
        self.host = host
        self.user_id = user_id

    @property
    def publishing_location(self) -> Path:
        return Path(get_user_path()) / ".ssh" / self.host / self.user_id

    def publish_new_key(self) -> str:
        _ensure_ssh_home_exists()
        _, public_key = KeyGen.generate_private_public_key_in_file(
            str(self.publishing_location),
            private_key_name=KeyGen.PRIVATE_KEY_NAME,
            public_key_name=KeyGen.PUBLIC_KEY_NAME,
        )
        return public_key.decode()

    def publish_new_key_with_metadata(
        self, key_metadata: KeyMetadata | None = None
    ) -> tuple[str, KeyMetadata]:
        if key_metadata is None:
            key_metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish_new_key()
        metadata_file = str(self.publishing_location / KeyMetadata.FILE_NAME)
        with open(metadata_file, encoding="utf-8", mode="wt") as metadata_file:
            key_metadata.serialize(metadata_file)
        return public_key, key_metadata

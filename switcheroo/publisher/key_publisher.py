from abc import ABC, abstractmethod
import os
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

    @abstractmethod
    def publish_new_key(self) -> str:
        """Abstract method for publishing a new public key"""

    @abstractmethod
    def publish_new_key_with_metadata(self, key_metadata: KeyMetadata | None) -> str:
        """Abstract method for publishing a new public key with metadata
        If no metadata is passed in, default metadata should be provided
        """


class S3Publisher(Publisher):
    """S3 Publisher class"""

    def __init__(self, bucket_name: str, host: str, user_id: str):
        self.bucket_name = bucket_name
        self.host = host
        self.user_id = user_id

    def publish_new_key(self) -> str:
        # Generate new public/private key pair
        private_key, public_key = KeyGen.generate_private_public_key()
        _ensure_ssh_home_exists()
        # Store the new public key in S3 bucket
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Body=public_key,
            Bucket=self.bucket_name,
            Key=f"{self.host}/{self.user_id}/{KeyGen.PUBLIC_KEY_NAME}",
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

    def publish_new_key_with_metadata(self, key_metadata: KeyMetadata | None) -> str:
        if key_metadata is None:
            key_metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish_new_key()
        s3_client = boto3.client("s3")
        # Store the metadata in the same folder - metadata.json
        s3_client.put_object(
            Body=key_metadata.serialize_to_string(),
            Bucket=self.bucket_name,
            Key=f"{self.host}/{self.user_id}/{KeyMetadata.FILE_NAME}",
        )
        return public_key


class LocalPublisher(Publisher):
    """Local Publisher class"""

    def __init__(self, host: str, user_id: str):
        self.host = host
        self.user_id = user_id

    def publish_new_key(self) -> str:
        user_path = get_user_path()
        _ensure_ssh_home_exists()
        _, public_key = KeyGen.generate_private_public_key_in_file(
            f"{user_path}/.ssh/{self.host}/{self.user_id}",
            private_key_name=KeyGen.PRIVATE_KEY_NAME,
            public_key_name=KeyGen.PUBLIC_KEY_NAME,
        )
        return public_key.decode()

    def publish_new_key_with_metadata(self, key_metadata: KeyMetadata | None) -> str:
        if key_metadata is None:
            key_metadata = KeyMetadata.now_by_executing_user()
        # Publish the key
        public_key = self.publish_new_key()
        metadata_file = (
            f"{get_user_path()}/.ssh/{self.host}/{self.user_id}/{KeyMetadata.FILE_NAME}"
        )
        with open(metadata_file, encoding="utf-8", mode="wt") as metadata_file:
            key_metadata.serialize(metadata_file)
        return public_key

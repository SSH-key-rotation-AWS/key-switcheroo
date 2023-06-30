from abc import ABC, abstractmethod
import os
import shutil
import boto3
from ssh_key_rotator.custom_keygen import (
    generate_private_public_key_in_file,
    generate_private_public_key,
)
from ssh_key_rotator.util import get_user_path, get_username


def _ensure_ssh_home_exists():
    ssh_home = f"{get_user_path()}/.ssh"
    if not os.path.isdir(ssh_home):
        os.makedirs(ssh_home)


class Publisher(ABC):
    """Abstract key publisher base class"""

    @abstractmethod
    def publish_new_key(self) -> str:
        """Abstract method for publishing a new public key"""


class S3Publisher(Publisher):
    """S3 Publisher class"""

    def __init__(self, bucket_name: str, host: str, user_id: str):
        self.bucket_name = bucket_name
        self.host = host
        self.user_id = user_id

    def publish_new_key(self) -> str:
        # Generate new public/private key pair
        private_key, public_key = generate_private_public_key()
        _ensure_ssh_home_exists()
        # Store the new public key in S3 bucket
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Body=public_key,
            Bucket=self.bucket_name,
            Key=f"{self.host}/{self.user_id}-cert.pub",
        )

        # Store the private key on the local machine
        private_key_dir = f"{get_user_path()}/.ssh/{self.host}"
        if not os.path.isdir(private_key_dir):
            os.makedirs(private_key_dir)
        private_key_path = f"{private_key_dir}/{self.user_id}"
        with open(private_key_path, "wb") as private_out:
            private_out.write(private_key)
        shutil.chown(private_key_path, user=get_username(), group=-1)
        os.chmod(private_key_path, 0o600)

        return public_key.decode()


class LocalPublisher(Publisher):
    """Local Publisher class"""

    def __init__(self, host: str, user_id: str):
        self.host = host
        self.user_id = user_id

    def publish_new_key(self) -> str:
        user_path = os.path.expanduser("~")
        _ensure_ssh_home_exists()
        _, public_key = generate_private_public_key_in_file(
            f"{user_path}/.ssh/{self.host}",
            private_key_name=self.user_id,
            public_key_name=f"{self.user_id}-cert.pub",
        )
        return public_key.decode()

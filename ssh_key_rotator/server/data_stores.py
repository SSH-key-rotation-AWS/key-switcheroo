"Data stores that specifies where a Server stores its keys"
import os
from abc import ABC, abstractmethod
import boto3
from ssh_key_rotator.util import get_user_path


class DataStore(ABC):
    "A server uses a DataStore to get public keys from somewhere."

    @abstractmethod
    def get_sshd_config_line(self):
        "Return the config line that the server will add to the sshd_config"

    @abstractmethod
    def delete_key(self, host: str, user: str):
        "Delete the key for the host/user"


class S3DataStore(DataStore):
    "Store the public keys in an S3 bucket"

    def __init__(self, _s3_bucket_name: str):
        self._s3_bucket_name = _s3_bucket_name

    @property
    def s3_bucket_name(self):
        "The name of the bucket in which the keys are stored"
        return self._s3_bucket_name

    def get_sshd_config_line(self) -> str:
        return f"s3 ${self.s3_bucket_name}"

    def delete_key(self, host: str, user: str):
        s3_client = boto3.client("s3")
        s3_client.delete_object(Bucket=self.s3_bucket_name, Key=f"{host}/{user}")


class FileSystemDataStore(DataStore):
    "Stores keys in a file system"

    def __init__(self, temp: bool = False):
        self.temp = temp
        self.dir = f"{get_user_path()}/.ssh"

    def get_sshd_config_line(self) -> str:
        return "local"

    def delete_key(self, host: str, user: str):
        os.remove(f"{get_user_path()}/.ssh/{host}/{user}")

"Data stores that specifies where a Server stores its keys"
from abc import ABC, abstractmethod
from dataclasses import dataclass


class DataStore(ABC):
    "A server uses a DataStore to get public keys from somewhere."

    @abstractmethod
    def get_sshd_config_line(self):
        "Return the config line that the server will add to the sshd_config"

    def putting_this_here_to_make_pylint_happy_for_now(self):
        "Need 2 public methods, maybe will redesign later"


class S3DataStore(DataStore):
    "Store the public keys in an S3 bucket"

    def __init__(self, _s3_bucket_name: str):
        self._s3_bucket_name = _s3_bucket_name

    @property
    def s3_bucket_name(self):
        "The name of the bucket in which the keys are stored"
        return self._s3_bucket_name

    def get_sshd_config_line(self):
        pass


UseExistingPathOptions = str


@dataclass
class UseNewPathOptions:
    "Options for a data store to create a new path for keys - where and lifespan"
    dir: str
    temp: bool = True


class FileSystemDataStore(DataStore):
    "Stores keys in a file system"

    def __init__(self, creation_options: UseExistingPathOptions | UseNewPathOptions):
        self.dir = "TODo"
        self.creation_options = creation_options

    def get_sshd_config_line(self) -> str:
        return "AuthorizedKeysFile /path/to/authorized_keys"

"Data stores that specifies where a Server stores its keys"
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from switcheroo import paths
from switcheroo.custom_keygen import KeyMetadata
from switcheroo import util
from switcheroo.exceptions import KeyNotFoundException


class DataStore(ABC):
    "A server uses a DataStore to get public keys from somewhere."

    def __init__(self, ssh_home: Path | None = None, temp: bool = False):
        # If temp is true, will reset the home_dir to a temp file upon usage as a context manager
        self._temp = temp
        # ssh_home is only relevant if not being used as a context manager
        self._dir: Path = paths.local_ssh_home() if ssh_home is None else ssh_home
        # To be used later if we decide to use this as a context manager, and temp is selected
        self._temp_dir: TemporaryDirectory[str] | None = None

    @property
    def home_dir(self) -> Path:
        """The folder where local files are stored"""
        if self._temp and self._temp_dir is not None:
            return Path(self._temp_dir.name)
        return self._dir

    @abstractmethod
    def get_sshd_config_line(self):
        "Return the config line that the server will add to the sshd_config"

    @abstractmethod
    def publish(
        self, host: str, user: str, metadata: KeyMetadata | None
    ) -> tuple[str, KeyMetadata]:
        """Publish a new public key for the given host and user with metadata"""

    @abstractmethod
    def retrieve(self, host: str, user: str) -> str:
        """Retrieve the public key for the given host and user"""

    def __enter__(self):
        if self._temp:
            self._temp_dir: TemporaryDirectory[str] | None = TemporaryDirectory[
                str
            ](  # pylint: disable=consider-using-with
                prefix="ssh-keys-", dir=self._dir
            )

    def __exit__(self, exc_t, exc_v, exc_tb):
        if self._temp:
            assert self._temp_dir is not None
            self._temp_dir.__exit__(None, None, None)


class FileSystemDataStore(DataStore):
    "Stores keys in a file system"

    def get_sshd_config_line(self) -> str:
        return f'-ds local --sshdir "{str(self.home_dir)}"'

    def publish(
        self, host: str, user: str, metadata: KeyMetadata | None = None
    ) -> tuple[str, KeyMetadata]:
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        _, public_key = util.generate_private_public_key_in_file(
            paths.local_key_dir(host, user, home_dir=self.home_dir)
        )
        metadata_file = paths.local_metadata_loc(host, user, home_dir=self.home_dir)
        with open(metadata_file, encoding="utf-8", mode="wt") as metadata_file:
            metadata.serialize(metadata_file)
        return public_key.decode(), metadata

    def retrieve(self, host: str, user: str) -> str:
        key_path = paths.local_public_key_loc(host, user, home_dir=self.home_dir)
        try:
            with open(key_path, mode="rt", encoding="utf-8") as key_file:
                return key_file.read()
        except FileNotFoundError:
            raise KeyNotFoundException()


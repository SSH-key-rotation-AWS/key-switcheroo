from abc import ABC, abstractmethod


class DataStore(ABC):
    @abstractmethod
    def get_sshd_config_line(self):
        pass


class S3DataStore(DataStore):
    def get_sshd_config_line(self):
        return super().get_sshd_config_line()


class FileSystemDataStore(DataStore):
    def get_sshd_config_line(self) -> str:
        return "AuthorizedKeysFile /path/to/authorized_keys"

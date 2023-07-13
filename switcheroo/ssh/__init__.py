from abc import ABC, abstractmethod


class AuthorizedKeysCmndProvider(ABC):
    @property
    @abstractmethod
    def command(self) -> str:
        "Provides an AuthorizedKeysCommand for the sshd to use"

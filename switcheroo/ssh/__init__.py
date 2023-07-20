from abc import ABC, abstractmethod


class AuthorizedKeysCmndProvider(ABC):
    @property
    @abstractmethod
    def command(self) -> str:
        "Provides an AuthorizedKeysCommand for the sshd to use"


# pylint: disable=too-few-public-methods
class MetricConstants:
    NAME_SPACE = "Key-Switcheroo"
    COUNTER_METRIC_NAME = "Key-Count"
    TIMING_METRIC_NAME = "Time-to-Publish-Keys"

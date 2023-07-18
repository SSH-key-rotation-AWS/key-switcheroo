from abc import ABC, abstractmethod


class AuthorizedKeysCmndProvider(ABC):
    """Provides the arguments for an AuthorizedKeysCommand for the sshd to use. \
    This is mostly useful for testing.
    """

    @property
    @abstractmethod
    def command(self) -> str:
        "Provides an AuthorizedKeysCommand for the sshd to use"


# pylint: disable=too-few-public-methods
class MetricConstants:
    """Constants to use for metrics."""

    NAME_SPACE = "Key-Switcheroo"
    COUNTER_METRIC_NAME = "Key Count"
    TIMING_METRIC_NAME = "Time Published"

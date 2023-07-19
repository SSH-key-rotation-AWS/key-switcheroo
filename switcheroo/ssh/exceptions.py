import dataclasses
from typing import TypeAlias, Literal

SSHItem: TypeAlias = Literal["public key", "private key", "metadata"]


class SSHItemNotFoundException(Exception):
    """Raised when some SSH item (public key, private key, or key metadata) was requested\
    but could not be found."""

    @dataclasses.dataclass(frozen=True)
    class Data:
        """Data about what the user was trying to request that failed."""

        requested_user: str
        requested_host: str
        requested_item: SSHItem

    def __init__(self, data: Data | None = None):
        if data is None:
            self.message = "Some SSH-related item could not be found!"
        else:
            self.message = (
                f"{data.requested_item} could not be found for user "
                f"{data.requested_user} and host {data.requested_host}"
            )
        super().__init__(self.message)

import dataclasses
from typing import TypeAlias, Literal

SSHItem: TypeAlias = Literal["public key", "private key", "metadata"]


class SSHItemNotFoundException(Exception):
    """Raised when a public key cannot be found for the user.

    Attributes:
        message -- explanation of the error
    """

    @dataclasses.dataclass(frozen=True)
    class Data:
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

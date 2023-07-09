import dataclasses


class KeyNotFoundException(Exception):
    """Raised when a public key cannot be found for the user.

    Attributes:
        message -- explanation of the error
    """

    @dataclasses.dataclass(frozen=True)
    class Data:
        requested_user: str
        requested_host: str

    def __init__(self, data: Data | None = None):
        if data is None:
            self.message = "Public key could not be found!"
        else:
            self.message = f"Public key could not be found for user {data.requested_user}\
                and host {data.requested_host}"
        super().__init__(self.message)

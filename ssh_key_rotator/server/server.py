"SSH Server"
from typing import Callable
from ssh_key_rotator.server.data_stores import DataStore
from ssh_key_rotator.ssh_decorators import get_open_port


class Server:
    "Wrapper for SSH Server. Takes a DataStore to determine where to look for keys"

    def __init__(
        self, data_store: DataStore, port: int | Callable[[], int] = get_open_port
    ):
        if callable(port):
            port = port()
        self.port = port
        self.data_store = data_store

    @property
    def logs(self) -> list[str]:
        "Returns the sshd logs"
        return []

    async def __aenter__(self):
        return self

    async def __aexit__(self, one, two, three):
        pass

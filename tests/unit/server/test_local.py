"Tests the server with keys stored locally"
from io import StringIO
from pathlib import Path
import socket
from getpass import getuser
from unittest import IsolatedAsyncioTestCase
from hamcrest import assert_that, has_item, contains_string
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import RSAKey
from switcheroo.ssh.server import Server
from switcheroo.ssh.data_org.retriever import FileKeyRetriever
from switcheroo import paths
from switcheroo import util
from tests.util import SSHDirCleanup


class TestServerLocal(IsolatedAsyncioTestCase):
    "Test server with local keys"

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._temp_dir: Path | None = None

    def setUp(self) -> None:
        self._temp_dir = self.enterContext(SSHDirCleanup())

    async def test_retrieve_public_keys_locally(self):
        assert self._temp_dir is not None
        retriever = FileKeyRetriever(self._temp_dir)
        async with Server(retriever=retriever) as server:
            server: Server = server
            host = socket.getfqdn()
            random_host_dir = paths.local_key_dir(host, getuser(), self._temp_dir)
            private_key, _ = util.generate_private_public_key_in_file(random_host_dir)
            key: RSAKey = RSAKey.from_private_key(StringIO(private_key.decode()))
            key_fingerprint: str = key.fingerprint  # type: ignore
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                "127.0.0.1",
                port=server.port,
                pkey=key,
            )
            logs = await server.logs
            assert isinstance(key_fingerprint, str)
            assert_that(logs, has_item(contains_string(key_fingerprint)))

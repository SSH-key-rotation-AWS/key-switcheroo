"Tests the server with keys stored locally"
from io import StringIO
import socket
from unittest import IsolatedAsyncioTestCase
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import RSAKey
from ssh_key_rotator.server.server import Server
from ssh_key_rotator.server.data_stores import FileSystemDataStore
from ssh_key_rotator.custom_keygen import generate_private_public_key_in_file
from ssh_key_rotator.util import get_username


class TestServerLocal(IsolatedAsyncioTestCase):
    "Test server with local keys"

    async def test_retrieve_public_keys_locally(self):
        data_store = FileSystemDataStore(temp=True)
        async with Server(data_store=data_store) as server:
            server: Server = server
            host = socket.getfqdn()
            random_host_dir = f"{data_store.dir}/{host}"
            private_key, _ = generate_private_public_key_in_file(
                random_host_dir,
                private_key_name=get_username(),
                public_key_name=f"{get_username()}-cert.pub",
            )
            key: RSAKey = RSAKey.from_private_key(StringIO(private_key.decode()))
            key_fingerprint = key.fingerprint  # type: ignore
            client = SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                "127.0.0.1",
                port=server.port,
                pkey=key,
            )
            self.assertTrue(any(key_fingerprint in line for line in await server.logs))

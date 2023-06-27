"Tests the server with keys stored locally"
from io import StringIO
from unittest import IsolatedAsyncioTestCase
from paramiko.client import SSHClient
from paramiko import RSAKey
from ssh_key_rotator.server.server import Server
from ssh_key_rotator.server.data_stores import FileSystemDataStore
from ssh_key_rotator.custom_keygen import generate_private_public_key_in_file


class TestServerLocal(IsolatedAsyncioTestCase):
    "Test server with local keys"

    async def can_retrieve_public_keys_locally(self):
        data_store = FileSystemDataStore()
        async with Server(data_store=data_store) as server:
            server: Server = server
            random_user_dir = f"{data_store.dir}/SomeComputerHost/some_person"
            private_key, _ = generate_private_public_key_in_file(random_user_dir)
            key: RSAKey = RSAKey.from_private_key(StringIO(private_key.decode()))
            key_fingerprint = key.fingerprint  # type: ignore
            client = SSHClient()
            client.load_system_host_keys()
            client.connect("127.0.0.1", port=server.port, key_filename=data_store.dir)
            self.assertTrue(any(key_fingerprint in line for line in await server.logs))

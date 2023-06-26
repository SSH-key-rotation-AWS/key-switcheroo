"Tests the server with keys stored locally"
from unittest import IsolatedAsyncioTestCase
from paramiko.client import SSHClient
from paramiko import RSAKey
from ssh_key_rotator.server.server import Server
from ssh_key_rotator.server.data_stores import FileSystemDataStore, UseNewPathOptions
from ssh_key_rotator.ssh_decorators import get_user_path
from ssh_key_rotator.custom_keygen import generate_private_public_key_in_file


class TestServerLocal(IsolatedAsyncioTestCase):
    "Test server with local keys"

    async def can_retrieve_public_keys_locally(self):
        data_store = FileSystemDataStore(UseNewPathOptions(dir=get_user_path()))
        async with Server(data_store=data_store) as server:
            server: Server = server
            generate_private_public_key_in_file(data_store.dir)
            key: RSAKey = RSAKey.from_private_key_file(f"{data_store.dir}/key")
            key_fingerprint = key.fingerprint  # type: ignore
            client = SSHClient()
            client.load_system_host_keys()
            client.connect("127.0.0.1", port=server.port, key_filename=data_store.dir)
            self.assertTrue(any(key_fingerprint in line for line in server.logs))

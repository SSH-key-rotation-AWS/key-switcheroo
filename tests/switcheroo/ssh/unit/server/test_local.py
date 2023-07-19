"Tests the server with keys stored locally"
from io import StringIO
from pathlib import Path
import socket
from getpass import getuser
import pytest
from hamcrest import assert_that, has_item, contains_string
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import RSAKey
from tests.switcheroo.ssh.server import Server
from switcheroo.ssh.data_org.retriever import FileKeyRetriever
from switcheroo import paths
from switcheroo import util


@pytest.mark.asyncio
async def test_retrieve_public_keys_locally(
    ssh_temp_path: Path, file_key_retriever: FileKeyRetriever
):
    async with Server(retriever=file_key_retriever) as server:
        server: Server = server
        host = socket.getfqdn()
        key_dir = paths.local_key_dir(host, getuser(), ssh_temp_path)
        private_key, _ = util.generate_private_public_key_in_file(key_dir)
        key: RSAKey = RSAKey.from_private_key(StringIO(private_key.decode()))
        key_fingerprint: str = key.fingerprint  # type: ignore
        file_key_retriever.retrieve_key(host, getuser())
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

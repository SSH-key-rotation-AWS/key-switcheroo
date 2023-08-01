"Tests the server with keys stored locally"
from pathlib import Path
import socket
from getpass import getuser
from hamcrest import assert_that, equal_to
from Crypto.PublicKey import RSA
from switcheroo.ssh.data_org.retriever import FileKeyRetriever
from switcheroo import paths
from switcheroo import util


def test_retrieve_public_keys_locally(
    ssh_temp_path: Path, file_key_retriever: FileKeyRetriever
):
    host = socket.getfqdn()
    key_dir = paths.local_key_dir(host, getuser(), ssh_temp_path)
    private_key, _ = util.generate_private_public_key_in_file(key_dir)
    crypto_key = RSA.import_key(private_key).public_key().export_key(format="OpenSSH")
    retrieved_key = file_key_retriever.retrieve_key(host, getuser())[
        0
    ].public_key.byte_data
    assert_that(retrieved_key, equal_to(crypto_key))

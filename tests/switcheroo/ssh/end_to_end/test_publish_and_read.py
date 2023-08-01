import socket
from getpass import getuser
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy, RSAKey
import pytest
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.data_org.retriever import FileKeyRetriever
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths
from tests.switcheroo.ssh.conftest import ServerGenerator


# We cannot mock services on E2E tests, because the SSH server running the retrieval script runs
# a new instance of python which does not have the S3 mock from the publishing end.
@pytest.mark.require_credentials
@pytest.mark.nomock
@pytest.mark.asyncio
class TestE2E:
    async def test_publish_and_retrieve_s3(
        self,
        s3_key_retriever: S3KeyRetriever,
        s3_key_publisher: S3KeyPublisher,
        ssh_temp_path: Path,
        create_temp_server: ServerGenerator,
    ):
        # Start the server with the S3 data store
        async with create_temp_server(s3_key_retriever) as server:
            # Create public/private key pair and publish the public key to S3
            s3_key_publisher.publish_key(socket.getfqdn(), getuser())
            # Create an SSH client to connect to the server
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = paths.local_private_key_loc(
                socket.getfqdn(), getuser(), ssh_temp_path
            )
            private_key = RSAKey.from_private_key_file(
                str(pkey_location)
            )  # Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                pytest.fail("Some error occured connecting!")

    async def test_publish_and_retrieve_local(
        self,
        file_key_retriever: FileKeyRetriever,
        file_key_publisher: FileKeyPublisher,
        ssh_temp_path: Path,
        create_temp_server: ServerGenerator,
    ):
        # Start the server with the S3 data store
        async with create_temp_server(file_key_retriever) as server:
            # Create public/private key pair and publish the public key to S3
            file_key_publisher.publish_key(socket.getfqdn(), getuser())
            # Create an SSH client to connect to the server
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = paths.local_private_key_loc(
                socket.getfqdn(), getuser(), ssh_temp_path
            )
            private_key = RSAKey.from_private_key_file(
                str(pkey_location)
            )  # Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                pytest.fail("Some error occured connecting!")

    async def test_public_key_is_rotated(
        self,
        s3_key_retriever: S3KeyRetriever,
        s3_key_publisher: S3KeyPublisher,
        ssh_temp_path: Path,
        create_temp_server: ServerGenerator,
    ):
        "Tests if the server rejects the connection after rotating keys"
        # Start the server with the S3 data store
        async with create_temp_server(s3_key_retriever) as server:
            # Create public/private key pair and publish the public key to S3
            s3_key_publisher.publish_key(socket.getfqdn(), getuser())
            # Create an SSH client to connect to the server
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = paths.local_private_key_loc(
                socket.getfqdn(), getuser(), ssh_temp_path
            )
            private_key = RSAKey.from_private_key_file(
                str(pkey_location)
            )  # Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                pytest.fail("Some error occured connecting!")
            # Now we rotate the keys
            s3_key_publisher.publish_key(socket.getfqdn(), getuser())
            # Try connecting with the old key - fail if we connect
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
                pytest.fail("Should not be able to connect after rotating keys!")
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            # Now try with the new key
            private_key = RSAKey.from_private_key_file(str(pkey_location))
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                pytest.fail("Some error occured connecting!")

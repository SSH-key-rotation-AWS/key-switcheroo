import socket
from getpass import getuser
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy, RSAKey
import pytest
from switcheroo.ssh.server.server import Server
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths


@pytest.mark.asyncio
async def test_publish_and_retrieve(ssh_temp_path: Path, s3_bucket: str):
    retriever = S3KeyRetriever(ssh_temp_path, s3_bucket)
    # Start the server with the S3 data store
    async with Server(retriever=retriever) as server:
        # Instantiate the S3 publisher
        publisher = S3KeyPublisher(s3_bucket, ssh_temp_path)
        # Create public/private key pair and publish the public key to S3
        publisher.publish_key(socket.getfqdn(), getuser())
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

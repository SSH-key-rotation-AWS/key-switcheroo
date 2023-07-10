import os
import socket
from getpass import getuser
from unittest import IsolatedAsyncioTestCase
import boto3
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from switcheroo.ssh.server.server import Server
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths
from tests.util import SSHDirCleanup
from tests.util.s3 import S3Cleanup


class EndToEnd(IsolatedAsyncioTestCase):
    "Tests publishing and retrieving SSH keys"

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]
        self._s3_client = boto3.client("s3")  # type: ignore

    def setUp(self) -> None:
        self._temp_dir = self.enterContext(SSHDirCleanup())
        self.enterContext(S3Cleanup(self._s3_client, self.bucket_name))

    async def test_publish_and_retrieve(self):
        retriever = S3KeyRetriever(paths.local_ssh_home(), self.bucket_name)
        # Start the server with the S3 data store
        async with Server(retriever=retriever) as server:
            # Instantiate the S3 publisher
            publisher = S3KeyPublisher(self.bucket_name, self._temp_dir)
            # Create public/private key pair and publish the public key to S3
            publisher.publish_key(socket.getfqdn(), getuser())
            # Create an SSH client to connect to the server
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = paths.local_private_key_loc(
                socket.getfqdn(), getuser(), self._temp_dir
            )
            private_key = RSAKey.from_private_key_file(
                str(pkey_location)
            )  # Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                self.fail("Some error occured connecting!")

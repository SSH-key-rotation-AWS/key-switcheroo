import os
import socket
from getpass import getuser
from unittest import IsolatedAsyncioTestCase
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from switcheroo.server.server import Server
from switcheroo.server.data_stores import S3DataStore
from switcheroo.publisher.key_publisher import S3Publisher
from switcheroo import paths


class EndToEnd(IsolatedAsyncioTestCase):
    "Tests publishing and retrieving SSH keys"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]

    async def test_publish_and_retrieve(self):
        # Initialize a temporary S3 data store
        data_store = S3DataStore(self.bucket_name, temp=True)
        # Start the server with the S3 data store
        async with Server(data_store=data_store) as server:
            # Instantiate the S3 publisher
            publisher = S3Publisher(self.bucket_name, socket.getfqdn(), getuser())
            # Create public/private key pair and publish the public key to S3
            publisher.publish_new_key(data_store=data_store)
            # Create an SSH client to connect to the server
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = paths.local_private_key_loc(
                socket.getfqdn(), getuser(), home_dir=data_store.home_dir
            )
            private_key = RSAKey.from_private_key_file(
                str(pkey_location)
            )  # Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                self.fail("Some error occured connecting!")

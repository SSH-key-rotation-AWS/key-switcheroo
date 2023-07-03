import os
import socket
from unittest import IsolatedAsyncioTestCase
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from ssh_key_rotator.server.server import Server
from ssh_key_rotator.server.data_stores import S3DataStore
from ssh_key_rotator.publisher.key_publisher import S3Publisher
from ssh_key_rotator.util import get_username, get_user_path


class EndToEnd(IsolatedAsyncioTestCase):
    "Tests publishing and retrieving SSH keys"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]

    async def test_publish_and_retrieve(self):
        #Initialize a temporary S3 data store
        data_store = S3DataStore(self.bucket_name, temp=True)
        #Start the server with the S3 data store
        async with Server(data_store=data_store) as server:
            #Instantiate the S3 publisher
            publisher = S3Publisher(
                self.bucket_name, socket.getfqdn(), get_username()
            )
            publisher.publish_new_key() #Create public/private key pair and publish the public key to S3
            client = SSHClient() #Create an SSH client to connect to the server
            client.set_missing_host_key_policy(AutoAddPolicy())
            pkey_location = (
                f"{get_user_path()}/.ssh/{socket.getfqdn()}/{get_username()}"
            )
            private_key = RSAKey.from_private_key_file(pkey_location) #Fetch private key
            try:
                client.connect(hostname="127.0.0.1", port=server.port, pkey=private_key)
            except Exception:  # pylint: disable=broad-exception-caught
                self.fail("Some error occured connecting!")

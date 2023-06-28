"Tests the server with keys stored in S3"
import os
from unittest import IsolatedAsyncioTestCase
from io import StringIO
import socket
from paramiko import SSHClient, RSAKey, AutoAddPolicy
import boto3
from ssh_key_rotator.server.server import Server
from ssh_key_rotator.server.data_stores import S3DataStore
from ssh_key_rotator.custom_keygen import generate_private_public_key
from ssh_key_rotator.util import get_username


class TestServerRemote(IsolatedAsyncioTestCase):
    "Test server with keys stored in S3"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]

    async def test_retrieve_public_keys_from_s3(self):
        "Can the server retrieve public keys from s3?"
        data_store = S3DataStore(self.bucket_name, temp=True)
        async with Server(data_store=data_store) as server:
            server: Server = server
            private_key, public_key = generate_private_public_key()
            private_key_paramiko = RSAKey.from_private_key(
                StringIO(private_key.decode())
            )
            s3_client = boto3.client("s3")
            key_name = f"{socket.getfqdn()}/{get_username()}-cert.pub"
            s3_client.put_object(
                Bucket=data_store.s3_bucket_name, Key=key_name, Body=public_key
            )
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(
                "127.0.0.1",
                server.port,
                username=get_username(),
                pkey=private_key_paramiko,
            )
            key_fingerprint = private_key_paramiko.fingerprint  # type: ignore
            self.assertTrue(any(key_fingerprint in line for line in await server.logs))

"Tests the server with keys stored in S3"
import os
from unittest import IsolatedAsyncioTestCase
from io import StringIO
import socket
from getpass import getuser
from hamcrest import assert_that, has_item, contains_string
from paramiko import SSHClient, RSAKey, AutoAddPolicy
import boto3
from switcheroo.server.server import Server
from switcheroo.data_store.s3 import S3DataStore
from switcheroo.custom_keygen import KeyGen
from switcheroo import paths


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
            private_key, public_key = KeyGen.generate_private_public_key()
            private_key_paramiko = RSAKey.from_private_key(
                StringIO(private_key.decode())
            )
            s3_client = boto3.client("s3")
            key_name = paths.cloud_public_key_loc(host=socket.getfqdn(), user=getuser())
            s3_client.put_object(
                Bucket=data_store.s3_bucket_name, Key=str(key_name), Body=public_key
            )
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(
                "127.0.0.1",
                server.port,
                username=getuser(),
                pkey=private_key_paramiko,
            )
            key_fingerprint = private_key_paramiko.fingerprint  # type: ignore
            logs = await server.logs
            assert_that(logs, has_item(contains_string(key_fingerprint)))

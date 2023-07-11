"Tests the server with keys stored in S3"
import os
from unittest import IsolatedAsyncioTestCase
from io import StringIO
import socket
from getpass import getuser
from hamcrest import assert_that, has_item, contains_string
from paramiko import SSHClient, RSAKey, AutoAddPolicy
import boto3
from switcheroo.ssh.server.server import Server
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo.ssh.objects.key import KeyMetadata, KeyGen
from switcheroo import paths
from tests.util.s3 import S3Cleanup


class TestServerRemote(IsolatedAsyncioTestCase):
    "Test server with keys stored in S3"

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]
        self._s3_retriever: S3KeyRetriever = S3KeyRetriever(
            paths.local_ssh_home(), self._bucket_name
        )
        self._s3_client = boto3.client("s3")  # type: ignore

    def setUp(self) -> None:
        self.enterContext(S3Cleanup(self._s3_client, self._bucket_name))

    async def test_retrieve_public_keys_from_s3(self):
        "Can the server retrieve public keys from s3?"
        async with Server(retriever=self._s3_retriever) as server:
            server: Server = server
            private_key, public_key = KeyGen.generate_private_public_key()
            private_key_paramiko = RSAKey.from_private_key(
                StringIO(private_key.decode())
            )
            key_name = paths.cloud_public_key_loc(host=socket.getfqdn(), user=getuser())
            self._s3_client.put_object(
                Bucket=self._bucket_name, Key=str(key_name), Body=public_key
            )
            self._s3_client.put_object(
                Bucket=self._bucket_name,
                Key=str(paths.cloud_metadata_loc(socket.getfqdn(), getuser())),
                Body=KeyMetadata.now_by_executing_user().serialize_to_string(),
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
            key_fingerprint: str = private_key_paramiko.fingerprint  # type: ignore
            logs = await server.logs
            assert isinstance(key_fingerprint, str)
            assert_that(logs, has_item(contains_string(key_fingerprint)))

"Tests the server with keys stored in S3"
from io import StringIO
import socket
from getpass import getuser
from hamcrest import assert_that, has_item, contains_string
from paramiko import SSHClient, RSAKey, AutoAddPolicy
import pytest
from mypy_boto3_s3 import Client
from switcheroo.ssh.server.server import Server
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo.ssh.objects.key import KeyGen
from switcheroo import paths


@pytest.mark.asyncio
async def test_retrieve_public_keys_from_s3(
    s3_retriever: S3KeyRetriever, s3_client: Client, s3_bucket: str
):
    "Can the server retrieve public keys from s3?"
    async with Server(retriever=s3_retriever) as server:
        server: Server = server
        private_key, public_key = KeyGen.generate_private_public_key()
        private_key_paramiko = RSAKey.from_private_key(StringIO(private_key.decode()))
        key_name = paths.cloud_public_key_loc(host=socket.getfqdn(), user=getuser())
        s3_client.put_object(Bucket=s3_bucket, Key=str(key_name), Body=public_key)
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

"Tests the server with keys stored in S3"
import socket
from getpass import getuser
from hamcrest import assert_that, equal_to
from Crypto.PublicKey import RSA
from mypy_boto3_s3 import Client
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo.ssh.objects.key import KeyGen
from switcheroo import paths


def test_retrieve_public_keys_from_s3(
    s3_key_retriever: S3KeyRetriever, s3_client: Client, s3_bucket: str
):
    "Can the server retrieve public keys from s3?"
    private_key, public_key = KeyGen.generate_private_public_key()
    key_name = paths.cloud_public_key_loc(host=socket.getfqdn(), user=getuser())
    s3_client.put_object(Bucket=s3_bucket, Key=str(key_name), Body=public_key)
    crypto_key = RSA.import_key(private_key).public_key().export_key(format="OpenSSH")
    retrieved_key = s3_key_retriever.retrieve_public_key(
        socket.getfqdn(), getuser()
    ).byte_data
    assert_that(retrieved_key, equal_to(crypto_key))

import os
from unittest import TestCase
from pathlib import Path
import boto3
from hamcrest import assert_that, contains_string, equal_to
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.objects.key import KeyMetadata
from switcheroo import paths
from tests.util import SSHDirCleanup
from tests.util.s3 import S3Cleanup


class S3PublisherTests(TestCase):
    """Tests for S3 publisher class"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]
        self._s3_client = boto3.client("s3")  # type: ignore
        self._temp_dir: Path | None = None
        self._publisher: S3KeyPublisher | None = None
        self.some_user = "Random_User"
        self.some_host = "Random_Host"

    def setUp(self) -> None:
        self._temp_dir = self.enterContext(SSHDirCleanup())
        self._publisher = S3KeyPublisher(self.bucket_name, self._temp_dir)
        self.enterContext(S3Cleanup(self._s3_client, self._publisher))

    def _check_published_key_contains(self, expected_key: str):
        key_loc = paths.cloud_public_key_loc(self.some_host, self.some_user)
        file = self._s3_client.get_object(Bucket=self.bucket_name, Key=str(key_loc))
        file_data = file["Body"].read()
        contents = file_data.decode("utf-8")
        assert_that(contents, contains_string(expected_key))

    def test_s3_publish(self):
        """Test for S3 publisher"""
        assert self._publisher is not None
        key, _ = self._publisher.publish_key(self.some_host, self.some_user)
        self._check_published_key_contains(key.public_key.byte_data.decode())

    def test_public_metadata_works(self):
        """Does using the with metadata method publish the metadata correctly?"""
        assert self._publisher is not None
        _, metadata = self._publisher.publish_key(self.some_host, self.some_user)
        metadata_loc = paths.cloud_metadata_loc(self.some_host, self.some_user)
        file = self._s3_client.get_object(
            Bucket=self.bucket_name, Key=str(metadata_loc)
        )
        file_data = file["Body"].read()
        contents = file_data.decode("utf-8")
        read_metadata = KeyMetadata.from_string(contents)
        assert_that(metadata, equal_to(read_metadata))

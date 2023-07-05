import os
from unittest import TestCase
import boto3
from hamcrest import assert_that, contains_string, equal_to
from switcheroo.publisher.key_publisher import S3Publisher
from switcheroo.custom_keygen import KeyGen, KeyMetadata


class S3PublisherTests(TestCase):

    """Tests for S3 publisher class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]
        self.s3_publisher = S3Publisher(self.bucket_name, "ExampleServer", "12345")

    def _check_published_key_contains(self, expected_key: str):
        s3_client = boto3.client("s3")
        key_loc = f"{self.s3_publisher.publishing_location}/{KeyGen.PUBLIC_KEY_NAME}"
        file = s3_client.get_object(Bucket=self.bucket_name, Key=key_loc)
        file_data = file["Body"].read()
        contents = file_data.decode("utf-8")
        assert_that(contents, contains_string(expected_key))
        s3_client.delete_object(Bucket=self.bucket_name, Key=key_loc)

    def test_s3_publish(self):
        """Test for S3 publisher"""
        public_key = self.s3_publisher.publish_new_key()
        self._check_published_key_contains(public_key)

    def test_publish_key_in_metadata_method(self):
        """Does using the with metadata method publish the key correctly??"""
        public_key, _ = self.s3_publisher.publish_new_key_with_metadata()
        self._check_published_key_contains(public_key)

    def test_public_metadata_works(self):
        """Does using the with metadata method publish the metadata correctly?"""
        _, metadata = self.s3_publisher.publish_new_key_with_metadata()
        s3_client = boto3.client("s3")
        metadata_loc = (
            f"{self.s3_publisher.publishing_location}/{KeyMetadata.FILE_NAME}"
        )
        file = s3_client.get_object(Bucket=self.bucket_name, Key=metadata_loc)
        file_data = file["Body"].read()
        contents = file_data.decode("utf-8")
        read_metadata = KeyMetadata.from_string(contents)
        assert_that(metadata, equal_to(read_metadata))

import os
from unittest import TestCase
import boto3
from hamcrest import assert_that, contains_string
from key_switcheroo.publisher.key_publisher import S3Publisher


class S3PublisherTests(TestCase):

    """Tests for S3 publisher class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket_name = os.environ["SSH_KEY_DEV_BUCKET_NAME"]

    def test_s3_publish(self):
        """Test for S3 publisher"""
        s3_publisher = S3Publisher(self.bucket_name, "ExampleServer", "12345")
        public_key = s3_publisher.publish_new_key()
        s3_client = boto3.client("s3")
        file = s3_client.get_object(
            Bucket=self.bucket_name, Key="ExampleServer/12345-cert.pub"
        )
        file_data = file["Body"].read()
        contents = file_data.decode("utf-8")
        assert_that(contents, contains_string(public_key))
        s3_client.delete_object(
            Bucket=self.bucket_name, Key="ExampleServer/12345-cert.pub"
        )

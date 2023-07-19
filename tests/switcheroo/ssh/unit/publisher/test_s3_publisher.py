from mypy_boto3_s3 import Client
from hamcrest import assert_that, contains_string, equal_to
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.objects.key import KeyMetadata
from switcheroo import paths


def test_s3_publish(
    s3_key_publisher: S3KeyPublisher,
    some_name: str,
    some_host: str,
    s3_client: Client,
    s3_bucket: str,
):
    """Test for S3 publisher"""
    key, _ = s3_key_publisher.publish_key(some_host, some_name)
    key_loc = paths.cloud_public_key_loc(some_host, some_name)
    file = s3_client.get_object(Bucket=s3_bucket, Key=str(key_loc))
    file_data = file["Body"].read()
    contents = file_data.decode("utf-8")
    assert_that(contents, contains_string(key.public_key.byte_data.decode()))


def test_public_metadata_works(
    s3_key_publisher: S3KeyPublisher,
    some_name: str,
    some_host: str,
    s3_client: Client,
    s3_bucket: str,
):
    """Does using the with metadata method publish the metadata correctly?"""
    _, metadata = s3_key_publisher.publish_key(some_host, some_name)
    metadata_loc = paths.cloud_metadata_loc(some_host, some_name)
    file = s3_client.get_object(Bucket=s3_bucket, Key=str(metadata_loc))
    file_data = file["Body"].read()
    contents = file_data.decode("utf-8")
    read_metadata = KeyMetadata.from_string(contents)
    assert_that(metadata, equal_to(read_metadata))

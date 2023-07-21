from typing import Generator
import pytest
import boto3
from mypy_boto3_s3 import Client


def _empty_bucket(s3_client: Client, bucket: str):
    objects = s3_client.list_objects_v2(Bucket=bucket)["Contents"]
    delete_objects = [{"Key": bucket_obj["Key"]} for bucket_obj in objects]  # type: ignore
    s3_client.delete_objects(
        Bucket=bucket,
        Delete={"Objects": delete_objects},  # type: ignore
    )


@pytest.fixture(name="s3_client", scope="session")
def fixture_s3_client() -> Generator[Client, None, None]:
    yield boto3.client("s3")  # type: ignore


@pytest.fixture
def s3_bucket(s3_client: Client) -> Generator[str, None, None]:
    bucket = "dev-test-bucket"
    s3_client.create_bucket(Bucket=bucket)
    yield bucket
    _empty_bucket(s3_client, bucket)

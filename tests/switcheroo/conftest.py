from typing import Generator
import uuid
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


@pytest.fixture(name="s3_client")
def fixture_s3_client(
    credentials: tuple[str, str, str]
) -> Generator[Client, None, None]:
    yield boto3.client(  # type: ignore
        "s3",
        aws_access_key_id=credentials[0],
        aws_secret_access_key=credentials[1],
        region_name=credentials[2],
    )


@pytest.fixture
def s3_bucket(s3_client: Client) -> Generator[str, None, None]:
    bucket_name = str(uuid.uuid4())
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    _empty_bucket(s3_client, bucket_name)
    s3_client.delete_bucket(Bucket=bucket_name)

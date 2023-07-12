from tempfile import TemporaryDirectory
from typing import Generator
from pathlib import Path
import os
import pytest
import boto3
from mypy_boto3_s3 import Client
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.data_org.retriever import FileKeyRetriever
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths


def ssh_temp_dir():
    return TemporaryDirectory(dir=paths.local_ssh_home(), prefix="switcheroo-test-")


def _empty_bucket(s3_client: Client, bucket: str):
    objects = s3_client.list_objects_v2(Bucket=bucket)["Contents"]
    delete_objects = [{"Key": bucket_obj["Key"]} for bucket_obj in objects]  # type: ignore
    s3_client.delete_objects(
        Bucket=bucket,
        Delete={"Objects": delete_objects},  # type: ignore
    )


@pytest.fixture(name="ssh_temp_path")
def fixture_ssh_temp_path() -> Generator[Path, None, None]:
    temp_dir = ssh_temp_dir()
    with temp_dir:
        yield Path(temp_dir.name)


@pytest.fixture
def file_pub(ssh_temp_path: Path) -> Generator[FileKeyPublisher, None, None]:
    yield FileKeyPublisher(ssh_home=ssh_temp_path)


@pytest.fixture(name="s3_client", scope="session")
def fixture_s3_client() -> Generator[Client, None, None]:
    yield boto3.client("s3")  # type: ignore


@pytest.fixture(name="s3_bucket")
def fixture_s3_dev_bucket() -> Generator[str, None, None]:
    yield os.environ["SSH_KEY_DEV_BUCKET_NAME"]


@pytest.fixture
def s3_pub(
    ssh_temp_path: Path, s3_bucket: str, s3_client: Client
) -> Generator[S3KeyPublisher, None, None]:
    yield S3KeyPublisher(s3_bucket, ssh_temp_path)
    _empty_bucket(s3_client, s3_bucket)


@pytest.fixture
def file_retriever(ssh_temp_path: Path) -> Generator[FileKeyRetriever, None, None]:
    yield FileKeyRetriever(ssh_temp_path)


@pytest.fixture
def s3_retriever(
    ssh_temp_path: Path, s3_bucket: str, s3_client: Client
) -> Generator[S3KeyRetriever, None, None]:
    yield S3KeyRetriever(ssh_temp_path, s3_bucket)
    _empty_bucket(s3_client, s3_bucket)


@pytest.fixture
def some_host() -> Generator[str, None, None]:
    yield "Some_Host"


@pytest.fixture
def some_name() -> Generator[str, None, None]:
    yield "Some_User"

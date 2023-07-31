from tempfile import TemporaryDirectory
from typing import Generator, Callable, TypeAlias
from pathlib import Path
import pytest
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo.ssh.data_org.retriever import FileKeyRetriever, KeyRetriever
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths
from tests.switcheroo.ssh.server import Server


def ssh_temp_dir():
    if not paths.local_ssh_home().exists():
        paths.local_ssh_home().mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(dir=paths.local_ssh_home(), prefix="switcheroo-test-")


@pytest.fixture(name="ssh_temp_path")
def fixture_ssh_temp_path() -> Generator[Path, None, None]:
    temp_dir = ssh_temp_dir()
    with temp_dir:
        yield Path(temp_dir.name)


@pytest.fixture
def file_key_publisher(ssh_temp_path: Path) -> Generator[FileKeyPublisher, None, None]:
    yield FileKeyPublisher(ssh_home=ssh_temp_path)


@pytest.fixture
def s3_key_publisher(
    ssh_temp_path: Path, s3_bucket: str, credentials: tuple[str, str, str]
) -> Generator[S3KeyPublisher, None, None]:
    yield S3KeyPublisher(
        s3_bucket, credentials[0], credentials[1], credentials[2], ssh_temp_path
    )


@pytest.fixture
def file_key_retriever(ssh_temp_path: Path) -> Generator[FileKeyRetriever, None, None]:
    yield FileKeyRetriever(ssh_temp_path)


@pytest.fixture
def s3_key_retriever(
    ssh_temp_path: Path, s3_bucket: str, credentials: tuple[str, str, str]
) -> Generator[S3KeyRetriever, None, None]:
    yield S3KeyRetriever(
        ssh_temp_path, credentials[0], credentials[1], credentials[2], s3_bucket
    )


@pytest.fixture
def some_host() -> Generator[str, None, None]:
    yield "Some_Host"


@pytest.fixture
def some_name() -> Generator[str, None, None]:
    yield "Some_User"


@pytest.fixture(name="temp_pathlib_dir")
def fixture_temp_pathlib_dir() -> Generator[Path, None, None]:
    temp_dir = TemporaryDirectory(prefix="switcheroo")
    with temp_dir:
        yield Path(temp_dir.name)


ServerGenerator: TypeAlias = Callable[[KeyRetriever], Server]


@pytest.fixture
def create_temp_server(temp_pathlib_dir: Path) -> ServerGenerator:
    def _create_server_from_retriever(retriever: KeyRetriever):
        server = Server(retriever, serverdata_dir=temp_pathlib_dir)
        return server

    return _create_server_from_retriever

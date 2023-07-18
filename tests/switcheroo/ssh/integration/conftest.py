from tempfile import TemporaryDirectory
from typing import Generator
from pathlib import Path
import pytest
from switcheroo import paths
from metric_system.functions.file_metric_publisher import FileMetricPublisher
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher
from tests.test_cloud_watch.retrievers import FileMetricRetriever
from tests.test_cloud_watch.retrievers.cloudwatch import AWSMetricRetriever


def metrics_temp_dir():
    return TemporaryDirectory(dir=paths.local_metrics_dir(), prefix="switcheroo-test-")


@pytest.fixture(name="metrics_temp_path")
def fixture_metrics_temp_path() -> Generator[Path, None, None]:
    temp_dir = metrics_temp_dir()
    with temp_dir:
        yield Path(temp_dir.name)


@pytest.fixture
def file_metric_publisher(
    metrics_temp_path: Path
) -> Generator[FileMetricPublisher, None, None]:
    yield FileMetricPublisher(metrics_temp_path)


@pytest.fixture
def aws_metric_publisher() -> Generator[AwsMetricPublisher, None, None]:
    yield AwsMetricPublisher("Test Metric Publisher")


@pytest.fixture
def file_metric_retriever(
    metrics_temp_path: Path
) -> Generator[FileMetricRetriever, None, None]:
    yield FileMetricRetriever(metrics_temp_path)


@pytest.fixture
def aws_metric_retriever(
) -> Generator[AWSMetricRetriever, None, None]:
    yield AWSMetricRetriever("Test Metric Retriever")

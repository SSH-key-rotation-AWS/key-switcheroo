# pyright: reportUnknownVariableType=false
import time
import pytest
from metric_system.functions.metrics import CounterMetric, TimingMetric
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher
from tests.test_cloud_watch.retrievers.cloudwatch import AWSMetricRetriever


@pytest.fixture(name="namespace")
def fixture_namespace() -> str:
    "The namespace we will be working with for testing"
    return "switcheroo-test"


@pytest.fixture
def cw_publisher(namespace: str) -> AwsMetricPublisher:
    "CloudWatch publisher for the namespace defined above"
    return AwsMetricPublisher(
        namespace, "fake access key", "fake secret access key", "us-east-1"
    )


@pytest.fixture
def cw_retriever(namespace: str) -> AWSMetricRetriever:
    "Cloudwatch retriever for the namespace defined above"
    return AWSMetricRetriever(
        namespace, "fake access key", "fake secret access key", "us-east-1"
    )


@pytest.fixture
def counting_metric() -> CounterMetric:
    return CounterMetric("test_counter", "Count")


@pytest.fixture
def timing_metric() -> TimingMetric:
    return TimingMetric("test_timer", "Seconds")


@pytest.fixture(autouse=True)
def sleep_a_second():
    "We want to wait a second after every CW test to ensure metrics are separate"
    time.sleep(1)

from datetime import datetime, timedelta
from pathlib import Path
from hamcrest import (
    assert_that,
    equal_to,
    has_length,
    greater_than_or_equal_to,
    less_than_or_equal_to,
    contains_string,
)
from mypy_boto3_s3 import Client
from switcheroo import paths
from switcheroo.ssh import MetricConstants
from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from metric_system.functions.file_metric_publisher import FileMetricPublisher
from tests.test_cloud_watch.retrievers import FileMetricRetriever


def test_file_metrics_publish_with_file_key_publisher(
    file_key_publisher: FileKeyPublisher,
    file_metric_publisher: FileMetricPublisher,
    file_metric_retriever: FileMetricRetriever,
    some_host: str,
    some_name: str,
    ssh_temp_path: Path,
):
    # publish the SSH keys and metrics
    start_time = datetime.now()
    current_time = datetime.now().replace(microsecond=0)
    key, _ = file_key_publisher.publish_key(
        host=some_host,
        user=some_name,
        metric_publisher=file_metric_publisher,
    )
    end_time = datetime.now()
    # check if counter metric published
    counter_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.COUNTER_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Count",
    )
    assert_that(counter_metric_data.data_points, has_length(1))
    actual_key_count = counter_metric_data.data_points[0].value
    assert_that(actual_key_count, equal_to(1))
    # check if timing metric published
    timing_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.TIMING_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Seconds",
    )
    assert_that(timing_metric_data.data_points, has_length(1))
    expected_max_time = (datetime.now() + timedelta(seconds=2)).replace(microsecond=0)
    assert_that(
        timing_metric_data.data_points[0].timestamp,
        greater_than_or_equal_to(current_time),
    )
    assert_that(
        timing_metric_data.data_points[0].timestamp,
        less_than_or_equal_to(expected_max_time),
    )
    # check if keys published
    public_key_path = paths.local_public_key_loc(some_host, some_name, ssh_temp_path)
    with open(public_key_path, encoding="utf-8") as public_key_file:
        file_contents = public_key_file.read()
        assert_that(file_contents, contains_string(key.public_key.byte_data.decode()))


def test_file_metrics_publish_with_s3_key_publisher(
    s3_key_publisher: S3KeyPublisher,
    file_metric_publisher: FileMetricPublisher,
    file_metric_retriever: FileMetricRetriever,
    some_host: str,
    some_name: str,
    s3_client: Client,
    s3_bucket: str,
):
    # publish the SSH keys and metrics
    start_time = datetime.now()
    current_time = datetime.now().replace(microsecond=0)
    key, _ = s3_key_publisher.publish_key(
        host=some_host,
        user=some_name,
        metric_publisher=file_metric_publisher,
    )
    end_time = datetime.now()
    # check if counter metric published
    counter_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.COUNTER_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Count",
    )
    assert_that(counter_metric_data.data_points, has_length(1))
    actual_key_count = counter_metric_data.data_points[0].value
    assert_that(actual_key_count, equal_to(1))
    # check if timing metric published
    timing_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.TIMING_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Seconds",
    )
    assert_that(timing_metric_data.data_points, has_length(1))
    expected_max_time = (datetime.now() + timedelta(seconds=2)).replace(microsecond=0)
    assert_that(
        timing_metric_data.data_points[0].timestamp,
        greater_than_or_equal_to(current_time),
    )
    assert_that(
        timing_metric_data.data_points[0].timestamp,
        less_than_or_equal_to(expected_max_time),
    )
    # check if keys published
    key_loc = paths.cloud_public_key_loc(some_host, some_name)
    file = s3_client.get_object(Bucket=s3_bucket, Key=str(key_loc))
    file_data = file["Body"].read()
    contents = file_data.decode("utf-8")
    assert_that(contents, contains_string(key.public_key.byte_data.decode()))

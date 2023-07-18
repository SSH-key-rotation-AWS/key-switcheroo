from datetime import datetime, timezone, timedelta
from hamcrest import (
    assert_that,
    equal_to,
    has_length,
    greater_than_or_equal_to,
    less_than_or_equal_to,
)
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
):
    #publish the SSH keys and metrics
    start_time = datetime.now(timezone.utc)
    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    file_key_publisher.publish_key(some_host, some_name, file_metric_publisher)
    end_time = datetime.now(timezone.utc)
    #check if counter metric published
    counter_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.COUNTER_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Count",
    )
    assert_that(counter_metric_data.data_points, has_length(1))
    actual_key_count = counter_metric_data.data_points[0].value
    assert_that(actual_key_count, equal_to(1))
    #check if timing metric published
    timing_metric_data = file_metric_retriever.retrieve_metric_data(
        metric_name=MetricConstants.TIMING_METRIC_NAME,
        start_time=start_time,
        end_time=end_time,
        unit="Seconds",
    )
    assert_that(timing_metric_data.data_points, has_length(1))
    expected_max_time = (datetime.now(timezone.utc) + timedelta(seconds=2)).replace(
        microsecond=0
    )
    assert_that(timing_metric_data.timestamp, greater_than_or_equal_to(current_time))
    assert_that(timing_metric_data.timestamp, less_than_or_equal_to(expected_max_time))


def test_file_metrics_publish_with_s3_key_publisher(
        s3_key_publisher: S3KeyPublisher,
        file_metric_publisher: FileMetricPublisher,
        file_metric_retriever: FileMetricRetriever,
        some_host: str,
        some_name: str,
):
    # publish the SSH keys and metrics
    start_time = datetime.now(timezone.utc)
    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    s3_key_publisher.publish_key(some_host, some_name, file_metric_publisher)
    end_time = datetime.now(timezone.utc)
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
    expected_max_time = (datetime.now(timezone.utc) + timedelta(seconds=2)).replace(
        microsecond=0
    )
    assert_that(timing_metric_data.timestamp, greater_than_or_equal_to(current_time))
    assert_that(timing_metric_data.timestamp, less_than_or_equal_to(expected_max_time))

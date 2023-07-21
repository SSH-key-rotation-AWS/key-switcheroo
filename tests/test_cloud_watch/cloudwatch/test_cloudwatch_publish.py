import time
from datetime import datetime, timezone, timedelta
from hamcrest import (
    assert_that,
    equal_to,
    has_length,
    greater_than_or_equal_to,
    less_than_or_equal_to,
)
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher
from metric_system.functions.metrics import CounterMetric
from tests.test_cloud_watch.retrievers.cloudwatch import AWSMetricRetriever


def test_publish_count(
    cw_publisher: AwsMetricPublisher,
    cw_retriever: AWSMetricRetriever,
    counting_metric: CounterMetric,
):
    "Publish a few values to cloudwatch and retrieve"
    # Store the current time - know when to get the metrics from
    current_time = datetime.now(timezone.utc)
    # Publish values 0-5
    for _ in range(0, 5):
        counting_metric.increment()
        cw_publisher.publish_metric(counting_metric)
        time.sleep(1)
    # Store end time
    end_time = datetime.now(timezone.utc)
    time.sleep(1)
    # Retrieve the metric datapoints
    retrieved_data = cw_retriever.retrieve_metric_data(
        metric_name=counting_metric.name,
        start_time=current_time,
        end_time=end_time,
        unit="Seconds",
    )
    expected_datapoints = set(range(1, 6))
    actual_datapoints = set(
        map(lambda datapoint: datapoint.value, retrieved_data.data_points)
    )
    assert_that(actual_datapoints, equal_to(expected_datapoints))


def test_publish_time(
    cw_publisher: AwsMetricPublisher,
    cw_retriever: AWSMetricRetriever,
    counting_metric: CounterMetric,
):
    """The AWS publisher should publish metric at the timestamp of when publish is called."""
    # AWS timestamps do not have microseconds, so we'll floor the time to the nearest second
    # We cant get the time exactly, but a leeway of 3 seconds should do, even if floored
    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    expected_max_time = (datetime.now(timezone.utc) + timedelta(seconds=3)).replace(
        microsecond=0
    )
    # Publish the metric
    cw_publisher.publish_metric(counting_metric)
    time.sleep(1)
    retrieved_data = cw_retriever.retrieve_metric_data(
        metric_name=counting_metric.name,
        start_time=current_time,
        end_time=expected_max_time,
        unit=counting_metric.unit,
    )
    # First ensure this is the metric we published - didn't pick up any extras
    assert_that(retrieved_data.data_points, has_length(1))
    retrieved_metric = retrieved_data.data_points[0]
    # Ensure value is the one we published
    assert_that(retrieved_metric.value, equal_to(counting_metric.value))
    # Ensure that the timeframe is within our bounds
    assert_that(retrieved_metric.timestamp, greater_than_or_equal_to(current_time))
    assert_that(retrieved_metric.timestamp, less_than_or_equal_to(expected_max_time))

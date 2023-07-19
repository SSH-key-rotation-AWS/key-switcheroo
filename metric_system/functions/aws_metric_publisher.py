"""AWS metric publisher"""
from datetime import datetime, timezone
import boto3
from botocore.exceptions import BotoCoreError
from mypy_boto3_cloudwatch import Client
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.metric import Metric


class AwsMetricPublisher(MetricPublisher):
    """Publishes Metric-specific data"""

    def __init__(self, name_space: str):
        """Instantiate the AWSMetricPublisher object.

        Args:
            name_space (str): The namespace of the metric.
        """
        try:
            self._name_space: str = name_space
            self.cloud_watch: Client = boto3.client("cloudwatch")  # type: ignore #pylint: disable = line-too-long
        except BotoCoreError as aws_error:
            raise RuntimeError("Something went wrong with AWS cloudWatch") from aws_error  # type: ignore #pylint: disable = line-too-long

    def publish_metric(self, metric: Metric):
        """Publishes a metric to CloudWatch.

        Args:
            metric (Metric): The metric object to be published.
        """

        metric_name = metric.name
        metric_value = metric.value
        metric_unit = metric.unit
        try:
            self.cloud_watch.put_metric_data(
                Namespace=self._name_space,
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Timestamp": datetime.now(timezone.utc),
                        "Unit": metric_unit,
                        "Value": metric_value,
                        "StorageResolution": 1,
                    },
                ],
            )
        except BotoCoreError as aws_error:
            raise RuntimeError("Something went wrong when Publishing A metric") from aws_error  # type: ignore #pylint: disable = line-too-long

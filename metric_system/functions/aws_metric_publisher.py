"""AWS metric publisher"""
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from mypy_boto3_cloudwatch import Client
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.metric import Metric


class AwsMetricPublisher(MetricPublisher):
    """Publishes Metric-specific data"""

    def __init__(
        self, name_space: str, access_key: str, secret_access_key: str, region: str
    ):
        """Instantiate the AWSMetricPublisher object.

        Args:
            name_space (str): The namespace of the metric.
        """
        self._name_space: str = name_space
        self._test_credentials(
            access_key=access_key, secret_access_key=secret_access_key, region=region
        )
        # Validate credentials
        self._cloud_watch: Client = boto3.client(  # type: ignore #pylint: disable = line-too-long
            "cloudwatch",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )

    def publish_metric(self, metric: Metric):
        """Publishes a metric to CloudWatch.

        Args:
            metric (Metric): The metric object to be published.
        """
        try:
            metric_name = metric.name
            metric_value = metric.value
            metric_unit = metric.unit

            self._cloud_watch.put_metric_data(
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
            raise RuntimeError(
                "An error occured when publishing the metric"
            ) from aws_error

    def _test_credentials(self, access_key: str, secret_access_key: str, region: str):
        sts_client = boto3.client(  # type: ignore
            "sts",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        try:
            sts_client.get_caller_identity()
        except ClientError as exc:
            raise RuntimeError(
                "Invalid AWS credentials were provided to the metric publisher"
            ) from exc

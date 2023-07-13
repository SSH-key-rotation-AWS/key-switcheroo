"""AWS metric publisher"""
from datetime import datetime
import boto3
from mypy_boto3_cloudwatch import Client
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.metric import Metric


class AwsMetricPublisher(MetricPublisher):
    """Publishes Metric-specific data"""

    def __init__(self, name_space: str, instance_id: str, aws_region: str):
        """Instantiate the AWSMetricPublisher object.

        Args:
            name_space (str): The namespace of the metric.
            instance_id (str): The ID of the instance associated with the metric.
            aws_region (str): The AWS region to use for CloudWatch.
        """
        self._name_space: str = name_space
        self.cloud_watch: Client = boto3.client("cloudwatch", region_name=aws_region)  # type: ignore #pylint: disable = line-too-long
        self._instance_id: str = instance_id
        self.time_of_init: datetime = datetime.now()

    def publish_metric(self, metric: Metric):
        """Publishes a metric to CloudWatch.

        Args:
            metric (Metric): The metric object to be published.
        """

        metric_name = metric.name
        metric_value = metric.value
        metric_unit = metric.unit

        self.cloud_watch.put_metric_data(
            Namespace=self._name_space,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [
                        {"Name": metric_name + "AWS_MetricPublisher", "Value": "AWS"},
                    ],
                    "Unit": metric_unit,
                    "Value": metric_value,
                },
            ],
        )

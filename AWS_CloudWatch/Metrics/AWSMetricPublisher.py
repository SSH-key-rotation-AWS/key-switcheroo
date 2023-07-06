"""AWS metric publisher """
from os import name
import time
from contextlib import contextmanager
import boto3

from AWS_CloudWatch.Metrics.general_metrics import general_metrics


class AWSMetricPublisher(general_metrics):
    """cloud_watch class.
    Stores:
    Name space AWS cloud_watch will publish the metrics to.
    Region the cloud_watch resource will be placed on."""

    def __init__(self,instance_id:str, name_space:str, aws_region:str):
        """Name space represents the title where under all metrics will be published to.
        region represents the region AWS CloudWatch resource should be located"""
        super().__init__(name_space = name_space, instance_id=instance_id)
        self._aws_region = aws_region
        self.cloud_watch = boto3.client("cloudwatch", region_name=self._aws_region)



    @contextmanager
    def timeit_and_publish(self, metric_name: str):
        """A key generation metric context manager to calculate
        the time it took for a key to be generated
        and publish metric to AWS CloudWatch"""
        start_time = 0
        try:
            start_time = time.time()
            yield 
        finally:
            end_time = time.time() - start_time     
        self.cloud_watch.put_metric_data(
                Namespace=self._name_space,
                MetricData=[
                    {
                        "MetricName": "Time to generate key",
                        "Dimensions": [
                            {"Name": metric_name, "Value": self._instance_id},
                        ],
                        "Unit": "Seconds",
                        "Value": end_time,
                    },
                ],
            )

    def _count_metric(self, metric_name: str):
        """Function that publishes the key count
        to AWS CloudWatch under the 'key count' metric,
        within the initialized namespace"""
        self._key_count = self._key_count+1
        
        self.cloud_watch.put_metric_data(
            Namespace=self._name_space,
            MetricData=[
                {
                    "MetricName": "Key Count",
                    "Dimensions": [
                        {"Name": metric_name, "Value": self._instance_id},
                    ],
                    "Unit": "Count",
                    "Value": self._key_count,
                }
            ],
        )

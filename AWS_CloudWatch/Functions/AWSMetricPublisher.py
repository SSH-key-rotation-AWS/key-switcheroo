"""AWS metric publisher """
import time
from contextlib import contextmanager
from typing_extensions import override
import boto3
from Metric import Metric
from Metrics import CounterMetric, TimingMetric
from MetricPublisher import MetricPublisher
import json


class AWSMetricPublisher(MetricPublisher):
    """cloud_watch class.
    Stores:
    Name space AWS cloud_watch will publish the metrics to.
    Region the cloud_watch resource will be placed on."""

    def __init__(self,instance_id:str, name_space:str, aws_region:str ):
        """Name space represents the title where under all metrics will be published to.
        region represents the region AWS CloudWatch resource should be located"""
        self._name_space = name_space
        self._aws_region = aws_region
        self.cloud_watch = boto3.client("cloudwatch", region_name=self._aws_region)
        self._instance_id = instance_id
        self.counter_metric = CounterMetric(self._name_space)
        self.time_to_generate_key_metric = TimingMetric(self._name_space)


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


    def inc_key_count(self, metric_name: str):
        """Function that publishes the key count
        to AWS CloudWatch under the 'key count' metric,
        within the initialized namespace"""

        count_data = self.counter_metric.publish_metric(metric_name=metric_name)
        data_dict = json.loads(str(count_data))
        count = data_dict["Metric Data"]["Value"]
        

        self.cloud_watch.put_metric_data( 
            Namespace=self._name_space,
            MetricData=[
                {
                    "MetricName": "Key Count",
                    "Dimensions": [
                        {"Name": metric_name, "Value": self._instance_id},
                    ],
                    "Unit": "Count",
                    "Value": count,
                }
            ],
        )

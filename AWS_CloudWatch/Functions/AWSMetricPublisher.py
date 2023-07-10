"""AWS metric publisher """
import boto3
from Metric import Metric
from  MetricPublisher import MetricPublisher



class AWSMetricPublisher(MetricPublisher):
    """Publishes Metric specificed data"""

    def __init__(
        self, name_space: str, instance_id: str, aws_region:str
    ):
        self.name_space = name_space
        self.cloud_watch = boto3.client("cloudwatch", region_name=aws_region)
        self._instance_id = instance_id

    def publish_metric(self,metric:Metric):

        metric_name = metric.get_metric_name()
        metric_value = metric.get_metric_value()
        metric_unit = metric.get_metric_unit()
        
        self.cloud_watch.put_metric_data(
            Namespace=self.name_space,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [
                        {"Name": "AWS_MetricPublisher","Value": self._instance_id},
                    ],
                    "Unit": metric_unit,
                    "Value": metric_value,
                },
            ],
        )

        

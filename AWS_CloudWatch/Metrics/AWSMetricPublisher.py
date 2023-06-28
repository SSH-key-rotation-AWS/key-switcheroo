"""AWS metric publisher """
import time
from contextlib import contextmanager
import boto3

class AWSMetricPublisher:
    """cloud_watch class. 
    Stores:
    Name space AWScloud_watch will publish the metrics to. 
    Region the cloud_watch resource will be placed on. """
    def __init__(self, aws_region: str, name_space_name: str,instance_id:str):
        """Name space represents the title where under all metrics will be published to.
        region represents the region aws cloudwatch resource should be located"""
        self.region = aws_region
        self.generated_keys = 0
        self.cloud_watch = boto3.client('cloudwatch', region_name=self.region)
        self.name_space = name_space_name
        self.instance_id = instance_id

    @contextmanager
    def timeit_and_publish(self,metric_name:str):
        """A  key generation metric 
        context manager , to calcualate 
        the time it took for a a key to be generated 
        and publish metric to AWS cloudwatch"""
        start_time = 0
        try:
            start_time = time.time()
            yield
        finally:
            end_time = time.time() - start_time
            response = self.cloud_watch.put_metric_data(
                Namespace=self.name_space,
                MetricData=[
                    {
                        "MetricName": "Time to generate key",
                        "Dimensions": [
                            {
                                "Name": metric_name,
                                "Value": self.instance_id
                            },
                        ],
                        "Unit": "Seconds",
                        "Value": end_time,
                    },
                ],
                
            )
            print(response) 

    def inc_count_metric(self,metric_name:str):
        """Function that publishes the key count 
        to AWS cloudwatch under the "key count" metric, 
        under the initialized namespace """
        self.generated_keys += 1
        response = self.cloud_watch.put_metric_data(
            Namespace=self.name_space,
            MetricData=[
                {
                    "MetricName": "Key Count",
                    "Dimensions": [
                        {
                         "Name": metric_name, 
                         "Value": self.instance_id
                        },
                    ],
                    "Unit": "Count",
                    "Value": self.generated_keys,
                }
            ],
        )
        return response
    
import boto3
from contextlib import contextmanager
import time 

class AWS_Cloudwatch:
    def __init__(self,aws_region:str,name_space_name:str):
        self.region = aws_region
        self.generated_keys = 0
        self.cloudWatch = boto3.client('cloudwatch',region_name=self.region)
        self.name_space = name_space_name


    @contextmanager
    def key_generation_time_metric(self,instance_id:str,metric_name:str):
        start_time = 0
        try:
            start_time = time.time()
            yield
        finally:
            end_time = time.time() - start_time
            self.cloudWatch.put_metric_data(
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': 'Key Generation Time Metric Instance',
                        'Value': instance_id
                    },
                ],
                'Unit': 'Seconds',
                'Value': end_time
            },
        ],
        Namespace= self.name_space
)   
    
    def key_count_metric(self,metric_name:str,instance_id:str):
        self.generated_keys +=1
        response = self.cloudWatch.put_metric_data(
            Namespace=self.name_space,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': [
                        {
                            'Name':'Key Count Metric Instance',
                            'Value':instance_id
                        },
                    ],
                    'Unit':'Count',
                    'Value':self.generated_keys,
                }
            ],
        )
        












    

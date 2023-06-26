import boto3
from contextlib import contextmanager 
from time import time


@contextmanager
def key_generation_time_metric(instance_id:str,aws_region:str):
    cloudwatch = boto3.client('cloudwatch',region_name=aws_region)
    start_time = 0
    try:
        start_time = time.time()
        yield
    finally:
        end_time = time.time() - start_time
        cloudwatch.put_metric_data(
    MetricData=[
        {
            'MetricName': 'Time_to_create_cs_key',
            'Dimensions': [
                {
                    'Name': 'instance_id',
                    'Value': instance_id
                },
            ],
            'Unit': 'Seconds',
            'Value': end_time
        },
    ],
    Namespace='KEY_TIME_GENERATION'
)


with key_generation_time_metric("test","us-west-1"):
    print("Here is the key generation Logic")










    

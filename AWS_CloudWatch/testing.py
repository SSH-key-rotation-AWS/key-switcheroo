import boto3
import datetime

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch',region_name='us-east-1')

# List metrics through the pagination interface
paginator = cloudwatch.get_paginator('list_metrics')
for response in paginator.paginate(
                                   MetricName='Key Count',
                                   Namespace='TESTING NAMESPACE ZdBAYSBWLt'):
    print(response['Metrics'])



print("-------------------------------")
response = cloudwatch.get_metric_statistics(
            Namespace='TESTING NAMESPACE ZdBAYSBWLt',
            MetricName='Key Count',
            Dimensions=[
                {
                    "Name": 'Key Count Metric :wdgkgfLCnT',
                    "Value":'TEST INSTANCE DQLthPtvus',
                },
            ],

            StartTime=datetime.datetime(year=2023,month=6,day=1),
            EndTime=datetime.datetime(year=2023,month=6,day=30),
            Period=86460,
            Statistics=[
                "SampleCount",
            ]
    )  

print(response)
            
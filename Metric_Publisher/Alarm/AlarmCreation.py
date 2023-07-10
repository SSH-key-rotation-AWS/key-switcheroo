import boto3
"""
def create_key_count_alarm(self,metric_name:str,threshold:int,alarm_name:str,alarm_description:str):
    response = client.put_metric_alarm(
AlarmName=alarm_name,
AlarmDescription=alarm_description,
ActionsEnabled=True|False,
OKActions=[
    'string',
],
AlarmActions=[
    'string',
],
InsufficientDataActions=[
    'string',
],
MetricName='string',
Namespace='string',
Statistic='SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',
ExtendedStatistic='string',
Dimensions=[
    {
        'Name': 'string',
        'Value': 'string'
    },
],
Period=123,
Unit='Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None',
EvaluationPeriods=123,
DatapointsToAlarm=123,
Threshold=123.0,
ComparisonOperator='GreaterThanOrEqualToThreshold'|'GreaterThanThreshold'|'LessThanThreshold'|'LessThanOrEqualToThreshold'|'LessThanLowerOrGreaterThanUpperThreshold'|'LessThanLowerThreshold'|'GreaterThanUpperThreshold',
TreatMissingData='string',
EvaluateLowSampleCountPercentile='string',
Metrics=[
    {
        'Id': 'string',
        'MetricStat': {
            'Metric': {
                'Namespace': 'string',
                'MetricName': 'string',
                'Dimensions': [
                    {
                        'Name': 'string',
                        'Value': 'string'
                    },
                ]
            },
            'Period': 123,
            'Stat': 'string',
            'Unit': 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
        },
        'Expression': 'string',
        'Label': 'string',
        'ReturnData': True|False,
        'Period': 123,
        'AccountId': 'string'
    },
],
Tags=[
    {
        'Key': 'string',
        'Value': 'string'
    },
],
ThresholdMetricId='string'
)
    
"""
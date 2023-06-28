
from Metrics.AWSMetricPublisher import AWSMetricPublisher 
import random
import unittest
import string 
import time
import boto3
import datetime

class aws_metric_test(unittest.TestCase):

    
    def setUp(self) -> None:
        self.REGION = "us-east-1"
        self.INSTANCE_ID = "TEST INSTANCE " + self.random_name_generator()
        self.NAME_SPACE= "TESTING NAMESPACE FINAL"
        self.cloud_watch=AWSMetricPublisher(aws_region=self.REGION,name_space_name=self.NAME_SPACE,instance_id=self.INSTANCE_ID)
        self.cloud_get_metric_data = boto3.client('cloudwatch',region_name=self.REGION)

    def random_name_generator(self):
        random_string = ''.join(random.choices(string.ascii_letters, k=10))
        return random_string
    

    def test_key_count_metric(self):
        key_count_metric = "Key Count Metric :"+self.random_name_generator()
        print("in key count metric test...")
        for element in range(10):
            print("Sending :"+str(element)+"Key Count metric")
            time.sleep(5)

            self.cloud_watch.inc_count_metric(metric_name=key_count_metric)

        time.sleep(10)    
        response = self.cloud_get_metric_data.get_metric_statistics(
            Namespace=self.NAME_SPACE,
            MetricName='Key Count',
            Dimensions=[
                {
                    "Name": key_count_metric,
                    "Value": self.INSTANCE_ID,
                },
            ],

            StartTime=datetime.datetime(year=2023,month=6,day=1),
            EndTime=datetime.datetime(year=2023,month=6,day=30),
            Period=86460,
            Unit= 'Count',
            Statistics=[
                "SampleCount",
            ]
    ) 
        
        sample_count = 0
        for r in response['Datapoints']:
            sample_count = (r['SampleCount'])
            metric = (r['Label'])
   
        self.assertEquals(first="Key Count",second=metric)
        self.assertEquals(first=10,second=sample_count)


    def generate_random_integer(self):
        random_ints = []
        for _ in range(5):
            random_ints.append(random.randint(1,50))
        return random_ints
    
    
if __name__ == '__main__':
    unittest.main()



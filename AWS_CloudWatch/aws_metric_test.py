from Metrics.AWSMetricPublisher import AWSMetricPublisher
import random
import unittest
import string
import time
import boto3
import datetime
import math
import random


class aws_metric_test(unittest.TestCase):
    def setUp(self) -> None:
        self.REGION = "us-east-1"
        self.INSTANCE_ID = "TEST INSTANCE " + self.random_name_generator()
        self.NAME_SPACE = "TESTING NAMESPACE FINAL"
        self.cloud_watch = AWSMetricPublisher(
        aws_region=self.REGION,
        name_space_name=self.NAME_SPACE,
        instance_id=self.INSTANCE_ID,
        do_not_enable=False
        )
        self.cloud_get_metric_data = boto3.client("cloudwatch", region_name=self.REGION)

        current_datetime = datetime.datetime.now()
        self.current_time = current_datetime - datetime.timedelta(days=1)
        self.end_date_time = current_datetime + datetime.timedelta(days=1)

    def random_name_generator(self):
        random_string = "".join(random.choices(string.ascii_letters, k=10))
        return random_string

    def test_key_count_metric(self):
        key_count_metric = "Key Count Metric TEST"
        key_amount = random.randint(1, 10)
        print("in key count metric test...")
        for element in range(key_amount):
            print("Sending :" + str(element+1) + " Key Count metric")
            time.sleep(5)

            self.cloud_watch.inc_count_metric(metric_name=key_count_metric)

        time.sleep(10)
        response = self.cloud_get_metric_data.get_metric_statistics(
            Namespace=self.NAME_SPACE,
            MetricName="Key Count",
            Dimensions=[
                {
                    "Name": key_count_metric,
                    "Value": self.INSTANCE_ID,
                },
            ],
            StartTime=self.current_time,
            EndTime=self.end_date_time,
            Period=86460,
            Unit="Count",
            Statistics=[
                "SampleCount",
            ],
        )

        sample_count = 0
        for json_response in response["Datapoints"]:
            sample_count = json_response["SampleCount"]

            

        self.assertEqual(first=key_amount, second=sample_count)

    def generate_random_integer(self):
        random_ints = []
        for _ in range(5):
            random_ints.append(random.randint(1, 50))
        return random_ints


    def test_time_it_and_publish(self):
        metric_name = "Time to Generate key metric TEST"
        time_to_generate_key = random.randint(1,10)
        for _ in range(5):
            with self.cloud_watch.timeit_and_publish(metric_name=metric_name):
                print("In Testing method of timeit_and_publish function.... ")
                time.sleep(time_to_generate_key)
        
        response = self.cloud_get_metric_data.get_metric_statistics(
            Namespace=self.NAME_SPACE,
            MetricName="Time to generate key",
            Dimensions=[
                {
                    "Name": metric_name,
                    "Value": self.INSTANCE_ID,
                },
            ],
            StartTime=self.current_time, 
            EndTime=self.end_date_time,
            Period=86460,
            Unit="Seconds",
            Statistics=[
                "Average",
            ],
        )
        
        average_count = 0
        for json_response in response["Datapoints"]:
            average_count = json_response["Average"]

        self.assertEqual(first=time_to_generate_key, second=math.floor(average_count))

if __name__ == "__main__":
    unittest.main()

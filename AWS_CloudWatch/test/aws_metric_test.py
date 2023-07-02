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
        self.INSTANCE_ID = "TEST INSTANCE " + self._random_name_generator()
        self.NAME_SPACE = "TESTING NAMESPACE FINAL"
        self.cloud_watch = AWSMetricPublisher(
            aws_region=self.REGION,
            name_space_name=self.NAME_SPACE,
            instance_id=self.INSTANCE_ID,
            do_not_enable=False,
        )
        self.cloud_get_metric_data = boto3.client("cloudwatch", region_name=self.REGION)

        current_datetime = datetime.datetime.now()
        self.current_time = current_datetime - datetime.timedelta(days=1)
        self.end_date_time = current_datetime + datetime.timedelta(days=1)

    def _random_name_generator(self):
        random_string = "".join(random.choices(string.ascii_letters, k=10))
        return random_string

    def test_key_count_metric(self):
        key_count_metric = "Key Count Metric TEST"
        key_amount = random.randint(1, 10)
        print("\nin key count metric test...")
        for element in range(key_amount):
            with self.cloud_watch.metric_publisher(key_count=True,key_count_metric_name=key_count_metric,key_publish_time=False,key_publish_time_metric_name="None"):
                print("Sending :" + str(element + 1) + " Key Count metric")
                time.sleep(5)

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
                "Sum",
            ],
        )
    

        sum = 0
        for json_response in response["Datapoints"]:
            sum = json_response["Sum"]

        self.assertEqual(first=key_amount, second=sum)

    def generate_random_integer(self):
        random_ints = []
        for _ in range(5):
            random_ints.append(random.randint(1, 50))
        return random_ints

    def test_time_it_and_publish(self):
        metric_name = "Time to Generate key metric TEST"
        time_to_generate_key = random.randint(1, 10)
        for _ in range(5):
            with self.cloud_watch.metric_publisher(key_count=False,key_count_metric_name="None",key_publish_time=True,key_publish_time_metric_name=metric_name):
                print("\nIn Testing method of timeit_and_publish function.... ")
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

    def test_time_and_key_count(self):
        test_time_metric = "Test time metrics"
        test_key_count = "Test Key Count Metrics"
        key_count_val = random.randint(1,10)
        time_to_generate_key = random.randint(1, 10)

        for _ in range(key_count_val):
            with self.cloud_watch.metric_publisher(key_count=True,key_count_metric_name=test_key_count,key_publish_time=True,key_publish_time_metric_name=test_time_metric):
                print("\nIn Testing method of Metric Publisher function.... ")
                time.sleep(time_to_generate_key)
        time.sleep(10)
        
        key_time_response = self.cloud_get_metric_data.get_metric_statistics(
            Namespace=self.NAME_SPACE,
            MetricName="Time to generate key",
            Dimensions=[
                {
                    "Name": test_time_metric,
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

        key_count_response = self.cloud_get_metric_data.get_metric_statistics(
            Namespace=self.NAME_SPACE,
            MetricName="Key Count",
            Dimensions=[
                {
                    "Name":test_key_count ,
                    "Value": self.INSTANCE_ID,
                },
            ],
            StartTime=self.current_time,
            EndTime=self.end_date_time,
            Period=86460,
            Unit="Count",
            Statistics=[
                "Sum",
            ],
        )

        average_count = 0
        for json_response in key_time_response["Datapoints"]:
            average_count = json_response["Average"]

        sum = 0
        for json_response in key_count_response["Datapoints"]:
            sum = json_response["Sum"]

        self.assertEqual(first=key_count_val, second=sum)
        self.assertEqual(first=time_to_generate_key, second=math.floor(average_count))

    

        


if __name__ == "__main__":
    unittest.main()

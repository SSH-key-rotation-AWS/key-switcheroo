"""
Module Docstring: Test File Publishing API
"""

import json
import unittest
import random
import time
import math
import os
from hamcrest import assert_that, equal_to
from tests.test_cloud_watch.FileMetricPublisher import FileMetricPublisher
from Metric_Publisher.Functions.Metrics import CounterMetric, TimingMetric


class publisher_metric_api_test(unittest.TestCase):
    """
    Test to verify Publisher and metric API
    """

    def setUp(self) -> None:
        self.publisher = FileMetricPublisher(
            name_space="Test NameSpace", instance_id="DothansMac"
        )
        self.inc_key_count_metric = CounterMetric(
            metric_name="File Test Counter", unit="Count"
        )
        self.time_metric = TimingMetric(metric_name="File test Timing", unit="Seconds")
        self.time_to_generate_int = random.randint(1, 10)
        self.count_int = random.randint(1, 10)
        self._file_location = (
            os.getcwd() + "/tests/test_cloud_watch/FileMetricPublisherTest"
        )

    def test_inc_count(self):
        """
        Test increment count
        """
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
        data = self.retrieve_json_data(self._file_location + "/test_inc_count.json")
        val = data["Metric Data"]["Value"]
        assert_that(self.count_int, equal_to(val))

    def test_time_to_gen_key(self):
        """
        Test time to generate key
        """
        self.time_key()
        self.publisher.publish_metric(self.time_metric)
        data = self.retrieve_json_data(self._file_location + "/test_timeit.json")
        val = data["Metric Data"]["Value"]
        assert_that(self.time_to_generate_int, equal_to(math.floor(val)))

    def increment_count_metric(self):
        """
        Simulate key count metrics
        """
        for i in range(self.count_int):
            self.inc_key_count_metric.inc_count_metric()
            print("Currently incremented by: " + str(i + 1))

    def time_key(self):
        """
        Simulate time to generate key
        """
        with self.time_metric.timeit_metric():
            time.sleep(self.time_to_generate_int)

    def retrieve_json_data(self, file_location):
        """
        Retrieve JSON data from file
        """
        with open(file_location, "r") as file:
            return json.load(file)


if __name__ == "__main__":
    unittest.main()

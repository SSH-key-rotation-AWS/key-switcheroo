"""
Module Docstring: Test File Publishing API
"""
import unittest
import random
import time
import math
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta
from pathlib import Path
from hamcrest import assert_that, equal_to, has_length
from mypy_boto3_cloudwatch.literals import StandardUnitType
from metric_system.functions.file_metric_publisher import FileMetricPublisher
from metric_system.functions.metric import MetricData
from metric_system.functions.metrics import TimingMetric, CounterMetric
from tests.test_cloud_watch.retrievers import FileMetricRetriever


class PublisherAPITest(unittest.TestCase):
    """
    Test to verify Publisher and metric API
    """

    def setUp(self) -> None:
        temp_dir = TemporaryDirectory(  # pylint: disable=consider-using-with
            prefix="switcheroo-cloudwatch"
        )
        self.enterContext(temp_dir)
        self._file_location = Path(temp_dir.name)
        self.publisher = FileMetricPublisher(metric_dir=self._file_location)
        self.retriever = FileMetricRetriever(metric_dir=self._file_location)
        self.inc_key_count_metric = CounterMetric(
            metric_name="File Test Counter", unit="Count"
        )
        self.time_metric = TimingMetric(metric_name="File test Timing", unit="Seconds")
        self.time_to_generate_int = random.randint(1, 10)
        self.count_int = random.randint(1, 10)

    def test_inc_count(self):
        """
        Test increment count
        """
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
        data: MetricData | None = self.retrieve_all_test_data(
            self.inc_key_count_metric.name, "Count"
        )
        assert data is not None
        assert_that(self.count_int, equal_to(data.data_points[0].value))

    def test_time_to_gen_key(self):
        """
        Test time to generate key
        """
        self.time_key()
        self.publisher.publish_metric(self.time_metric)
        data = self.retrieve_all_test_data(self.time_metric.name, "Seconds")
        assert data is not None
        assert_that(
            self.time_to_generate_int, equal_to(math.floor(data.data_points[0].value))
        )

    def test_multiple_data_points(self):
        """
        Tests if we can publish multiple data points
        """
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
        data = self.retrieve_all_test_data(self.inc_key_count_metric.name, "Count")
        assert data is not None
        assert_that(data.data_points, has_length(1))
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
        data2 = self.retrieve_all_test_data(self.inc_key_count_metric.name, "Count")
        assert data2 is not None
        assert_that(data2.data_points, has_length(2))
        assert_that(data.data_points[0].value, equal_to(self.count_int))
        assert_that(data2.data_points[1].value, equal_to(self.count_int * 2))

    def test_time_range(self):
        """Can we retrieve from the file publisher within a given time range?"""
        for _ in range(0, 4):
            time.sleep(2)
            self.publisher.publish_metric(self.inc_key_count_metric)
        # Get all data
        all_data = self.retrieve_all_test_data(
            self.inc_key_count_metric.name, unit="Seconds"
        ).data_points
        # Get their timestamps
        data_timestamps = list(map(lambda datapoint: datapoint.timestamp, all_data))
        # Retrieve between the middle 2 timestamps
        middle_data = self.retriever.retrieve_metric_data(
            self.inc_key_count_metric.name,
            start_time=data_timestamps[1],
            end_time=data_timestamps[2],
            unit="Count",
        ).data_points
        assert_that(middle_data[0], equal_to(all_data[1]))
        assert_that(middle_data[1], equal_to(all_data[2]))

    def increment_count_metric(self):
        """
        Simulate key count metrics
        """
        for _ in range(self.count_int):
            self.inc_key_count_metric.increment()

    def time_key(self):
        """
        Simulate time to generate key
        """
        with self.time_metric.timeit():
            time.sleep(self.time_to_generate_int)

    def retrieve_all_test_data(
        self, metric_name: str, unit: StandardUnitType
    ) -> MetricData:
        # Presumably our tests dont take a day to finish, so this should get all data
        return self.retriever.retrieve_metric_data(
            metric_name,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            unit=unit,
        )


if __name__ == "__main__":
    unittest.main()

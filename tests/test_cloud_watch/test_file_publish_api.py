"""
Module Docstring: Test File Publishing API
"""
import unittest
import random
import time
import math
from tempfile import TemporaryDirectory
from pathlib import Path
from hamcrest import assert_that, equal_to, has_length
from metric_system.functions.file_metric_publisher import FileMetricPublisher
from metric_system.functions.metric import MetricJsonData
from metric_system.functions.metrics import TimingMetric, CounterMetric


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
        data: MetricJsonData | None = self.publisher.retrieve_metric_data(
            self.inc_key_count_metric.name
        )
        assert data is not None
        assert_that(self.count_int, equal_to(data.data_points[0].value))

    def test_time_to_gen_key(self):
        """
        Test time to generate key
        """
        self.time_key()
        self.publisher.publish_metric(self.time_metric)
        data = self.publisher.retrieve_metric_data(self.time_metric.name)
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
        data = self.publisher.retrieve_metric_data(self.inc_key_count_metric.name)
        assert data is not None
        assert_that(data.data_points, has_length(1))
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
        data2 = self.publisher.retrieve_metric_data(self.inc_key_count_metric.name)
        assert data2 is not None
        assert_that(data2.data_points, has_length(2))
        assert_that(data.data_points[0].value, equal_to(self.count_int))
        assert_that(data2.data_points[1].value, equal_to(self.count_int * 2))

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


if __name__ == "__main__":
    unittest.main()

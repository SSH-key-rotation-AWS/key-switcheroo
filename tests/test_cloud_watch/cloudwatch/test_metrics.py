import unittest
import random
import time
import math
from hamcrest import assert_that, equal_to
from metric_system.functions.metrics import TimingMetric, CounterMetric


class MetricsFuncTest(unittest.TestCase):
    def setUp(self) -> None:
        self.counter_metric = CounterMetric("TEST METRIC", unit="Count")
        self.time_metric = TimingMetric("Test Metric", unit="Seconds")
        self.random_count = random.randint(2, 10)
        self.random_time = random.randint(2, 10)

    def test_counter_metric(self):
        for _ in range(self.random_count):
            self.counter_metric.increment()
        assert_that(self.random_count, equal_to(self.counter_metric.value))

    def test_time_metric(self):
        with self.time_metric.timeit():
            print("In Timing Metric")
            time.sleep(self.random_time)
        assert_that(self.random_time, equal_to(math.floor(self.time_metric.value)))


if __name__ == "__main__":
    unittest.main()

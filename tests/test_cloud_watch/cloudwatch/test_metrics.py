import unittest
import random
import time
from hamcrest import assert_that, equal_to, close_to
from metric_system.functions.metrics import TimingMetric, CounterMetric


class MetricsFuncTest(unittest.TestCase):
    def test_increment_count_counter_metric(self):
        random_count = random.randint(2, 10)
        counter_metric = CounterMetric("TEST METRIC", unit="Count")
        for _ in range(random_count):
            counter_metric.increment()
        assert_that(random_count, equal_to(counter_metric.value))

    def test_timeit_in_timing_metric(self):
        random_time = random.randint(2, 10)
        time_metric = TimingMetric("Test Metric", unit="Seconds")
        with time_metric.timeit():
            print("In Timing Metric")
            time.sleep(random_time)
        assert_that(random_time, close_to(time_metric.value,1)) 


if __name__ == "__main__":
    unittest.main()

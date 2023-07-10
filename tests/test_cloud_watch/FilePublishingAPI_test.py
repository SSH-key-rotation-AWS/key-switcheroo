import hamcrest
from FileMetricPublisher import FileMetricPublisher
from AWS_CloudWatch.Functions.Metrics import CounterMetric , TimingMetric
import unittest
from hamcrest import assert_that, equal_to, is_in


class PublisherMetricAPITest(unittest.TestCase):
    """Test to verify Publisher and metric API"""
    def setUp(self) -> None:
        self.publisher = FileMetricPublisher(name_space="Test NameSpace",instance_id="DothansMac")
        self.inc_key_count_metric = CounterMetric(metric_name="File Test Counter",unit="Count")
        self.time_metric = TimingMetric(metric_name="File test Timing",unit="Seconds")

    def test(self):
        """Instantiate Count metric , and use it to publish metrics to File"""
        self.increment_count_metric()
        self.publisher.publish_metric(self.inc_key_count_metric)
    def increment_count_metric(self):
        """Simulate 5 key count metrics"""
        for i in range(5):
            self.inc_key_count_metric.inc_count_metric()
            print("Currently incrmented by :" + str(i) )


if __name__ == '__main__':
    unittest.main()
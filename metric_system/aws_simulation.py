import time
from metric_system.functions.metrics import CounterMetric
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher


class AWSDemo:
    def __init__(self) -> None:
        self.server_a = AwsMetricPublisher(
            "DEMO S3 BUCKET", instance_id="SERVER A", aws_region="us-east-1"
        )
        self.count_metric_server_a = CounterMetric("Count Metric DEMO", "Count")

        self.server_b = AwsMetricPublisher(
            "DEMO S3 BUCKET", instance_id="SERVER B", aws_region="us-east-1"
        )
        self.count_metric_server_b = CounterMetric("Count Metric DEMO", "Count")

        self.server_c = AwsMetricPublisher(
            "DEMO S3 BUCKET", instance_id="SERVER C", aws_region="us-east-1"
        )
        self.count_metric_server_c = CounterMetric("Count Metric DEMO", "Count")

    def publish(self):
        self._increment_count_metric()
        print("Incremented....")

        self.server_a.publish_metric(self.count_metric_server_a)
        time.sleep(100)
        self.server_b.publish_metric(self.count_metric_server_b)
        time.sleep(100)
        self.server_c.publish_metric(self.count_metric_server_c)
        time.sleep(100)

    def _increment_count_metric(self):
        for _ in range(5):
            self.count_metric_server_a.inc_count_metric()
            self.count_metric_server_b.inc_count_metric()
            self.count_metric_server_c.inc_count_metric()


demo = AWSDemo()

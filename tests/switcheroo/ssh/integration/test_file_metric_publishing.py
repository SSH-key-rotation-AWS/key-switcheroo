from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from metric_system.functions.file_metric_publisher import FileMetricPublisher

def test_file_metrics_publish(
        file_key_publisher: FileKeyPublisher,
        file_metric_publisher: FileMetricPublisher,
        some_host: str,
        some_name: str,
):
    file_key_publisher.publish_key(some_host, some_name, file_metric_publisher)

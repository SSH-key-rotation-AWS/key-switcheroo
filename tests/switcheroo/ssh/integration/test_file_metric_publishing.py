from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from metric_system.functions.file_metric_publisher import FileMetricPublisher
#from tests.test_cloud_watch.retrievers import FileMetricRetriever
#from tests.test_cloud_watch.retrievers.cloudwatch import AWSMetricRetriever

def test_file_metrics_publish_with_file_key_publisher(
        file_key_publisher: FileKeyPublisher,
        file_metric_publisher: FileMetricPublisher,
        some_host: str,
        some_name: str,
):
    #publish the SSH keys and metrics
    file_key_publisher.publish_key(some_host, some_name, file_metric_publisher)
    #check if metrics published


def test_file_metrics_publish_with_s3_key_publisher(
        s3_key_publisher: S3KeyPublisher,
        file_metric_publisher: FileMetricPublisher,
        some_host: str,
        some_name: str,
):
    #publish the SSH keys and metrics
    s3_key_publisher.publish_key(some_host, some_name, file_metric_publisher)
    #check if metrics published

from switcheroo.ssh.data_org.publisher import FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher
#from tests.test_cloud_watch.retrievers import FileMetricRetriever
#from tests.test_cloud_watch.retrievers.cloudwatch import AWSMetricRetriever

def test_aws_metrics_publish_with_file_key_publisher(
        file_key_publisher: FileKeyPublisher,
        aws_metric_publisher: AwsMetricPublisher,
        some_host: str,
        some_name: str,
):
    #publish the SSH keys and metrics
    file_key_publisher.publish_key(some_host, some_name, aws_metric_publisher)
    #check if metrics published

def test_aws_metrics_publish_with_s3_key_publisher(
        s3_key_publisher: S3KeyPublisher,
        aws_metric_publisher: AwsMetricPublisher,
        some_host: str,
        some_name: str,
):
    s3_key_publisher.publish_key(some_host, some_name, aws_metric_publisher)
    #check if metrics published

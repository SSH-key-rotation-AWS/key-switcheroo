from pathlib import Path
from argparse import ArgumentParser
from switcheroo.ssh.data_org.publisher import KeyPublisher, FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo import paths
from switcheroo.ssh.constants import NAME_SPACE
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.aws_metric_publisher import AwsMetricPublisher
from metric_system.functions.file_metric_publisher import FileMetricPublisher


def create_argument_parser() -> ArgumentParser:
    # pylint: disable=R0801
    argument_parser = ArgumentParser(
        prog="key_publisher",
        description="Creates public/private SSH keys and publishes "
        + "the public key either locally or to S3 (default is S3)",
        epilog="Thanks for using key_publisher! :)",
    )

    argument_parser.add_argument("hostname")
    argument_parser.add_argument("user")

    argument_parser.add_argument(
        "-ds",
        "--datastore",
        choices=["s3", "local"],
        default="s3",
        help="choose where to store the public key, on S3 or on the local system (default is S3)",
    )

    argument_parser.add_argument(
        "--bucket",
        required=False,
        help="If s3 is selected, the bucket name to store the key in",
    )
    argument_parser.add_argument(
        "--sshdir",
        required=False,
        help="The absolute path to\
            the directory that stores local keys (ie /home/you/.ssh)",
        default=paths.local_ssh_home(),
    )
    argument_parser.add_argument(
        "-m",
        "--metric",
        action="store_true",
        choices=["file", "cloud"],
        required=False,
        help="opt to have metrics published,\
              either to AWS cloudwatch or to the local file system (default is cloud)",
    )
    argument_parser.add_argument(
        "--metricpath",
        required=False,
        help="The absolute path to the directory that stores the metrics",
        default=paths.local_metrics_dir(),
    )

    return argument_parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    key_publisher: KeyPublisher | None = None
    metric_publisher: MetricPublisher | None = None
    if args.datastore == "local":  # If the user chose to store the public key locally
        key_publisher = FileKeyPublisher(Path(args.sshdir))
    else:  # If the user chose to store the public key on S3 or chose to default to S3
        if args.bucket is None:
            parser.error("The s3 option requires a bucket name!")
        key_publisher = S3KeyPublisher(args.bucket, root_ssh_dir=Path(args.sshdir))
    if args.metric: # If the user chose to publish metrics
        if args.metric == "file": #publish to file system
            metric_publisher = FileMetricPublisher(args.metricpath)
        elif args.metric == "cloud": #publish to cloudwatch
            metric_publisher = AwsMetricPublisher(NAME_SPACE, "", "")
        else:
            raise ValueError('Please specify either "file" or "cloud" after the -m/--metric option.')
    assert key_publisher is not None
    key_publisher.publish_key(args.hostname, args.user, metric_publisher=metric_publisher)


if __name__ == "__main__":
    main()

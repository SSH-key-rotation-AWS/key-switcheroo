from pathlib import Path
from argparse import ArgumentParser
from switcheroo.ssh.data_org.publisher import KeyPublisher, FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo import paths
from switcheroo.ssh import MetricConstants
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

    argument_parser.add_argument(
        "hostname",
        help="the hostname of the server",
    )
    argument_parser.add_argument(
        "user",
        help="the username of the connecting client",
    )
    argument_parser.add_argument(
        "-ds",
        "--datastore",
        default="s3",
        choices=["s3", "local"],
        required=False,
        help="choose where to store the public key,\
            on S3 or on the local system (default is S3)",
    )
    argument_parser.add_argument(
        "--bucket",
        required=False,
        help="If s3 is selected, the bucket name to store the key in",
    )
    argument_parser.add_argument(
        "--sshdir",
        default=paths.local_ssh_home(),
        required=False,
        help="The absolute path to\
            the directory that stores local keys (ie /home/you/.ssh)",
    )
    argument_parser.add_argument(
        "-m",
        "--metric",
        choices=["file", "aws"],
        required=False,
        help="opt to have metrics published, either to AWS cloudwatch\
            or to the local file system",
    )
    argument_parser.add_argument(
        "--metricpath",
        default=paths.local_metrics_dir(),
        required=False,
        help="The absolute path to the directory\
            that stores the metrics (if metrics are stored locally)",
    )

    return argument_parser


def main(mocking: bool = False):
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
    if args.metric:  # If the user chose to publish metrics
        if args.metric == "file":  # publish to file system
            metric_publisher = FileMetricPublisher(Path(args.metricpath))
        elif args.metric == "aws":  # publish to cloudwatch
            metric_publisher = AwsMetricPublisher(MetricConstants.NAME_SPACE)
        else:
            parser.error(
                'Please specify either "file" or "aws" after the -m/--metric option.'
            )
    assert key_publisher is not None
    key_publisher.publish_key(
        args.hostname, args.user, metric_publisher=metric_publisher
    )


if __name__ == "__main__":
    main()

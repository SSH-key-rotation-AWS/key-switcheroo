from pathlib import Path
from argparse import ArgumentParser
from switcheroo.ssh.data_org.publisher import KeyPublisher, FileKeyPublisher
from switcheroo.ssh.data_org.publisher.s3 import S3KeyPublisher
from switcheroo import paths


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

    return argument_parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    publisher: KeyPublisher | None = None
    if args.datastore == "local":  # If the user chose to store the public key locally
        publisher = FileKeyPublisher(Path(args.sshdir))
    else:  # If the user chose to store the public key on S3 or chose to default to S3
        if args.bucket is None:
            parser.error("The s3 option requires a bucket name!")
        publisher = S3KeyPublisher(args.bucket, root_ssh_dir=Path(args.sshdir))
    assert publisher is not None
    publisher.publish_key(args.hostname, args.user)


if __name__ == "__main__":
    main()

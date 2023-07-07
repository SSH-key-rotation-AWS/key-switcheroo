from argparse import ArgumentParser
from switcheroo.publisher.key_publisher import Publisher, LocalPublisher, S3Publisher


def create_argument_parser() -> ArgumentParser:
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

    return argument_parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    publisher: Publisher | None = None
    if args.datastore == "local":  # If the user chose to store the public key locally
        publisher = LocalPublisher(args.hostname, args.user)
    else:  # If the user chose to store the public key on S3 or chose to default to S3
        if args.bucket is None:
            parser.error("The s3 option requires a bucket name!")
        publisher = S3Publisher(args.bucket, args.hostname, args.user)
    assert publisher is not None
    publisher.publish_new_key_with_metadata()


if __name__ == "__main__":
    main()

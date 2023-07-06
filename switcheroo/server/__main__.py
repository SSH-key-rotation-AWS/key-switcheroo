from argparse import ArgumentParser
from pathlib import Path
from switcheroo.server.retrieve_public_keys import get_public_keys_local, get_public_keys_s3

def create_argument_parser() -> ArgumentParser:
    argument_parser = ArgumentParser(
        prog="key_retriever",
        description="Fetches the public SSH keys from S3 or the local machine",
        epilog="Thanks for using key_retriever! :)"
    )
    argument_parser.add_argument("user")
    argument_parser.add_argument(
        "-ds",
        "--datastore",
        choices=["s3", "local"],
        default="s3",
        help="choose where to fetch the public key from, S3 or the local system (default is S3)",
    )
    argument_parser.add_argument(
        "--bucketname",
        required=False,
        help="If s3 is selected, the bucket name to look for the key",
    )
    return argument_parser

if __name__ == "__main__":
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.datastore == "local":
        ssh_dir = Path("~/.ssh").expanduser()
        print(get_public_keys_local(args.user, ssh_dir))
    else:
        if args.bucket is None:
            parser.error("The s3 option requires a specified bucket name!")
        print(get_public_keys_s3(args.user, args.bucketname))

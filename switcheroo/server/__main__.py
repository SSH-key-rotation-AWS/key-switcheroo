from argparse import ArgumentParser
from pathlib import Path
import socket
import traceback
from switcheroo.data_store import DataStore, FileSystemDataStore
from switcheroo.data_store.s3 import S3DataStore
from switcheroo import paths


def create_argument_parser() -> ArgumentParser:
    argument_parser = ArgumentParser(
        prog="key_retriever",
        description="Fetches the public SSH keys from S3 or the local machine",
        epilog="Thanks for using key_retriever! :)",
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
        "--bucket",
        required=False,
        help="If s3 is selected, the bucket name to look for the key",
    )
    argument_parser.add_argument(
        "--sshdir",
        required=False,
        help="If local is selected, the absolute path to\
            the directory that stores the keys (ie /home/you/.ssh)",
        default=paths.local_ssh_home(),
    )
    return argument_parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    data_store: DataStore | None = None

    if args.datastore == "local":
        data_store = FileSystemDataStore(Path(args.sshdir))
    elif args.datastore == "s3":
        if args.bucket is None:
            parser.error("The s3 option requires a specified bucket name!")
        data_store = S3DataStore(args.bucket)
    try:
        assert data_store is not None
        public_key = data_store.retrieve(socket.getfqdn(), args.user)
        print(public_key)
    except Exception as exc:  # pylint: disable = broad-exception-caught
        print(exc)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()

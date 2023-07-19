from argparse import ArgumentParser, ArgumentError
from pathlib import Path
import socket
import traceback
from switcheroo.ssh.scripts.custom_argument_exceptions import (
    InvalidArgumentError,
    MissingArgumentError,
)
from switcheroo.ssh.data_org.retriever import KeyRetriever, FileKeyRetriever
from switcheroo.ssh.data_org.retriever.s3 import S3KeyRetriever
from switcheroo import paths


def create_argument_parser() -> ArgumentParser:
    # pylint: disable=R0801
    argument_parser = ArgumentParser(
        prog="switcheroo_retrieve",
        description="Fetches the public SSH keys from S3 or the local machine",
        epilog="Thanks for using switcheroo_retrieve! :)",
    )
    argument_parser.add_argument("user", help="the username of the connecting client")
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
        help="The absolute path to\
            the directory that stores local keys (ie /home/you/.ssh)",
        default=paths.local_ssh_home(),
    )
    return argument_parser


def _local_store(sshdir: str, bucket: str | None = None) -> FileKeyRetriever:
    if bucket is not None:
        raise InvalidArgumentError(
            'Invalid argument "--bucket" when retrieving the keys locally'
        )
    return FileKeyRetriever(Path(sshdir))


def _s3_store(sshdir: str, bucket: str | None = None) -> S3KeyRetriever:
    if bucket is None:
        raise MissingArgumentError("The s3 option requires a specified bucket name!")
    return S3KeyRetriever(sshdir, bucket)


def main():
    parser = create_argument_parser()
    try:
        args = parser.parse_args()
    except ArgumentError as error:
        raise InvalidArgumentError(f"Invalid argument: {error}") from error
    retriever: KeyRetriever | None = None
    if args.datastore == "local":
        retriever = _local_store(args.sshdir, args.bucket)
    elif args.datastore == "s3":
        retriever = _s3_store(args.sshdir, args.bucket)
    try:
        assert retriever is not None
        public_key = retriever.retrieve_public_key(socket.getfqdn(), args.user)
        print(public_key.byte_data.decode())
    except Exception as exc:  # pylint: disable = broad-exception-caught
        print(exc)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()

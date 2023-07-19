from typing import Any, TypeVar
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from switcheroo.base.data_store import DataStore
from switcheroo.base.exceptions.s3 import (
    UnconfiguredAWSException,
    NoBucketFoundException,
)

T = TypeVar("T")


class S3DataStore(DataStore):
    """See base classes. Stores items in an AWS S3 Bucket. \
    Credentials for AWS are read from the users AWS command line utility - if AWS command line \
    is not installed and configured, this class will not work
    """

    def __init__(self, _bucket_name: str):
        """Initialize the data store. \
        Uses credentials & region from the AWS CLI utility.

        Args:
            _bucket_name (str): the name of the S3 bucket to store items in

        Raises:
            UnconfiguredAWSException: If no AWS credentials are detected
            NoBucketFoundException: If no bucket with the given name is found
        """
        super().__init__()
        self._bucket_name = _bucket_name
        self._s3_client = boto3.client("s3")  # type: ignore
        # Ensure AWS credentials are configured
        sts_client = boto3.client("sts")  # type: ignore
        try:
            sts_client.get_caller_identity()
        except ClientError as exc:
            raise UnconfiguredAWSException() from exc

        # Ensure bucket exists - will error out otheriwse
        try:
            self._s3_client.head_bucket(Bucket=self._bucket_name)
        except ClientError as exc:
            raise NoBucketFoundException(self._bucket_name) from exc

    def publish(self, item: Any, location: Path):
        """See base class"""
        serialized_data = super().serialize(item)
        self._s3_client.put_object(
            Bucket=self._bucket_name, Key=str(location), Body=serialized_data
        )

    def retrieve(self, location: Path, clas: type[T]) -> T | None:
        """See base class"""
        try:
            response = self._s3_client.get_object(
                Bucket=self._bucket_name, Key=str(location)
            )
            # Found item
            str_data: str = response["Body"].read().decode()
            deserialized_item: T = super().deserialize(str_data, clas)
            return deserialized_item
        except ClientError as exc:
            # Item does not exist in the bucket
            if exc.response["Error"]["Code"] == "NoSuchKey":  # type: ignore
                return None
            # Something else AWS-related went wrong - throw the exception back at the user
            raise exc

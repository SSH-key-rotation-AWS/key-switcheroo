from typing import Any, TypeVar
from pathlib import Path
import boto3
from switcheroo.base.data_store import DataStore

T = TypeVar("T")


class S3DataStore(DataStore):
    def __init__(self, _bucket_name: str):
        super().__init__()
        self._bucket_name = _bucket_name
        self._s3_client = boto3.client("s3")  # type: ignore

    def publish(self, item: Any, location: Path):
        serialized_data = super().serialize(item)
        self._s3_client.put_object(
            Bucket=self._bucket_name, Key=str(location), Body=serialized_data
        )

    def retrieve(self, location: Path, clas: type[T]) -> T:
        response = self._s3_client.get_object(
            Bucket=self._bucket_name, Key=str(location)
        )
        str_data: str = response["Body"].read().decode()
        deserialized_item: T = super().deserialize(str_data, clas)
        return deserialized_item

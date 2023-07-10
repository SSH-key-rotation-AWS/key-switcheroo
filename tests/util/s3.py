def empty_bucket(s3_client, bucket: str):  # type: ignore
    objects = s3_client.list_objects_v2(Bucket=bucket)["Contents"]  # type: ignore
    delete_objects = [{"Key": bucket_obj["Key"]} for bucket_obj in objects]  # type: ignore
    s3_client.delete_objects(  # type: ignore
        Bucket=bucket,  # type: ignore
        Delete={"Objects": delete_objects},  # type: ignore
    )


class S3Cleanup:
    def __init__(self, s3_client, s3_bucket: str):  # type: ignore
        self._s3_client = s3_client  # type: ignore
        self._s3_bucket = s3_bucket

    def __enter__(self):
        return self

    def __exit__(self, one, two, three):  # type: ignore
        empty_bucket(self._s3_client, self._s3_bucket)  # type: ignore

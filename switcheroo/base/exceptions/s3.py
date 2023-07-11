class UnconfiguredAWSException(Exception):
    def __init__(self):
        super().__init__(
            "AWS Credentials not detected! Please configure AWS CLI on your machine"
        )


class NoBucketFoundException(Exception):
    def __init__(self, bucket_name: str) -> None:
        super().__init__(f"Could not find bucket with name {bucket_name}")

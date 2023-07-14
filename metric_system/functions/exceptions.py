class MetricOverwriteException(BaseException):
    "Thrown when the user writes metric data to a file dedicated for a different metric"

    def __init__(self, attempted_metric_name: str, existing_metric_name: str):
        message = f"cannot write metric {existing_metric_name} to\
                  a file containing {attempted_metric_name}!"
        super().__init__(message)

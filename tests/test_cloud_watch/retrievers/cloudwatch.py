from datetime import datetime
import boto3
from mypy_boto3_cloudwatch import Client
from mypy_boto3_cloudwatch.literals import StandardUnitType
from metric_system.functions.metric import MetricData, DataPoint


class AWSMetricRetriever:
    def __init__(self, name_space: str):
        self._name_space: str = name_space
        self._cloud_watch: Client = boto3.client("cloudwatch")  # type: ignore

    def retrieve_metric_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        unit: StandardUnitType,
    ) -> MetricData:
        """Returns metric data from CloudWatch"""
        response = self._cloud_watch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "some_id",  # Does not have to be unique
                    "MetricStat": {
                        "Metric": {
                            "Namespace": self._name_space,
                            "MetricName": metric_name,
                        },
                        "Period": 1,
                        "Stat": "Sum",
                    },
                    "ReturnData": True,
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
        )
        results = response["MetricDataResults"][0]
        datapoints = list(
            zip(results["Timestamps"], results["Values"])  # pyright: ignore
        )

        # Convert datapoint results to metric data
        def res_to_dp(datapoint_info: tuple[datetime, float]):
            return DataPoint(datapoint_info[0], unit, datapoint_info[1])

        metric_data = MetricData(metric_name, list(map(res_to_dp, datapoints)))
        return metric_data

from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
import json
from mypy_boto3_cloudwatch.literals import StandardUnitType
from metric_system.functions.metric import MetricData, DataPoint


class MetricRetriever(ABC):
    @abstractmethod
    def retrieve_metric_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        unit: StandardUnitType,
    ) -> MetricData:
        """Retrieves all metric data of the metric with the given name between the start & end time.
        This disregards the unit of the metric."""


class FileMetricRetriever(MetricRetriever):
    """
    Retrieves metric data from files.
    This class is purely for testing purposes - the functionality of CloudWatch is very vast,
    using this as a general retrieve method would be limiting.
    """

    def __init__(self, metric_dir: Path) -> None:
        self._metric_dir = metric_dir

    def retrieve_metric_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        unit: StandardUnitType,
    ) -> MetricData:
        all_data = self._retrieve_all_data(metric_name)
        datapoints_in_timeframe: list[DataPoint] = []
        found_beginning = False
        for datapoint in all_data.data_points:
            if not found_beginning:
                if datapoint.timestamp >= start_time:
                    datapoints_in_timeframe.append(
                        datapoint
                    )  # First datapoint in range
            else:  # Keep appending as long as we havent hit the end
                if datapoint.timestamp > end_time:
                    break
                # Check if the unit is what we passed in
                if datapoint.unit == unit:
                    datapoints_in_timeframe.append(
                        datapoint
                    )  # Have not hit the end just yet
        return MetricData(metric_name, datapoints_in_timeframe)

    def _retrieve_all_data(self, metric_name: str) -> MetricData:
        try:
            with open(
                self._metric_dir / f"{metric_name}.json", encoding="utf-8", mode="rt"
            ) as data_file:
                return MetricData.from_json(json.load(data_file))
        except FileNotFoundError:
            return MetricData(metric_name, [])

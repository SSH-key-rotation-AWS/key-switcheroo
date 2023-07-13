"""
file_metric_publisher.py
"""
from dataclasses import dataclass
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from mypy_boto3_cloudwatch.literals import StandardUnitType
from metric_system.functions.metric import Metric
from metric_system.functions.metric_publisher import MetricPublisher


@dataclass
class DataPoint:
    timestamp: datetime
    unit: StandardUnitType
    value: float

    @classmethod
    def create_from(cls, metric: Metric):
        return DataPoint(datetime.now(), metric.unit, metric.value)


@dataclass
class MetricJsonData:
    metric_name: str
    data_points: list[DataPoint]

    @classmethod
    def from_json(cls, obj: Any):
        "Parses the JSON representation of this class into an instance of this class"
        # Ensure that we have our attributes
        if not "metric_name" in obj or not "data_points" in obj:
            raise TypeError("Error deserializing metric data!")
        metric_name = obj["metric_name"]
        data_points_json = obj["data_points"]

        # Maps data point json => data point object, erroring out if needed
        def map_data_points(data_point: Any) -> DataPoint:
            if not all(
                ["timestamp" in data_point, "unit" in data_point, "value" in data_point]
            ):
                raise TypeError("Error deserializing metric data!")
            timestamp = datetime.strptime(
                data_point["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
            )
            unit = data_point["unit"]
            value = float(data_point["value"])
            return DataPoint(timestamp, unit, value)

        # Call the mapping function
        data_points = list(map(map_data_points, data_points_json))
        return MetricJsonData(metric_name, data_points)

    def to_json(self) -> Any:
        "Makes this object JSON-serializable by treating the data points as dicts"

        def data_point_to_json(data_point: DataPoint):
            return {
                "timestamp": str(data_point.timestamp),
                "unit": data_point.unit,
                "value": data_point.value,
            }

        data_points = list(map(data_point_to_json, self.data_points))
        return {"metric_name": self.metric_name, "data_points": data_points}


class FileMetricPublisher(MetricPublisher):
    """Publishes specified metric data to a file"""

    def __init__(self, metric_dir: Path):
        self._metric_dir = metric_dir

    def _metric_file_path(self, metric_name: str):
        return self._metric_dir / f"{metric_name}.json"

    def publish_metric(self, metric: Metric):
        """Publish metrics to a file.

        File location is the directory passed into the class / metric.name.

        New datapoints are appended to the existing ones.
        """

        # Create our new datapoint
        new_datapoint = DataPoint.create_from(metric)
        # Check if we already have data published to the file
        retrieved_data = self.retrieve_metric_data(metric.name)
        if retrieved_data is None:
            retrieved_data = MetricJsonData(metric_name=metric.name, data_points=[])
        retrieved_data.data_points.append(new_datapoint)
        # Write to file
        with open(
            self._metric_file_path(metric.name), encoding="utf-8", mode="wt+"
        ) as file:
            # Write the JSON data to the file
            json.dump(retrieved_data.to_json(), file)

    def retrieve_metric_data(self, metric_name: str) -> MetricJsonData | None:
        try:
            with open(
                self._metric_file_path(metric_name), encoding="utf-8", mode="rt"
            ) as data_file:
                return MetricJsonData.from_json(json.load(data_file))
        except FileNotFoundError:
            return None

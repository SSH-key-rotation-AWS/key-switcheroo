from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from mypy_boto3_cloudwatch.literals import StandardUnitType


class Metric(ABC):
    """Abstract class used to publish metrics"""

    def __init__(
        self,
        metric_name: str,
        unit: StandardUnitType,
        value: float = 0,
    ):
        self._metric_name: str = metric_name
        self._unit: StandardUnitType = unit
        self._value: float = value
        self._metric_init: datetime = datetime.now()

    @property
    def name(self) -> str:
        """Returns metric name"""
        return self._metric_name

    @property
    def value(self) -> float:
        """Returns the value associated with the metric"""
        return self._value

    @value.setter
    def value(self, val: float):
        self._value = val

    @property
    def unit(self) -> StandardUnitType:
        """Returns the unit associated with the metric"""
        return self._unit

    @property
    def metric_init_time(self) -> datetime:
        return self._metric_init


@dataclass
class DataPoint:
    timestamp: datetime
    unit: StandardUnitType
    value: float

    @classmethod
    def parse_timestamp(cls, str_timestamp: str) -> datetime:
        return datetime.strptime(str_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    @classmethod
    def create_from(cls, metric: Metric):
        return DataPoint(datetime.now(), metric.unit, metric.value)


@dataclass
class MetricData:
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
            timestamp = DataPoint.parse_timestamp(data_point["timestamp"])
            unit = data_point["unit"]
            value = float(data_point["value"])
            return DataPoint(timestamp, unit, value)

        # Call the mapping function
        data_points = list(map(map_data_points, data_points_json))
        return MetricData(metric_name, data_points)

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

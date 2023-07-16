from abc import ABC
from datetime import datetime
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

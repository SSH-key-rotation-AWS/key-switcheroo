from abc import ABC
from datetime import datetime


class Metric(ABC):
    """Abstract class used to publish metrics"""

    def __init__(
        self,
        metric_name: str,
        unit: str,
    ):
        self._metric_name = metric_name
        self._unit = unit
        self._value = None
        self._metric_init = datetime.now()

    @property
    def name(self) -> str:
        """Returns metric name"""
        return self._metric_name

    @property
    def value(self):
        """Returns the value associated with the metric"""
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def unit(self) -> str:
        """Returns the unit associated with the metric"""
        return self._unit

    @property
    def metric_init(self):
        return self._metric_init

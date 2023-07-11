from abc import ABC

class Metric(ABC):
    """Abstract class used to publish metrics"""

    def __init__(self, metric_name: str, unit: str):
        self._metric_name = metric_name
        self._unit = unit
        self._value = None  

    def get_name(self) -> str:
        """Returns metric name"""
        return self._metric_name

    def get_value(self):
        """Returns the value associated with the metric"""
        return self._value

    def get_unit(self) -> str:
        """Returns the unit associated with the metric"""
        return self._unit

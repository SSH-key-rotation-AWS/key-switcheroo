from abc import ABC, abstractmethod


class Metric(ABC):
    """Abstract class , used to publish metrics"""

    @abstractmethod
    def get_metric_name(self) ->str:
        """Returns metric name"""

    def get_metric_value(self):
        """Retruns the value associated with the metric"""
    def get_metric_unit(self):
        """returns the unit associated with the metric"""



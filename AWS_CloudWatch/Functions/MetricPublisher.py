from abc import ABC, abstractmethod
from Metric import Metric

class MetricPublisher(ABC):
    """Abstract class , used to publish metrics"""

    @abstractmethod
    def publish_metric(self,metric:Metric):
        """A general layout for publishing metrics."""

    
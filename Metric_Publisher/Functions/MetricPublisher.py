from abc import ABC, abstractmethod
from Metric import Metric

class MetricPublisher(ABC):

    @abstractmethod
    def publish_metric(self, metric: Metric):
        """Publishes a metric.

        Args:
            metric (Metric): The metric object to be published.
        """
        

from abc import ABC, abstractmethod
from datetime import datetime
from metric_system.functions.metric import Metric, MetricData


class MetricPublisher(ABC):
    @abstractmethod
    def publish_metric(self, metric: Metric):
        """Publishes a metric.

        Args:
            metric (Metric): The metric object to be published.
        """

    @abstractmethod
    def retrieve_metric_data(
        self, metric_name: str, start_time: datetime, end_time: datetime
    ) -> MetricData:
        """Retrieves a metrics data within a given timeframe as a list of time-marked data points

        Args:
            metric_name (str): The metric to retrieve data from
            start_time: (datetime): when to start the timeframe of data
            end_time (datetime): when to end the timeframe of data

        Returns:
            metric_data (MetricData): The metric data"""

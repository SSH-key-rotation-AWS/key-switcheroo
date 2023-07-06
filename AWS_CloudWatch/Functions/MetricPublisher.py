"""Abstract class implemintation import """
from abc import ABC, abstractmethod


class MetricPublisher(ABC):
    """Abstract class , used to publish metrics"""

    @abstractmethod
    def timeit_and_publish(self, metric_name: str):
        """A key generation metric context manager to calculate
        the time it took for a key to be generated"""
        

    @abstractmethod
    def inc_key_count(self, metric_name: str):
        """A function that calculates the  a key count to be generated"""

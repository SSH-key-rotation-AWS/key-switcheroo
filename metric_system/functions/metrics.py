from contextlib import contextmanager
import time
from mypy_boto3_cloudwatch.literals import StandardUnitType
from metric_system.functions.metric import Metric


class TimingMetric(Metric):
    """Timing metric that calculates the time the metric has run."""

    @contextmanager
    def timeit(self):
        """Context manager used to calculate the time the method has run."""
        start_time = 0
        try:
            start_time = time.time()
            yield
        finally:
            self._value = time.time() - start_time


class CounterMetric(Metric):
    """Counter metric that counts the key count."""

    def __init__(self, metric_name: str, unit: StandardUnitType):
        super().__init__(metric_name, unit)

    def increment(self):
        """Increments the count metric by 1."""
        self._value += 1

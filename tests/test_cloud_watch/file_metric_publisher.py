"""
file_metric_publisher.py
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from metric_system.functions.metrics import TimingMetric, CounterMetric
from metric_system.functions.metric import Metric
from metric_system.functions.metric_publisher import MetricPublisher


class FileMetricPublisher(MetricPublisher):
    """Publishes specified metric data to a file"""

    def __init__(self, name_space: str, instance_id: str, file_location: Path):
        self.file_name = name_space
        self._instance_id = instance_id
        self._file_location = file_location

    def publish_metric(self, metric: Metric):
        """Publish metrics to a file"""
        metric_name = metric.name
        metric_value = metric.value
        metric_unit = metric.unit
        time = str(datetime.now().time())

        data: Any = {
            "Metric Name": metric_name,
            "Metric Data": {
                "Time Stamp": time,
                "Unit": metric_unit,
                "Value": metric_value,
            },
        }

        if isinstance(metric, TimingMetric):
            self.write_to_file(Path(self._file_location / "test_timeit.json"), data)
        if isinstance(metric, CounterMetric):
            self.write_to_file(Path(self._file_location / "test_inc_count.json"), data)

    def write_to_file(self, file_path: Path, content: Any):
        """Write to file"""
        with open(file_path, "w+") as file:  # pylint: disable=unspecified-encoding
            # Write the JSON data to the file
            json.dump(content, file)

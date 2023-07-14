"""
file_metric_publisher.py
"""
import json
from pathlib import Path
from metric_system.functions.metric import Metric, DataPoint, MetricData
from metric_system.functions.metric_publisher import MetricPublisher


class FileMetricPublisher(MetricPublisher):
    """Publishes specified metric data to a file"""

    def __init__(self, metric_dir: Path):
        self._metric_dir = metric_dir
        if not metric_dir.exists():
            metric_dir.mkdir(parents=True, exist_ok=True)

    def _metric_file_path(self, metric_name: str):
        return self._metric_dir / f"{metric_name}.json"

    def publish_metric(self, metric: Metric):
        """Publish metrics to a file.

        File location is the directory passed into the class / metric.name.

        New datapoints are appended to the existing ones.
        """

        # Create our new datapoint
        new_datapoint = DataPoint.create_from(metric)
        # Check if we already have data published to the file
        retrieved_data = self._retrieve_all_data(metric.name)
        retrieved_data.data_points.append(new_datapoint)
        # Write to file
        with open(
            self._metric_file_path(metric.name), encoding="utf-8", mode="wt+"
        ) as file:
            # Write the JSON data to the file
            json.dump(retrieved_data.to_json(), file)

    def _retrieve_all_data(self, metric_name: str) -> MetricData:
        try:
            with open(
                self._metric_file_path(metric_name), encoding="utf-8", mode="rt"
            ) as data_file:
                return MetricData.from_json(json.load(data_file))
        except FileNotFoundError:
            return MetricData(metric_name, [])

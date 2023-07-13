"""
file_metric_publisher.py
"""
import json
from pathlib import Path
from datetime import datetime
from metric_system.functions.metric import Metric
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.metric import MetricData, DataPoint


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

    def retrieve_metric_data(
        self, metric_name: str, start_time: datetime, end_time: datetime
    ) -> MetricData:
        all_data = self._retrieve_all_data(metric_name)
        datapoints_in_timeframe: list[DataPoint] = []
        found_beginning = False
        for datapoint in all_data.data_points:
            if not found_beginning:
                if datapoint.timestamp >= start_time:
                    datapoints_in_timeframe.append(
                        datapoint
                    )  # First datapoint in range
            else:  # Keep appending as long as we havent hit the end
                if datapoint.timestamp > end_time:
                    break
                datapoints_in_timeframe.append(
                    datapoint
                )  # Have not hit the end just yet
        return MetricData(metric_name, datapoints_in_timeframe)

    def _retrieve_all_data(self, metric_name: str) -> MetricData:
        try:
            with open(
                self._metric_file_path(metric_name), encoding="utf-8", mode="rt"
            ) as data_file:
                return MetricData.from_json(json.load(data_file))
        except FileNotFoundError:
            return MetricData(metric_name, [])

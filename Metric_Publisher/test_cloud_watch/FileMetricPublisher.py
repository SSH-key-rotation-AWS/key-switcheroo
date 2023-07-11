"""File metric publisher """
import os
import sys
from Functions.Metrics import CounterMetric, TimingMetric
from Functions.Metric import Metric
from Functions.MetricPublisher import MetricPublisher

sys.path.insert(0, '/Users/dothanbar/Desktop/ComputerScience/YU/SummerProgram/team-henrique/AWS_CloudWatch/Functions')

from datetime import datetime




class FileMetricPublisher(MetricPublisher):
    """Publishes Metric specificed data"""

    def __init__(self, name_space: str, instance_id: str):
        self.file_name = name_space
        self._instance_id = instance_id
        self._file_location = os.getcwd() + "/test/FileMetricPublisherTest"

    def publish_metric(self, metric:Metric):
        """Publish metrics to a file"""
        metric_name = metric.get_name()
        metric_value = metric.get_value()
        metric_unit = metric.get_unit()
        time = str(datetime.now().time())

        data = {
            "Metric Name": metric_name,
            "Metric Data": {
                "Time Stamp": time,
                "Unit": metric_unit,
                "Value": metric_value,
            },
        }

        if isinstance(metric, TimingMetric):
            self.write_to_file(self._file_location + "/test_timeit.json", data)
        if isinstance(metric, CounterMetric):
            self.write_to_file(self._file_location + "/test_inc_count.json", data)

    def write_to_file(self, file_path, content):
        """Write to file"""
        with open(file_path, "w") as file:
            file.write(content)


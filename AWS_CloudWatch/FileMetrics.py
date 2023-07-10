"""File metric publisher """
from Functions.Metrics import CounterMetric, TimingMetric
from Functions.Metric import Metric
from  Functions.MetricPublisher import MetricPublisher
from datetime import datetime
import os



class FileMetricPublisher(MetricPublisher):
    """Publishes Metric specificed data"""

    def __init__(
        self, name_space: str, instance_id: str):
        self.file_name = name_space
        self._instance_id = instance_id
        self._file_location =os.getcwd() +"/test/FileMetricPublisherTest"

    def publish_metric(self,metric:Metric):
        metric_name = metric.get_metric_name()
        metric_value = metric.get_metric_value()
        metric_unit = metric.get_metric_unit()
        time  = str(datetime.now().time())
        
        
        data = {"Metric Name": metric_name, 
                "Metric Data": 
                {"Time Stamp": time,
                  "Unit": metric_unit,"Value": metric_value} }
        
        if isinstance(metric,TimingMetric):
            self.write_to_file(self._file_location+"/test_timeit.json",data)
        if isinstance(metric,CounterMetric):
            self.write_to_file(self._file_location+"/test_inc_count.json",data)

    def write_to_file(self,file_path, content):
        with open(file_path, "w") as file:
            file.write(content)

        

            

        

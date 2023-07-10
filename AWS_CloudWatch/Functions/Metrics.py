from contextlib import contextmanager
from Functions.Metric import Metric
import time

class TimingMetric(Metric):
    def __init__(self,metric_name:str):
        self._end_time = 0
        self._metric_name = metric_name
        self._unit = "Seconds"
         

    @contextmanager
    def timeit_metric(self):
        start_time = 0
        try:
            start_time = time.time()
            yield
        finally:
            self._end_time = time.time() - start_time

    def get_metric_name(self) -> str:
        return self._metric_name
    def get_metric_value(self):
        return self._end_time
    def get_metric_unit(self):
        return self._unit

class CounterMetric(Metric):
    def __init__(self,metric_name:str):
        self._counter = 0
        self._metric_name = metric_name
        self._unit = "Count"
    
    def inc_count_metric(self):
        self._counter +=1

    def get_metric_name(self) -> str:
        return self._metric_name
    
    def get_metric_value(self):
        return self._counter
    
    def get_metric_unit(self):
        return self.get_metric_unit
    
        

from Functions.Metric import Metric

class CounterMetric(Metric):

    def __init__(self, name_space: str):
        super().__init__(name_space, "Count")
        self.counter = 0

    def publish_metric(self, metric_name: str):
        self.increment_counter()
        return super().publish_metric(metric_name=metric_name,value=self.counter)
    
    def increment_counter(self):
        self.counter +=1 


class TimingMetric(Metric):

    def __init__(self, name_space: str):
        super().__init__(name_space, "Seconds")
    
    def publish_metric(self, metric_name: str,value):
        return super().publish_metric(metric_name=metric_name,value=value)
        

## Introduction

This package provides generic and concrete metric and publishing classes that should be implemented in order to provide metric publishing functionality to the SSH Key rotation service. 

## Abstract Classes

### Metric
-  Abstract class used to define metric

#### Abstract methods 

##### __init__(self, metric_name: str, unit: str):
- metric_name=str -> stores the name of the user defined metric in the extended metric class  
- unit=str -> stores the unit of the user defined metric in the extended metric class
##### get_name(self) -> str:
- returns the name of the user defined metric
##### def get_value(self):
- returns the value of the user defined metric
##### def get_unit(self)
- returns the Unit of the user defined metric
     
### MetricPublisher
- Abstract class used to publish metrics
  
#### Abstract methods 

#### publish_metric(self, metric: Metric):
- metric (Metric): The metric object to be published.
- Publishes the metric.

## Concrete classes

### TimingMetric extends Metric

#### Methods

##### def timeit(self):
- Context manager used to calculate the time the method has run.
##### def get_name(self) -> str:
- Returns the metric name
##### def get_unit(self) -> str:
- Returns the unit associated with the metric.
##### def get_value(self):
- Returns the value associated with the metric.

### CounterMetric Extends Metric

#### Methods

##### def inc_count(self):
- Increments the Key Count
##### def get_name(self) -> str:
- Returns the metric name
##### def get_unit(self) -> str:
- Returns the unit associated with the metric.
##### def get_value(self):
- Returns the value associated with the metric.

### AWSMetricPublisher(MetricPublisher):

#### Methods

#####  def __init__(self, name_space: str, instance_id: str, aws_region: str):
- name_space (str): The namespace of the metric.
- instance_id (str): The ID of the instance associated with the metric.
- aws_region (str): The AWS region to use for CloudWatch.
#####  def publish_metric(self, metric: Metric):
- Publishes the metric to AWS CloudWatch resource based on region and namespace. 

## Use Cases

### Simulation for an AWS CloudWatch Metric Publisher
```python
    setUp(self):
        self.publisher = AWSMetricPublisher(name_space="NameSpace",instance_id="ec2_instance",aws_region="us-east-1")
        self.inc_key_count_metric = CounterMetric(metric_name="Counter",unit="Count")
        self.time_metric = TimingMetric(metric_name="File test Timing",unit="Seconds")

    key_generation():
        with self.time_metric.timeit():
            # Key implementation logic
            # Done publishing keys
        self.inc_key_count.inc_count()
        #increments key count.
        self.publisher.publish(self.time_metrtic)
        self.publisher.publish(self.inc_key_count)
        # publishes data to AWS cloudWatch
```

        

        

    








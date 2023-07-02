## Introduction

This is a Python script for publishing specific metrics to your personal AWS CloudWatch using the AWS SDK. It is designed to automatically send data for two specific metrics: "Time to create a key" and "Key count."

### Constructor

The `AWSMetricPublisher` object takes the following arguments:

- `aws_region`: The region to which you want the `AWSMetricPublisher` object to send metric data to AWS CloudWatch.
- `namespace_name`: The namespace under which you want to store the metric data in AWS CloudWatch.
- `instance_id`: The instance identifier that can be tied to the metric data. For example, if you are publishing keys to an S3 bucket, the bucket name would be used as an identifier.
- `do_not_enable`: If the user specifies from the command line that they do not want to use the feature, this argument should be set to `True`, and no metric data will be published. By default, it is set to `False`.

### Metric Publisher - `metric_publisher(self, key_count: bool, key_count_metric_name: str, key_publish_time: bool, key_publish_time_metric_name: str)`

This context manager API provides an additional layer of abstraction for publishing metrics. It takes the following arguments:

- `key_count`: If set to `True`, it will publish a key count value to the "Key count" metric name. If set to `False`, no metric data will be published for key count.
- `key_count_metric_name`: Sets the metric name for the key count metric.
- `key_publish_time`: If set to `True`, it will publish the time taken to generate a key to the "Time to generate key" metric name. If set to `False`, no metric data will be published for time to generate key.
- `key_publish_time_metric_name`: Sets the metric name for the time to generate key metric.

### Usage

This function is used as a context manager and should be invoked when initially publishing a key. Once the context manager is closed, the function calculates the time it took for the key to be generated and sends the results to the "Time to generate key" metric under the generic metric name. It also sends the key count to the "Key count" metric, depending on the values of the `key_count` and `key_publish_time` arguments.

Example usage:

```python
def function_that_publishes_keys():
    with AWSMetricPublisher.MetricPublisher(
        key_count=True,
        key_count_metric_name="My Key Count Metric",
        key_publish_time=True,
        key_publish_time_metric_name="My Time to publish keys metric"
    ):
        # Currently publishing keys to client...

        # Done publishing keys to client

    # Done with the context manager and publishing keys
    # Once the context manager is closed, you can view the updated metric data.

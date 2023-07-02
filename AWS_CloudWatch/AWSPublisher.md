
  

This is a Python script for publishing specific metrics to your personal AWS CloudWatch using the AWS SDK. It is designed to automatically send data for two specific metrics: "Time to create a key" and "Key count."

## Constructor

The `AWSMetricPublisher` object takes the following arguments:

- `aws_region`: The region to which you want the `AWSMetricPublisher` object to send metric data to AWS CloudWatch.

- `namespace_name`: The namespace under which you wxant to store the metric data in AWS CloudWatch.

- `instance_id`: The instance identifier that can be tied to the metric data. For example, if you are publishing keys to an S3 bucket, the bucket name would be used as an identifier.

- `do_not_enable`: If the user specifies from the command line that they do not want to use the feature, this argument should be set to `True`, and no metric data will be published. It should be set to default as `False` .

## Time to create a key metric - `timeit_and_publish(self, metric_name: str) -> response`

This function is used as a context manager and is invoked when creating a key. Once the context manager is closed, the function calculates the time it took for the key to be generated and sends the results to the "Key count" metric under a generic metric name.

Example usage:

```python

def function_that_publishes_keys():

with cloud_Watch.timeit_and_publish(metric_name="my metric"):

# Currently publishing keys to client...

# Done publishing keys to client

# Once the context manager is closed, you can view the updated metric data under the namespace "my metric"

```

function returns the API respnse from the published metric data.

## Key count metric - `inc_count_metric(self, metric_name: str)`

This function increments the count for the specified metric name.

Example usage:

```python

def function_that_publishes_keys():

# Currently publishing keys to client...

# Done publishing keys to client

AWSMetricPublisher.inc_count_metric(metric_name:"my metric")

#cureenlty sent to "my metric" that 1 key has been published.

```

##When running these functions, you are able to view the updated metric data in real time under the name space in the grafana dashboard

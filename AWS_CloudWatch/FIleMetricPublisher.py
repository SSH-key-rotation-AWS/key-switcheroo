from Functions.MetricPublisher import MetricPublisher
from Functions.Metrics import CounterMetric
import unittest
from datetime import datetime
import json
import os
import time


class FileMetricPublisher(MetricPublisher):
    def __init__(self,file_location:str,name_space:str):
        self.file_location = file_location
        self.name_space = name_space
        self.counter_metric = CounterMetric(name_space=self.name_space)

    def inc_key_count(self, metric_name: str):
        data = self.counter_metric.publish_metric(metric_name=metric_name)
        meta_data =  str(datetime.now()) + ".json"
        meta_data.replace(" ","")
        file_name = "key_count_metric_data_from" + meta_data

        file_path = os.path.join(self.file_location,file_name)

        with open(file_path,"w") as json_file:
            json.dump(data, json_file)

    def timeit_and_publish(self, metric_name: str):
        return super().timeit_and_publish(metric_name)


class FileMetricPublisherTest(unittest.TestCase):
    def setUp(self) -> None:
        current_dir = os.getcwd()
        relative_path = "test/FileMetricPublisherTest"
        self.file_path = os.path.join(current_dir, relative_path)
        self.name_space = "FILE METRIC TESTING"
        self.key_count_metric_name = "KEY COUNT METRIC"
        self.metric_publisher = FileMetricPublisher(self.file_path,self.name_space)
    
    def tearDown(self) -> None:
        for file_name in os.listdir(self.file_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.file_path, file_name)
                try:
                    os.unlink(file_path) 
                except Exception as e:
                    print(f"Error deleting file: {file_path}")
                    print(e)
    
    def test_inc_key_count(self):
        for _ in range(5):
            self.metric_publisher.inc_key_count(metric_name=self.key_count_metric_name)
            self.read_json_files()


    def read_json_files(self):
        for file_name in os.listdir(self.file_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.file_path, file_name)
                with open(file_path, "r") as file:
                    data = json.load(file)

                    metric_name = data["Metric Name"]
                    name_space = data["Name Space"]
                    unit = data["Metric Data"]["Unit"]

                    self.assertEqual(self.name_space,name_space)
                    self.assertEqual(self.key_count_metric_name,metric_name)
                    self.assertEqual("Count",unit)
            
    

if __name__ == '__main__':
    unittest.main()
        





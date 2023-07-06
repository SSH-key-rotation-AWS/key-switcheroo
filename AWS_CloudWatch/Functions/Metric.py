from abc import ABC, abstractmethod
import datetime


class Metric(ABC):
    """Abstract class , used to publish metrics"""
    def __init__(self,name_space:str,unit:str):
        self._name_space = name_space
        self.unit = unit
        

    @abstractmethod
    def publish_metric(self,metric_name:str,value):
        """A general layout for publishing metrics."""
        return {
            "Name Space":self._name_space,
            "Metric Name":metric_name,
            "Metric Data":{
                "Time Stamp":str(datetime.datetime.now()),
                "Unit":self.unit, 
                "Value":value
            }
        } 




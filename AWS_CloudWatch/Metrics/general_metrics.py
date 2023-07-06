from abc import ABC, abstractmethod

class general_metrics(ABC):
    def __init__(self,name_space:str,instance_id:str) -> None:
        self._name_space = name_space
        self._instance_id = instance_id
        self._key_count = 0



    @abstractmethod
    def timeit_and_publish(self,metric_name: str):
        pass

    @abstractmethod
    def inc_key_count(self,metric_name:str):
        pass


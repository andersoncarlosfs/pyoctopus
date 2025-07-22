from abc import ABC
from abc import abstractmethod


class OctopusBase(ABC):  
    @abstractmethod
    def __init__(
        self, 
        host: str, 
        token: str = None
    ) -> None:
        pass

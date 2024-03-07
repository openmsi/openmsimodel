from abc import ABC, abstractmethod


class CoreElement(ABC):
    @property
    @abstractmethod
    def assets(self):
        return None

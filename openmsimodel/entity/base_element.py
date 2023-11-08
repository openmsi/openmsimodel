from abc import ABC, abstractmethod


class Element(ABC):
    @property
    @abstractmethod
    def assets(self):
        return None

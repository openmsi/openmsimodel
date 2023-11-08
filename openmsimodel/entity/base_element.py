from abc import ABC, abstractmethod


class BaseElement(ABC):
    @property
    @abstractmethod
    def assets(self):
        return None

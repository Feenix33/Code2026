"""
Base processor
"""
from abc import ABC, abstractmethod


class Processor(ABC):

    @abstractmethod
    def process(self, text):
        pass
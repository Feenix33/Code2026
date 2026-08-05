"""
Abstract renderer.
Every renderer should inherit from this class.
"""
from abc import ABC
from abc import abstractmethod
class Renderer(ABC):
    @abstractmethod
    def render(self, grid):
        """
        Draw the grid.

        Every renderer must implement this.
        """
        pass

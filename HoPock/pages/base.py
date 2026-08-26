from abc import ABC, abstractmethod

from models.config import PageConfig
from models.resolver import resolve_page_style


class Page(ABC):

    def __init__(self, config, booklet_style):
        self.config = config

        # get the effective style for this instance
        self.style = resolve_page_style(
            booklet_style,
            config.style
        ) 
        self.detail = config.detail

    @abstractmethod
    def render(self):
        """Render this page."""
        pass
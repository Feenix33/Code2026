from abc import ABC, abstractmethod

from models.config import PageConfig
from models.styles import *
from models.data_classes import *
from models.resolver import resolve_page_style
from pages.factory import PageFactory

import logging
logger = logging.getLogger(__name__)


class Page(ABC):

    def __init__(self, config: PageConfig, booklet_style: BookletStyle):
        self.config = config
        # self.style = config.style
        self.booklet_style = booklet_style

        # get the effective style for this instance
        self.style = resolve_page_style(
            self.booklet_style,
            config.style
        ) 
        self.detail = config.detail

    def _render_start(self):
        self.canvas.saveState()
        if self.rotate:
            width, height = self.canvas._pagesize
            self.canvas.translate(width / 2, height / 2)
            self.canvas.rotate(180)
            self.canvas.translate(-width / 2, -height / 2)
        self.canvas.translate(self.corner.x, self.corner.y)

    def _render_end(self):
        self.canvas.restoreState()

    @abstractmethod
    def draw(self):
        pass

    def render(self, canvas, corner, rotate, dim):
        self.canvas = canvas # draw on this canvas
        self.rotate = rotate # need to rotate 
        self.corner = corner # panel corner
        self.max = dim
        self.mid = Point(x=self.max.x/2, y=self.max.y/2)
        logger.debug("BLANK render()")

        self._render_start()
        
        if self.style.showframe:
            self.canvas.setStrokeColor(self.style.frame.color) 
            # self.canvas.rect(x=20, y=10, width=100, height=50, stroke=1, fill=0) 
            self.canvas.rect(0, 0, self.max.x, self.max.y, stroke=1, fill=0)

        self.draw()
        self._render_end()



@PageFactory.register("blank")
class BlankPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def draw(self):
        pass
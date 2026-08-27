from abc import ABC, abstractmethod

from models.config import PageConfig
from models.styles import *
from models.resolver import resolve_page_style
from pages.factory import PageFactory

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "blank"
)
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
            width, height = canvas._pagesize
            self.canvas.translate(width / 2, height / 2)
            self.canvas.rotate(180)
            self.canvas.translate(-width / 2, -height / 2)
        self.canvas.translate(self.corner.x, self.corner.y)

    def _render_end(self):
        self.canvas.restoreState()

    # @abstractmethod
    def render(self, canvas, corner, rotate, dim):
        self.canvas = canvas # draw on this canvas
        self.rotate = rotate # need to rotate 
        self.corner = corner # panel corner
        self.panel_dim = dim # size of the panel
        logger.debug("BLANK render()")

        self._render_start()
        # if self.style.showframe:
        if True:
            self.canvas.setStrokeColor("red") 
            self.canvas.rect(x=20, y=10, width=100, height=50, stroke=1, fill=0) 

        self._render_end()
        pass

    """
    def renderStart(self, canvas, rotate, corner, sizewh):
        self.mid = Point(sizewh.x / 2, sizewh.y / 2)
        self.max = Point(sizewh.x, sizewh.y)
        canvas.saveState()
        if rotate:
            width, height = canvas._pagesize
            canvas.translate(width / 2, height / 2)
            canvas.rotate(180)
            canvas.translate(-width / 2, -height / 2)
        canvas.translate(corner.x, corner.y)

        if self.get_style("drawFrame") and self.get_style("colorFrame") is not None:
            canvas.setStrokeColor(self.get_style("colorFrame"))
            canvas.rect(0, 0, self.max.x, self.max.y)

    def renderEnd(self, canvas, rotate, corner, sizewh):
        canvas.restoreState()

    def render(self, canvas, rotate, corner, sizewh):
        self.renderStart(canvas, rotate, corner, sizewh)
        self.draw(canvas)
        self.renderEnd(canvas, rotate, corner, sizewh)
    """
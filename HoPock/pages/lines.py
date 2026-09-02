from pages.base import Page
from pages.factory import PageFactory
from models.page_details import LinesPageDetail
from reportlab.lib.units import inch

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "lines",
    detail_class=LinesPageDetail
)

class LinesPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        self.spacing = self.detail.spacing * inch
        logger.debug(f"{self.detail.spacing}=>{self.spacing}")

    def draw(self, resume=False):
        if self.config.titletext:
            ypos = self._draw_title() - self.spacing
        else:
            ypos = self.max.y - self.spacing
        xmin, xmax = self.style.margin, self.max.x - self.style.margin
        while ypos > 0: #self.spacing:
            self.canvas.line(xmin, ypos, xmax, ypos)
            ypos -= self.spacing
        logger.debug ("Rendering a lines")


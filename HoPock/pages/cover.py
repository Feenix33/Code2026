from pages.base import Page
from pages.factory import PageFactory
from models.page_details import CoverPageDetail
from reportlab.lib.units import inch

import re
import logging
logger = logging.getLogger(__name__)

"""
Simple cover page
Three boxes of text
Box 1 in Title text
Box 2 in big text
Box 3 in regular text

magic proportions
horizontal
1/6   2/3  1/6

vertical
1/8 top
3/8 bottom
1/2 top
3/4 top

    titleyper: float = 0.875 # y percent pos of title 7/8
    box2yper: float = 0.5  # y percent pos of title 1/2
    box3yper: float = 0.25  # y percent pos of box3 1/4
    titleht: float = 0.25    # y percent of title box size
    titlefill: str = None   # fill color
"""

@PageFactory.register(
    "cover",
    detail_class=CoverPageDetail
)

class CoverPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        logger.debug (f"Cover details {self.detail}")

    def _draw_centered_lines(self, text, ypos, font):
        self._set_font(font)
        if text:
            lines = re.split(r'\n|\\n|\r|\\r', text)
            for line in lines:
                ypos -= self.canvas._leading
                self.canvas.drawCentredString(self.mid.x, ypos, line)

    def draw(self, resume=False):
        detail = self.detail
        logger.debug ("Rendering a simple cover page")
        xleft = self.max.x / 6
        # xright = self.max.x - xleft
        xwidth = self.max.x - 2*xleft
        ytitle = self.max.y * detail.titleyper
        ybox2 = self.max.y * detail.box2yper
        ybox3 = self.max.y * detail.box3yper
        titleht = self.max.y * detail.titleht
        ybox1 = ytitle - titleht

        # draw a box around tht title vox
        do_stroke=0
        if detail.titlebox: 
            self._set_line_format(self.style.line)
            do_stroke=1

        # get the fill color
        do_fill = 0
        if detail.titlefill:
            self.canvas.setFillColor(detail.titlefill)
            do_fill=1
        # draw the box
        self.canvas.rect(xleft, ybox1, xwidth, titleht, stroke=do_stroke, fill=do_fill)

        # title box
        self._draw_centered_lines(self.config.titletext, ytitle, self.style.title.font)

        # box 2
        self._draw_centered_lines(self.detail.box2text, ybox2, self.style.font_medium)

        # box 3
        self._draw_centered_lines(self.detail.box3text, ybox3, self.style.font)

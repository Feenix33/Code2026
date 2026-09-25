from pages.base import Page
from pages.factory import PageFactory
from models.page_details import ListPageDetail
from reportlab.lib.units import inch

import logging
logger = logging.getLogger(__name__)
"""
Options
    spacing: float = 0.25  # inches from one line to next if zero, use current font leading
    number: int = 10    max number of items, will process up to this number or add if there is room
    box: str = 'x'      x=boxes o=circles #=numbered
    mylist: list[str]   user can supply a list of items that are pre-printed
    file:               Get the list from the file instead, one item per line
"""
@PageFactory.register(
    "list",
    detail_class=ListPageDetail
)

class ListPage(Page):
    # LIST_PAGE_DEFAULT_FONT_SIZE = 14

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        self.spacing = None
        # logger.debug(f"{self.detail.spacing}=>{self.spacing}")
        # if config.style.font.size is None:
        #     self.style.font.size = self.LIST_PAGE_DEFAULT_FONT_SIZE

    def draw(self, resume=False):
        logger.debug (f"Drawing list page with params {self.detail}")
        if self.detail.spacing:
            self.spacing = int(self.detail.spacing * inch)
        else:
            use_font = self.style.font_large
            self._set_font(use_font)
            self.spacing = int(self.leading)

        if self.config.titletext:
            ypos = self._draw_title() - self.spacing
        else:
            ypos = self.max.y - self.spacing*2

        # read the text lines if file exists
        if self.config.file:
            self.config.text = self._read_file(self.config.file)
            list_lines = self.config.text
        elif len(self.detail.mylist) > 0:
            list_lines = self.detail.mylist
        else:
            list_lines = self.config.text

        # x spacing for the line drawing
        xmin, xmax = self.style.margin, self.max.x - self.style.margin
        xleft = xmin + self.spacing * 1.2 # adding space for the checkboxes

        # number of lines to draw if provided else until run out of room
        # max_lines = 100 if self.detail.number == 0 else self.detail.number
        if self.detail.number == 0:
            max_lines = 100
        elif self.detail.number < 0:
            max_lines = len(list_lines)
        else:
            max_lines = self.detail.number
        atline = 0

        # set the linespec
        self._set_Line_format_default()

        ymin = self.spacing/2 # magic numbers to add additional margin on bottom

        while atline < max_lines and ypos > ymin:
            boxdim = self.spacing * 0.8
            xpos = xleft
            if self.detail.checkbox == "x":
                self.canvas.rect(xmin, ypos, boxdim, boxdim, stroke=1, fill=0)
            elif self.detail.checkbox == "o":
                radius = boxdim / 2
                self.canvas.circle(xmin+radius, ypos+radius, radius, stroke=1, fill=0)
            else: # self.detila.checkbox = "#":
                xpos = xmin
                textline = f"{(atline+1):2d}"
                self.canvas.drawString(xmin, ypos, textline)

            # draw words if they exist, else draw a line
            if atline < len(list_lines)  and len(list_lines[atline]) > 0:
                textline = list_lines[atline]
                self.canvas.drawString(xleft, ypos, textline)
            else:
                if self.detail.drawlines:
                    self.canvas.line(xleft, ypos, xmax, ypos)

            # increment to next line
            ypos -= self.spacing
            atline += 1
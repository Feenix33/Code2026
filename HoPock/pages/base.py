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
        self.leading = None

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

    # =======================================================
    # generic support
    # =======================================================
    def _set_line_format(self, line_fmt: Line):
        if line_fmt.color:
            self.canvas.setStrokeColor(line_fmt.color)
        if line_fmt.width:
            self.canvas.setLineWidth(line_fmt.width)
        if line_fmt.dash is not None and line_fmt.dash > 0:
            dash_on = int(line_fmt.dash/10)
            dash_off = line_fmt.dash %10
            self.canvas.setDash([dash_on, dash_off], phase=0) 
            pass

    def _set_Line_format_default(self):
        self._set_line_format(self.style.line)


    def _set_font(self, font= None):
        if not font:
            font = self.style.font
        self.canvas.setFont(font.name, font.size)
        self.canvas.setFillColor(font.color)
        self.leading = self.canvas._leading

    def _set_font_title(self):
        self._set_font(self.style.titlefont)

    def _draw_title(self, title_str=None, ypos=None):
        self.canvas.saveState()
        self._set_font_title()
        x = self.mid.x
        y = ypos if ypos is not None else self.max.y - self.leading
        title = title_str if title_str is not None else self.config.title
        if title:
            self.canvas.drawCentredString(x, y, title)
            y -= self.leading
        self.canvas.restoreState()
        return y




    # =======================================================
    # Drawing routines
    # =======================================================
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

        # move to the proper panel area
        self._render_start()
        
        if self.style.showframe:
            self.canvas.setStrokeColor(self.style.frame.color) 
            # self.canvas.rect(x=20, y=10, width=100, height=50, stroke=1, fill=0) 
            self.canvas.rect(0, 0, self.max.x, self.max.y, stroke=1, fill=0)

        # set the generic stuff
        self._set_font()
        self._set_Line_format_default()

        self.draw()
        self._render_end()



@PageFactory.register("blank")
class BlankPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def draw(self):
        ypos = None
        if self.config.title:
            ypos = self._draw_title()

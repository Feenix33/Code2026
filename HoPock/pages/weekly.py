
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import WeeklyPageDetail
from utility import header_lcr, parse_mystery_date_string, get_monday, flip_format_string
from datetime import datetime, timedelta
from models.styles import Font 

import logging
logger = logging.getLogger(__name__)

@PageFactory.register("weekly", expands_to=["weekly_left", "weekly_right"],detail_class=WeeklyPageDetail)

class WeeklyPage(Page):
    DAYS = []

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        detail = self.config.detail
        monday = None

    def draw(self, resume=False):
        # detail = self.config.detail
        logger.error ("Should not be rendering a weekly")
        # logger.debug ("Rendering a weekly")
        # logger.debug(f"{self.detail}")

    def _detail_draw(self):
        logger.debug (f"Rendering a weekly page detail {self.DAYS}")
        # logger.debug(f"{self.detail}")
        detail = self.config.detail
        monday = None
        if detail.day:
            monday = parse_mystery_date_string(detail.day)
        monday = get_monday(monday)
        logger.debug (f"Monday = {monday} {type(monday)}")
        startday = monday if len(self.DAYS) == 3 else monday+timedelta(days=3)

        # title_fmt = "\t{dd}=={mmm}" if detail.dayformat is None else detail.dayformat
        if detail.dayformat is None:
            logger.error (" Default format string is not set")
        title_fmt = detail.dayformat
        
        if detail.flipformat and len(self.DAYS) == 4:
            title_fmt = flip_format_string(title_fmt)

        # drawing routines
        # border lines
        y_third = (self.max.y -2*self.mgn)/ 3
        xleft = self.mgn
        xmid = (self.max.x / 2)
        ypts = [self.mgn,  self.mgn+ y_third, self.mgn + 2*y_third,]
        xwidth = self.max.x - (2*self.mgn)

        self.canvas.rect(xleft, ypts[0], xwidth, 3*y_third, stroke=1, fill=0)
        self.canvas.line(xleft, ypts[1], xleft+xwidth, ypts[1])
        self.canvas.line(xleft, ypts[2], xleft+xwidth, ypts[2])

        self._set_font() # use default font

        y = y_third*3 #- self.canvas._leading # top box
        tl, tc, tr = header_lcr(title_fmt, startday)
        self._draw_title_lrc([tl,tc,tr], ypos=y, use_title_font=False) # No y means it computes from font size and dim

        y -= y_third # middle box
        tl, tc, tr = header_lcr(title_fmt, startday+timedelta(days=1))
        self._draw_title_lrc([tl,tc,tr], ypos=y, use_title_font=False) # No y means it computes from font size and dim

        y = ypts[1]  - self.canvas._leading  # bottom box
        tl, tc, tr = header_lcr(title_fmt, startday+timedelta(days=2))
        if len(self.DAYS) == 3:
            self._draw_title_lrc([tl,tc,tr], ypos=y, use_title_font=False) # No y means it computes from font size and dim
        else: # four days
            self._draw_title_lrc([tl,tc,tr], ypos=y, xleft=self.mgn, xright=self.mid.x, use_title_font=False) # No y means it computes from font size and dim
            self.canvas.line(xmid, ypts[0], xmid, ypts[1])
            tl, tc, tr = header_lcr(title_fmt, startday+timedelta(days=3))
            self._draw_title_lrc([tl,tc,tr], ypos=y, xleft=self.mid.x, xright=self.max.x-self.mgn, use_title_font=False) # No y means it computes from font size and dim

        # self._draw_title_lrc([tl,tc,tr], ypos=, use_title_font=False)
        # md += timedelta(days=1)
        
         

@PageFactory.register("weekly_left", detail_class=WeeklyPageDetail)
class PageWeeklyLeft(WeeklyPage):
    DAYS = ["Monday", "Tuesday", "Wednesday"]

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def draw(self, resume=False):
        logger.debug ("Rendering a weekly left")
        self._detail_draw()

@PageFactory.register("weekly_right", detail_class=WeeklyPageDetail)
class PageWeeklyRight(WeeklyPage):
    DAYS = ["Thursday", "Friday", "Saturday", "Sunday"]

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def draw(self, resume=False):
        logger.debug ("Rendering a weekly right")
        self._detail_draw()


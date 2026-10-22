from pages.base import Page
from pages.factory import PageFactory
from models.page_details import WorkWeekPageDetail
from utility import header_lcr, parse_mystery_date_string, get_monday
from datetime import datetime, timedelta
from models.styles import Font 
import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "workweek",
    detail_class=WorkWeekPageDetail
)
class WorkWeekPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)

    def draw(self, resume=False):

        self.startLandscape()
        detail = self.config.detail
        logger.debug (f"Rendering workweek {self.detail}")

        # what day are we on
        monday_date = None
        if detail.date:
            monday_date = parse_mystery_date_string(detail.date)
        monday_date = get_monday(monday_date)
  

        xleft = self.mgn
        xright = self.max.x - self.mgn
        self._set_font(self.style.font_medium)
        ypos = self.max.y - (self.leading * 1.5)

        # get the title text fmt, date
        titlefmt = self.config.titletext
        if titlefmt:
            tl, tc, tr = header_lcr(titlefmt, monday_date)
            #for tt in [tl, tc, tr]:
            #    if len(tt) > 0:
            #        logger.debug (f"Text is {tt}")
            # ypos=None, xleft=None, xright=None, use_title_font=True
            ypos = self._draw_title_lrc([tl,tc,tr], ypos=ypos, xleft=xleft, xright=xright, use_title_font=False) 


        # use_font = self.style.font
        self._set_font(self.style.font) #_medium)
        self._set_Line_format_default()

        dx = (self.max.x - (2*self.mgn))/5
        self.canvas.rect(xleft, self.mgn, self.max.x-(2*self.mgn), ypos-self.mgn, stroke=1, fill=0)

        # vertical lines
        xpos = self.mgn + dx
        while xpos < self.max.x:
            self.canvas.line(xpos, ypos, xpos, self.mgn)
            xpos += dx

        ypos -= self.leading
        xpos = self.mgn + (dx/2)
        n = 0
        datefmt = '\t' + self.detail.dateformat
        for n in range(5):
            tl, tc, tr = header_lcr(datefmt, monday_date+timedelta(days=n))
            self.canvas.drawCentredString(xpos, ypos, tc)
            xpos += dx
            # n += 1

        # horiz line
        ypos -= self.leading
        self.canvas.line(self.mgn, ypos, self.max.x-self.mgn, ypos)


        self.endLandscape()

         



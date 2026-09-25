
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import DailyPageDetail
from utility import header_lcr, parse_mystery_date_string
from datetime import datetime
from models.styles import Font 

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "daily",
    detail_class=DailyPageDetail
)
class DailyPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        # logger.debug ("Daily created")
        # logger.debug ("Effective Style")
        # logger.debug (self.style)
        # logger.debug ("Detail")
        # logger.debug (self.config.detail)

    def draw(self, resume=False):

        detail = self.config.detail
        logger.debug ("Rendering a daily")

        # what day are we on
        thisday = None
        if detail.day:
            thisday = parse_mystery_date_string(detail.day)

        # use_font = self.style.font
        self._set_font() # use default font

        # get the title text fmt, date
        tl, tc, tr = header_lcr("{dd}\t{mmmm}\t{yyyy}", thisday)
        for tt in [tl, tc, tr]:
            if len(tt) > 0:
                logger.debug (f"Text is {tt}")

        y = self._draw_title_lrc([tl,tc,tr]) # No y means it computes from font size and dim
        logger.debug(f"{self.detail}")
        start_time = datetime.strptime(detail.start, "%H:%M")
        end_time = datetime.strptime(detail.end, "%H:%M")
        current_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        if end_minutes <= current_minutes:
            end_minutes += 12 * 60

        self._set_font(self.style.font) #_medium)

        xmin= self.mgn + self._string_width("00:00 ")
        xmin= self.mgn
        xmax = self.max.x - self.mgn

        ydec = self._line_height() + 2
        if self.detail.stretch:
            nn = ((end_minutes - current_minutes) / detail.increment)+1
            ydec = int(y / nn) - 2

        y1 = self._line_height()
        y2 = ydec - y1

        while current_minutes <= end_minutes and y > self._line_height()/2:
            if self.detail.dividers:
                self.canvas.line(xmin, y, xmax, y)

            y -= y1

            hours, minutes = divmod(current_minutes, 60)
            self.canvas.drawString(self.mgn, y, f"{hours:02}:{minutes:02}")
            current_minutes += detail.increment

            y -= y2
        
         



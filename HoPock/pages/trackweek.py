from pages.base import Page
from pages.factory import PageFactory
from models.page_details import TrackWeekPageDetail
from reportlab.lib.units import inch

import logging
logger = logging.getLogger(__name__)
"""
Options
    mylist: list[str]   user can supply a list of items that are pre-printed
    file:               Get the list from the file instead, one item per line
"""
@PageFactory.register(
    "track_week",
    detail_class=TrackWeekPageDetail
)

class TrackWeekPage(Page):
    # LIST_PAGE_DEFAULT_FONT_SIZE = 14

    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)


    def draw(self, resume=False):
        logger.debug (f"Drawing week track with params {self.detail}")
        self.startLandscape()

        if self.config.titletext:
            ypos = self._draw_title()
        else:
            ypos = self.max.y

        # set the styles
        self._set_Line_format_default()
        self._set_font(self.style.font_large)
        lineht = self.canvas._leading
        ypos -= lineht * 1.5

        label_list = []
        if self.detail.habits:
            label_list = self.detail.habits.split("|")
        if len(self.config.text):
            label_list = self.config.text

        # dimensions
        xw = self.mid.x / 7
        xpos = self.mid.x

        if self.detail.header:
            for d in ["M", "T", "W", "T", "F", "S", "S"]:
                self.canvas.drawCentredString(xpos, ypos, d)
                xpos += xw
            ypos -= lineht

        max_habits = self.detail.number if self.detail.number else 100
        if max_habits < 0: max_habits = len(label_list)

        logger.debug(f"max={max_habits} number={self.detail.number}")

        n = 0
        while max_habits > 0 and ypos > lineht:
            if n < len(label_list):
               self.canvas.drawString(self.mgn, ypos, label_list[n])
            else:
               y = ypos - lineht/2
               self.canvas.line(self.mgn, y, self.mid.x-self.mgn, y)
            #    self.canvas.drawString(self.mgn, ypos, "Habit")
            xpos = self.mid.x
            r = lineht/2-1
            dow = 'MTWRTSS'
            for j in range(7):
                box = None
                if self.detail.checkbox in {'0','o', 'O'}:
                    box = 'circle'
                elif self.detail.checkbox in {'x','X','#'}:
                    box = 'square'
                else:
                    if n % 2:
                        box = 'circle'
                    else:
                        box = 'square'
                if box == 'circle':
                    self.canvas.circle(xpos, ypos, r, stroke=1, fill=0)
                else:
                    self.canvas.rect(xpos-r, ypos-r, 2*r, 2*r, stroke=1, fill=0)

                if self.detail.dow:
                    self._set_font(self.style.font_medium)
                    self.canvas.drawCentredString(xpos, ypos-(self.canvas._leading/3), dow[j])
                    self._set_font(self.style.font_large)

                xpos += xw
            ypos -= self.canvas._leading
            n += 1
            max_habits -= 1


        self.endLandscape()

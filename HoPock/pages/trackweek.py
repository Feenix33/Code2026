import logging
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import TrackWeekPageDetail
from reportlab.lib.units import inch

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

    def _init_layout(self):
        """Initializes shared configurations, fonts, and sets up baseline tracking variables."""
        if self.config.titletext:
            ypos = self._draw_title()
        else:
            ypos = self.max.y

        self._set_Line_format_default()
        self._set_font(self.style.font_large)
        
        lineht = self.leading
        ypos -= lineht * 1.5

        # Build shared label list
        label_list = []
        if self.detail.habits:
            label_list = self.detail.habits.split("|")
        if len(self.config.text):
            label_list = self.config.text

        # Determine limit of habits
        max_habits = self.detail.number if self.detail.number else 100
        if max_habits < 0: 
            max_habits = len(label_list)

        return ypos, lineht, label_list, max_habits

    def _draw_checkbox_row(self, x_start, ypos, xw, r, row_index):
        """Draws a standard row of 7 tracking indicators (circles or squares)."""
        xpos = x_start
        dow = 'MTWRTSS'

        for j in range(7):
            # Resolve shape
            if self.detail.checkbox in {'0', 'o', 'O'}:
                box = 'circle'
            elif self.detail.checkbox in {'x', 'X', '#'}:
                box = 'square'
            else:
                box = 'circle' if row_index % 2 else 'square'

            # Render shape
            if box == 'circle':
                self.canvas.circle(xpos, ypos, r, stroke=1, fill=0)
            else:
                self.canvas.rect(xpos - r, ypos - r, 2 * r, 2 * r, stroke=1, fill=0)

            # Optional Day of Week overlay
            if self.detail.dow:
                self._set_font(self.style.font_medium)
                self.canvas.drawCentredString(xpos, ypos - (self.canvas._leading / 3), dow[j])
                self._set_font(self.style.font_large)

            xpos += xw

    def _horizontal(self):
        logger.debug(f"Horizontal weekly track with params {self.detail}")
        self.startLandscape()

        ypos, lineht, label_list, max_habits = self._init_layout()
        xw = self.mid.x / 7

        # Optional header layout for landscape
        if self.detail.header:
            xpos = self.mid.x
            for d in ["M", "T", "W", "T", "F", "S", "S"]:
                self.canvas.drawCentredString(xpos, ypos, d)
                xpos += xw
            ypos -= lineht

        n = 0
        while max_habits > 0 and ypos > lineht:
            if n < len(label_list):
                self.canvas.drawString(self.mgn, ypos, label_list[n])
            else:
                y = ypos - lineht / 2
                self.canvas.line(self.mgn, y, self.mid.x - self.mgn, y)

            r = lineht / 2 - 1
            self._draw_checkbox_row(x_start=self.mid.x, ypos=ypos, xw=xw, r=r, row_index=n)

            ypos -= self.canvas._leading
            n += 1
            max_habits -= 1

        self.endLandscape()

    def _vertical(self):
        logger.debug(f"Weekly Tracker in vertical mode {self.detail}")
        ypos, lineht, label_list, max_habits = self._init_layout()
        
        xw = (self.max.x * 0.75) / 7

        n = 0
        while max_habits > 0 and ypos > lineht * 2:
            if n < len(label_list):
                self.canvas.drawString(self.mgn, ypos, label_list[n])
            else:
                xright = self.max.x * 0.75
                self.canvas.line(self.mgn, ypos, xright, ypos)

            ypos -= self.leading
            r = lineht / 2 - 1
            
            self._draw_checkbox_row(x_start=self.mid.x / 2, ypos=ypos, xw=xw, r=r, row_index=n)

            ypos -= self.leading * 1.75
            n += 1
            max_habits -= 1

    def draw(self, resume=False):
        if self.detail.portrait:
            self._vertical()
        else:
            self._horizontal()

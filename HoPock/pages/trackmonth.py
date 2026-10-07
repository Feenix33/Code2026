import logging
from pages.base import Page
from pages.factory import PageFactory
from models.page_details import TrackMonthPageDetail
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

""" 
Options
    mylist: list[str]   user can supply a list of items that are pre-printed
    file:               Get the list from the file instead, one item per line
"""
@PageFactory.register(
    "track_month",
    detail_class=TrackMonthPageDetail
)
class TrackMonthPage(Page):
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
        label_list = (label_list + ["", ""])[:2]

        # Determine limit of habits
        # max_habits = self.detail.number if self.detail.number else 100 # 100 is unlimited
        # if max_habits < 0: 
        #     max_habits = len(label_list)
        # if max_habits > 2: max_habits = 2
        # if max_habits > self.detail.count: max_habits = self.detail.count

        # Fallback to 100 if passed count is falsy, or use length of label_list if negative
        max_habits = self.detail.count if (self.detail.count or 0) >= 0 else len(label_list)
        # if max_habits: print (f"11111111111111 {max_habits}")
        max_habits = max_habits or 100 
        # print (f"222222222 {max_habits}")
        # Bound upper limits cleanly
        max_habits = min(max_habits, 2) #, self.detail.count)
        # print (f"3333333333333333 {max_habits}")

        # Get the habit count for the months
        #habit_count = [int(x.strip()) for x in (self.detail.habitcount or "").split('|') if x.strip().isdigit()]
        habit_count = [
            min(int(x.strip()), 49) 
            for x in (self.detail.habitcount or "").split('|') 
            if x.strip().isdigit()
        ]
        habit_count = (habit_count + [31, 31])[:2]


        return ypos, lineht, label_list, max_habits, habit_count

    def _draw_checkbox_grid(self, xleft, ypos, dx, dy, rad, total, draw_labels):
        """Draws a standard row of 7 tracking indicators (circles or squares)."""
        xpos = xleft

        nd = 0 # number drawn <= habit_count
        ri = 0 # row index

        # Resolve shape
        if self.detail.checkbox in {'x', 'X', '#'}:
            box = 'square'
        else:
            box = 'circle'

        while nd < total:

            # Render shape
            if box == 'circle':
                self.canvas.circle(xpos, ypos, rad, stroke=1, fill=0)
            else:
                self.canvas.rect(xpos - rad, ypos - rad, 2 * rad, 2 * rad, stroke=1, fill=0)

            # Optional Day number
            if draw_labels:
                self._set_font(self.style.font_medium)
                self.canvas.drawCentredString(xpos, ypos - (self.canvas._leading / 3), str(nd+1))
                self._set_font(self.style.font_large)

            xpos += dx
            nd += 1
            ri += 1
            if ri >= 7:
                ri = 0
                xpos = xleft
                ypos -= dy

        return ypos

    """
        count: int = 0             # max number of items 0 = infinite
        checkbox: str = None        # x=boxes o=circles
        habits: str = None          # habits separated by | 
        label: bool = True          # put numbers in the boxes
        habitcount: str = None      # string representing how many boxes
    """
    def draw(self, resume=False):
        logger.debug(f"Monthly Tracker render w/details {self.detail}")
        ypos, lineht, label_list, max_habits, habit_count = self._init_layout()
        # logger.debug(f"{label_list} for {max_habits}")
        # logger.debug(f"{habit_count}")

        n = 0
        while n < max_habits:
            # habit label
            # logger.debug(f"Drawing {label_list[n]}")
            if len(label_list[n]) > 0:
                self.canvas.drawString(self.mgn, ypos, label_list[n])
            else:
                ypos -= lineht
                xright = self.max.x * 0.75
                self.canvas.line(self.mgn, ypos, xright, ypos)

            ypos -= lineht

            # draw the grid
            dx = (self.max.x - (2*self.mgn)) / 7
            dy = lineht
            rad = (lineht/2) 
            dx = 2*rad + 2
            xleft = (self.max.x - 7*dx) / 2
            total = habit_count[n]
            draw_labels = self.detail.label
            ypos = self._draw_checkbox_grid(xleft, ypos, dx, dy, rad, total, draw_labels)
            ypos -= lineht
            
            n += 1

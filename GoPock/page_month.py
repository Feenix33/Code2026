from page import Page, PageFactory
from datetime import datetime, date as dt_date
from utils import parse_date_value
import calendar

def month_calendar_list(d: dt_date, start_of_week: int = 0) -> list:
    """
    Return a flat list representing the days of the month containing `d`,
    padded with '' at the front so the list lines up with weekday columns.

    start_of_week: 0 = Sunday (default), 1 = Monday, 2 = Tuesday, ... 6 = Saturday

    Loop through the result 7 at a time to print a calendar grid.
    """
    year, month = d.year, d.month

    # weekday() : Monday=0 ... Sunday=6
    first_weekday, days_in_month = calendar.monthrange(year, month)

    # Convert Python's Monday=0 convention to Sunday=0 convention
    first_weekday_sun0 = (first_weekday + 1) % 7  # Sunday=0 ... Saturday=6

    # Shift according to the requested start_of_week
    pad_count = (first_weekday_sun0 - start_of_week) % 7

    result = [""] * pad_count + list(range(1, days_in_month + 1))
    return result


@PageFactory.register("month")
class PageMonth(Page):
    def __init__(self, title=None, titleFormat="\t%b %Y", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title
        self.titleFormat = titleFormat

    def draw(self, canvas):
        wordFont = self.get_style("fontTitle")
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        pageDate = parse_date_value(self.get_style("date") or dt_date.today())

        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        y = self.max.y - (self.next_line(canvas) * 1.5)

        # titleFormat = self.get_style("titleFormat") or
        titleFormat = self.titleFormat
        self.drawCanvasThreePart(canvas, y, formatStr=titleFormat, titleStr=self.title, date=pageDate)
        y -= self.next_line(canvas)

        myfont = self.get_style("font")
        self.useCanvasFont(canvas, myfont)

        # get the drawing dimensions
        weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        dx = int((self.max.x - 20)/7) # 20 is 2* hardcoded margin
        xpos = 10 + dx/2
        for day in weekdays:
            canvas.drawCentredString(xpos, y, day)
            xpos += dx

        # print (f"Month:{month_calendar_list(d=pageDate)}")
        # print (f"today:{pageDate}")
        # print (f"titleFormat:{titleFormat}")

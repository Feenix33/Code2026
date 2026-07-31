from page import Page, PageFactory
from datetime import datetime, date as dt_date
# from utils import parse_date_value
from utils import parse_flexible_date
from reportlab.pdfbase.pdfmetrics import stringWidth
import calendar

"""
Month Reference
Simple page with little modification to print a month reference

Parameters beyond standard:
date
weekday: Start of the week. Mon=0
count: How many months to print (either 1 or 2)
"""

@PageFactory.register("monthref")
class PageMonthRef(Page):
    def __init__(self, title=None, **kwargs):
        super().__init__()
        # Set defaults
        self.title = title

    def _draw_month(self, canvas, myfont, aMonth, yIn):
        y = yIn
        # month name
        y -= self.next_line(canvas)
        monthName = aMonth[0].strip()
        canvas.drawCentredString(self.mid.x, y, monthName)

        # get xpos so we can print left justified
        wkWidth = stringWidth(aMonth[1], myfont.name, myfont.size)
        xpos = (self.max.x - wkWidth) / 2
        for aweek in aMonth[1:]:
            y -= self.next_line(canvas)
            if y > 0:
                canvas.drawString(xpos, y, aweek)
        return y

    def draw(self, canvas):
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        # pageDate = parse_date_value(self.get_style("date")) or dt_date.today()
        pageDate = parse_flexible_date(self.get_style("date")) or dt_date.today()
        # how many months to print
        countMonth = self.get_style("count") or 2
        countMonth = int(countMonth)

        # get start of week and generate a calendar
        startWeekday = self.get_style("weekday") or 6
        calendar.setfirstweekday(startWeekday)
        thisMonth = calendar.month(pageDate.year, pageDate.month).splitlines()

        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        y = self.max.y - (self.next_line(canvas) * 1.)

        myfont = self.get_style("font")
        myfont.name = "Courier"    # need fixed width font for this to work
        self.useCanvasFont(canvas, myfont)

        y = self._draw_month(canvas, myfont, thisMonth, y)

        # check if printing a second month
        if countMonth >= 2:
            # get the next month
            if pageDate.month == 12:
                nextMonth = calendar.month(pageDate.year+1, 1).splitlines()
            else:
                nextMonth = calendar.month(pageDate.year, pageDate.month+1).splitlines()

            y -= self.next_line(canvas)
            y = self._draw_month(canvas, myfont, nextMonth, y)

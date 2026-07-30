from page import Page, PageFactory
from datetime import datetime, date as dt_date
from utils import parse_date_value
from reportlab.pdfbase.pdfmetrics import stringWidth
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
        self.setLineSpec(canvas)

        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        pageDate = parse_date_value(self.get_style("date") or dt_date.today())

        thisMonth = calendar.month(pageDate.year, pageDate.month).splitlines()
        gridMonth = calendar.monthcalendar(pageDate.year, pageDate.month)

        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        y = self.max.y - (self.next_line(canvas) * 1.5)

        if self.title is not None:
            title = self.title
            titleFormat = self.titleFormat
        else:
            title = thisMonth[0].strip()
            titleFormat = "\t%s"

        self.drawCanvasThreePart(canvas, y, formatStr=titleFormat, titleStr=title, date=pageDate)
        y -= self.next_line(canvas)

        # switch to normal font
        myfont = self.get_style("font")
        self.useCanvasFont(canvas, myfont)

        # get the drawing dimensions
        dx = int((self.max.x - 20)/7) # 20 is 2* hardcoded margin
        xpos = 10 + dx/2

        ybgn = y + myfont.size * 0.2
        yend = 10
        ylen = ybgn - yend
        dy = (ylen - canvas._leading*1.5) / len(gridMonth) # sub off the lines for days of week; grid month has number of weeks
        yoff = canvas._leading *1.0
        canvas.line(10, ybgn, 10, yend)
        canvas.line(10+dx, ybgn, 10+dx, yend)

        # do days of week
        for dow in thisMonth[1].split(" "):
            canvas.drawCentredString(xpos, y, dow)
            xpos += dx

        y -= self.next_line(canvas, 1.5)

        # do the days # !! Switch to grid cal
        for week in gridMonth:
            xpos = 10 + (stringWidth("M", myfont.name, myfont.size)/2) # add a little buffer

            for dow in week:
                if dow != 0:
                    canvas.drawString(xpos, y, f"{dow}")
                xpos += dx
            canvas.line(10, y+yoff, self.max.x-10, y+yoff)
            y -= dy
        canvas.line(10, yend, self.max.x - 10, yend)
        for j in range(7):
            canvas.line(10 + j * dx, ybgn, 10 + j * dx, yend)
        canvas.line(self.max.x-10, ybgn, self.max.x-10, yend)

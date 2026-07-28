from page import Page, PageFactory
from datetime import datetime, date as dt_date, timedelta

# Debug only:
from reportlab.lib import colors

from data_classes import Font

@PageFactory.register("daily")
class DailyPage(Page):
    def _set_today(self, today):
        if today is None:
            return dt_date.today()

        if isinstance(today, dt_date):
            return today

        if isinstance(today, str):
            try:
                return dt_date.fromisoformat(today)
            except ValueError:
                try:
                    return dt_date.strptime(today, "%m/%d/%Y")
                except ValueError:
                    raise ValueError(f"Unsupported date string: {today}")

        if isinstance(today, int):
            return dt_date.today() + timedelta(days=today)

        raise TypeError(f"Unsupported date value: {today!r}")

    def __init__(self, date=None, title=None, titleFormat="%d%b\t\t%a", timeFormat="%I:%M", startTime="08:00", endTime="17:00", timeIncrement=30, timeLine=False, **kwargs):
        super().__init__()
        self.date = self._set_today(date)
        self.title = title
        self.titleFormat = titleFormat
        self.timeFormat = timeFormat
        self.startTime = startTime
        self.endTime = endTime
        self.increment = timeIncrement
        self.timeLine = bool(timeLine)
        self.flip = kwargs.get("flip", False)
        self.flip = bool(self.flip)

        if "titleFormat" not in self.overrides:
            self.overrides["titleFormat"] = self.titleFormat

        if self.flip:
            self.titleFormat = self.flip_title_format(self.titleFormat)

    def get_style(self, path):
        style = super().get_style(path)
        if path == "fontTitle" and style is None:
            return Font(size=10)
        if path == "font" and style is None:
            return Font(size=8)
        return style

    def _generate_time_list(self, start="08:00", end="17:00", format="%I:%M", increment=30, count=10):
        # Use a fixed base date to handle time arithmetic safely
        base_date = datetime.today()

        # Parse start time string (HH:MM)
        start_h, start_m = map(int, start.split(":"))
        current_time = base_date.replace(
            hour=start_h, minute=start_m, second=0, microsecond=0
        )

        time_list = []
        time_delta = timedelta(minutes=increment)

        # Scenario 1: Generate based strictly on count if end is None
        if end is None:
            for _ in range(count):
                time_list.append(current_time.strftime(format)) 
                current_time += time_delta

        # Scenario 2: Generate up until the specified end time
        else:
            end_h, end_m = map(int, end.split(":"))
            end_time = base_date.replace(hour=end_h, minute=end_m, second=0, microsecond=0)

            while current_time <= end_time:
                time_list.append(current_time.strftime(format))
                current_time += time_delta

        return time_list

    def _draw_header(self, canvas, y):
        titleFormat = self.get_style("titleFormat")
        if titleFormat is None:
            titleFormat = "%b%d\t\t%a"
        if self.flip:
            titleFormat = self.flip_title_format(titleFormat)
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        self.printCanvasThreePart(canvas, y, formatStr=titleFormat, titleStr="My Daily Page", date=self.date)
        return canvas._leading

    def draw(self, canvas):
        self.flip = self.get_style("flip") or False
        self.flip = bool(self.flip)

        times = self._generate_time_list(
            start=self.startTime,
            end=self.endTime,
            increment=self.increment,
            format=self.timeFormat,
        )

        y = self.max.y
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        # if self.title and len(self.title) > 0:
        y -= self._draw_header(canvas, y)
        y -= self.next_line(canvas)

        myfont = self.get_style("font")
        self.useCanvasFont(canvas, myfont)
        linespec = self.get_style("linespec")
        self.setLineSpec(canvas, linespec)

        y -= self.next_line(canvas)
        j = 0
        while y > 10 and j < len(times):
            if self.flip:
                canvas.drawRightString(self.max.x-10, y, f"{times[j]}")
            else:
                canvas.drawString(10, y, f"{times[j]}")
            if self.timeLine and j%2 == 1:
                y -= 2
                canvas.line(10, y, self.max.x-10, y)
                # y -= 2
            y -= self.next_line(canvas)
            j += 1

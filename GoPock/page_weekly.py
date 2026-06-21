from page import Page, PageFactory
from datetime import datetime, date, timedelta

# Debug only:
from reportlab.lib import colors


def get_current_week_monday(target_date=None):
    """Get the Monday of the week containing target_date.

    If target_date is None, uses today's date.

    Args:
        target_date: datetime.date object or string in YYYY-MM-DD format

    Returns:
        datetime.date object for the Monday of that week
    """
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    days_since_monday = target_date.weekday()
    return target_date - timedelta(days=days_since_monday)


class WeeklyPage(Page):
    """Shared weekly page behavior for left/right weekly pages."""

    def __init__(self, date=None, title=None, dateFormat="%b %d", **kwargs):
        super().__init__()
        self.date = date
        self.title = title
        self.dateFormat = dateFormat
        self.week_monday = self._get_week_start()
        self.days = self._build_days()

    def get_style(self, path):
        style = super().get_style(path)
        if path == "font" and style is not None:
            from dataclasses import replace
            from data_classes import Font

            if isinstance(style, Font) and "font.size" not in self.overrides:
                return replace(style, size=max(1, int(style.size * 0.8)))
        return style

    def _get_week_start(self):
        return get_current_week_monday(self.date)

    def _build_days(self):
        raise NotImplementedError("Subclasses must define _build_days().")

    def _draw_header(self, canvas, y):
        titleFormat = self.get_style("titleFormat")
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        # printCanvasThreePart(self, canvas, y, formatStr=None, titleStr=None, date=None):
        self.printCanvasThreePart(
            canvas,
            y,
            formatStr=titleFormat, # self.dateFormat,
            titleStr=self.title,
            # date=self.week_monday,
            date=self.days[0],
        )
        return canvas._fontsize*2
    
    def _draw_weekly(self, canvas):
        y = self.max.y
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        if self.title and len(self.title) > 0:
            y -= self._draw_header(canvas, y)

        myfont = self.get_style("font")
        self.useCanvasFont(canvas, myfont)
        linespec = self.get_style("linespec")
        self.setLineSpec(canvas,linespec)

        ypts = [y, 2*y/3, y/3,  0]
        for ypt in ypts:
            canvas.line(0, ypt, self.max.x, ypt)
        canvas.line(self.max.x, y, self.max.x, 0)
        canvas.line(0, y, 0, 0)
        if len(self.days) > 3:
            canvas.line(self.mid.x, ypts[2], self.mid.x, 0)
        self.printCanvasThreePart(canvas, ypts[0],
                                    formatStr=self.dateFormat,
                                    titleStr=None,
                                    date=self.days[0] )
        self.printCanvasThreePart(canvas, ypts[1],
                                    formatStr=self.dateFormat,
                                    titleStr=None,
                                    date=self.days[1] )
        if len(self.days) == 3:
            self.printCanvasThreePart(canvas, ypts[2],
                                        formatStr=self.dateFormat,
                                        titleStr=None,
                                        date=self.days[2] )
        else:
            self.printCanvasThreePart(canvas, ypts[2],
                                        formatStr=self.dateFormat,
                                        titleStr=None,
                                        date=self.days[2], 
                                        xmin=0, xmax=self.mid.x)
            self.printCanvasThreePart(canvas, ypts[2],
                                        formatStr=self.dateFormat,
                                        titleStr=None,
                                        date=self.days[3],
                                        xmin=self.mid.x, xmax=self.max.x )


@PageFactory.register("weeklyleft")
class PageWeeklyLeft(WeeklyPage):
    """Left page of weekly spread showing Monday, Tuesday, Wednesday."""

    def __init__(self, date=None, title=None, dateFormat="%b %d", **kwargs):
        super().__init__(date=date, title=title, dateFormat=dateFormat, **kwargs)

    def _build_days(self):
        return [self.week_monday + timedelta(days=i) for i in range(3)]

    def draw(self, canvas):
        """Draw the left weekly page."""
        self._draw_weekly(canvas)
        # TODO: Implement detailed draw routine for Monday-Wednesday


@PageFactory.register("weeklyright")
class PageWeeklyRight(WeeklyPage):
    """Right page of weekly spread showing Thursday, Friday, Saturday, Sunday."""

    def __init__(self, date=None, title=None, dateFormat="%b %d", **kwargs):
        super().__init__(date=date, title=title, dateFormat=dateFormat, **kwargs)

    def _build_days(self):
        return [self.week_monday + timedelta(days=i) for i in range(3, 7)]

    def draw(self, canvas):
        """Draw the right weekly page."""
        # self._draw_header(canvas)
        self._draw_weekly(canvas)
        # TODO: Implement detailed draw routine for Thursday-Sunday

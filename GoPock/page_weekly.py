from page import Page, PageFactory
from datetime import datetime, date, timedelta


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

    def __init__(self, date=None, title="Weekly Page", dateFormat="%b %d", **kwargs):
        super().__init__()
        self.date = date
        self.title = title
        self.dateFormat = dateFormat
        self.week_monday = self._get_week_start()
        self.days = self._build_days()

    def _get_week_start(self):
        return get_current_week_monday(self.date)

    def _build_days(self):
        raise NotImplementedError("Subclasses must define _build_days().")

    def _draw_header(self, canvas):
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        self.printCanvasThreePart(
            canvas,
            self.mid.y,
            formatStr=self.dateFormat,
            titleStr=self.title,
            # date=self.week_monday,
            date=self.days[0],
        )


@PageFactory.register("weeklyleft")
class PageWeeklyLeft(WeeklyPage):
    """Left page of weekly spread showing Monday, Tuesday, Wednesday."""

    def __init__(self, date=None, title="Weekly Left", dateFormat="%b %d", **kwargs):
        super().__init__(date=date, title=title, dateFormat=dateFormat, **kwargs)

    def _build_days(self):
        return [self.week_monday + timedelta(days=i) for i in range(3)]

    def draw(self, canvas):
        """Draw the left weekly page."""
        self._draw_header(canvas)
        # TODO: Implement detailed draw routine for Monday-Wednesday


@PageFactory.register("weeklyright")
class PageWeeklyRight(WeeklyPage):
    """Right page of weekly spread showing Thursday, Friday, Saturday, Sunday."""

    def __init__(self, date=None, title="Weekly Right", dateFormat="%b %d", **kwargs):
        super().__init__(date=date, title=title, dateFormat=dateFormat, **kwargs)

    def _build_days(self):
        return [self.week_monday + timedelta(days=i) for i in range(3, 7)]

    def draw(self, canvas):
        """Draw the right weekly page."""
        self._draw_header(canvas)
        # TODO: Implement detailed draw routine for Thursday-Sunday

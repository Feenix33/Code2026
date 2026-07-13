from page import Page, PageFactory
from reportlab.lib.units import inch

@PageFactory.register("tracker")
class PageTracker(Page):
    def __init__(self, title="Habit Tracker", spacing=0.25, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing

    def draw(self, canvas):
        self.startLandscape(canvas)
        colorLine = self.get_style("colorLine")


        y = self.max.y
        y -= 2.5 * self.standardTitle(canvas, self.max.y )#- (canvas._fontsize*1.5))
        # wordFont = self.get_style("fontTitle")
        # self.useCanvasFont(canvas, self.get_style("fontTitle"))
        # titleFormat = self.get_style("titleFormat")
        # pageDate = self.get_style("date")
        # # print(f"Title: {self.title}, Format: {titleFormat}, Date: {pageDate}")
        # self.printCanvasThreePart(canvas, self.max.y, formatStr=titleFormat, titleStr=self.title, date=pageDate)

        habits = self.get_style("habits")
        if habits is not None:
            habits = habits.split("|")
        else:
            habits = []
        habitcount = self.get_style("habitCount")
        if habitcount is None:
            habitcount = len(habits)
        else:
            habitcount = int(habitcount)
            if len(habits) < habitcount:
                habits += [""] * (habitcount - len(habits))
        print(f"DEBUG: {self.debugID} {len(habits)} habits: {habits}")
        print(f"DEBUG: {self.debugID} habitcount: {habitcount}")

        canvas.setStrokeColor(colorLine)
        dx= canvas._fontsize
        j = 0
        while y > 0 and j < habitcount:
            x = self.max.x - dx* 12
            if len(habits[j]) > 0:
                canvas.drawString(10, y, f"{habits[j]}")
            else:
                canvas.line(10, y, x-10, y)

            for i in range(7):
                x += dx * 1.5
                canvas.rect(x, y, dx, dx, stroke=1, fill=0)

            y -= (canvas._fontsize*1.5)
            j += 1

        self.stopLandscape(canvas)

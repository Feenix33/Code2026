from page import Page, PageFactory
from reportlab.lib.units import inch

@PageFactory.register("tracker")
class PageTracker(Page):
    def __init__(self, title="Habit Tracker", **kwargs):
        super().__init__()
        self.title = title
        self.default_habitcount = 5

    def draw(self, canvas):
        self.startLandscape(canvas)
        self.setLineSpec(canvas)

        habitbox = self.get_style("habitbox")
        if habitbox is None:
            habitbox = False
        else:
            habitbox = bool(habitbox)

        self.useTitleFont(canvas)
        y = self.max.y - self.next_line(canvas, 1)
        self.standardTitle(canvas, y )#- (canvas._fontsize*1.5))
        y -= self.next_line(canvas)

        self.setStandardFont(canvas)

        # add the day of week
        dow = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        dx= canvas._fontsize # use this later for habit lines
        x = self.max.x - dx* 12 #needs to match later

        for j in range(7):
            x += dx * 1.5
            canvas.drawString(x, y, f"{dow[j]}")
        y -= canvas._fontsize * 1.5

        habits = self.get_style("habits")
        habitcount = self.get_style("habitCount")
        if habits is not None:
            habits = habits.split("|")
        else:
            habits = []
        if habitcount is None:
            habitcount = len(habits)
        else:
            habitcount = int(habitcount)
        if habitcount == 0:
            habitcount = self.default_habitcount
        if len(habits) < habitcount:
            habits += [""] * (habitcount - len(habits))
        # print(f"DEBUG: {self.debugID} {len(habits)} habits: {habits}")
        # print(f"DEBUG: {self.debugID} habitcount: {habitcount}")

        j = 0
        while y > 0 and j < habitcount:
            x = self.max.x - dx* 12
            if len(habits[j]) > 0:
                canvas.drawString(10, y, f"{habits[j]}")
            else:
                canvas.line(10, y, x-10, y)

            for i in range(7):
                x += dx * 1.5
                if habitbox: canvas.rect(x, y, dx, dx, stroke=1, fill=0)
                else: canvas.circle(x + dx/2, y + dx/2, dx/2, stroke=1, fill=0)

            y -= self.next_line(canvas)
            j += 1

        self.stopLandscape(canvas)

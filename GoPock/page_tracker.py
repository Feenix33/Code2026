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
        self.setLineSpec(canvas)

        habitbox = self.get_style("habitbox")
        if habitbox is None:
            habitbox = False
        else:
            habitbox = bool(habitbox)

        y = self.max.y
        y -= 2.5 * self.standardTitle(canvas, self.max.y )#- (canvas._fontsize*1.5))

        # add the day of week
        dow = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        dx= canvas._fontsize # use this later for habit lines
        x = self.max.x - dx* 12 #needs to match later

        for j in range(7):
            x += dx * 1.5
            canvas.drawString(x, y, f"{dow[j]}")
        y -= canvas._fontsize * 1.5

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

            y -= (canvas._fontsize*1.5)
            j += 1

        self.stopLandscape(canvas)

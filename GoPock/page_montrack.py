from page import Page, PageFactory
from reportlab.lib.units import inch

@PageFactory.register("montrack")
class PageMonTrack(Page):
    def __init__(self, title="Monthly Tracker", spacing=0.25, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing
        self.default_habit_count = 2
        self.max_habits = 2


    def draw(self, canvas):

        #helper function for line spacing
        def space_down(lines=1): 
            nonlocal y
            y -= canvas._leading * 1.5 * lines


        self.setLineSpec(canvas)
        canvas.rect(0, 0, self.max.x, self.max.y, stroke=1, fill=0) # temp for debugging

        habitbox = self.get_style("habit.box")
        habitbox = bool(habitbox) if habitbox is not None else False

        y = self.max.y
        y -= 1.0 * self.standardTitle(canvas, self.max.y )

        #switch to standard font
        self.setStandardFont(canvas)

        #add a blank line sepa
        y -= canvas._fontsize * 1.5
        space_down()

        # prep habit titles
        habits = self.get_style("habit.list")
        habitcount = self.get_style("habit.count")
        if habits is not None:
            habits = habits.split("|")
        else:
            habits = []
        if habitcount is None:
            habitcount = len(habits)
            if habitcount == 0:
                habitcount = self.default_habit_count
        else:
            habitcount = int(habitcount)
        if len(habits) < habitcount:
            habits += [""] * (habitcount - len(habits))


        # loop through the habits
        # habit
        # calendar of check boxes

        #setup
        dx = canvas._leading # box width
        dxstart = (self.max.x-((7+3))*dx)/2 # start of box row

        # day of week and compute coords
        dow = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
        day_offset = self.get_style("habit.offset")
        day_offset = int(day_offset) if day_offset is not None else 0

        # main loop
        j = 0
        while y > 0 and j < habitcount and j < self.max_habits:
            x = 0
            if len(habits[j]) > 0:
                canvas.drawString(10, y, f"{habits[j]}")
            else:
                canvas.line(10, y, self.mid.x, y)

            x = dxstart
            space_down()
            # day of week indicators
            for i in range(7):
                canvas.drawString(x, y, f"{dow[(i+day_offset)%7]}")
                x += (1.5*dx)
            
            for w in range (5):
                space_down()
                x = dxstart
                for i in range(7):
                    if habitbox: canvas.rect(x, y, dx, dx, stroke=1, fill=0)
                    else: canvas.circle(x + dx/2, y + dx/2, dx/2, stroke=1, fill=0)
                    x += (1.5*dx)

            # next habit
            space_down(lines=2)
            j += 1

        # self.stopLandscape(canvas)

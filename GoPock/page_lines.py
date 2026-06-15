from page import Page, PageFactory
from reportlab.lib.units import inch
# import pprint

@PageFactory.register("line")
@PageFactory.register("lines")
class PageLines(Page):
    def __init__(self, title="None", spacing=0.25, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing

    def draw(self, canvas):
        spacing = self.get_style("spacing") * inch
        colorLine = self.get_style("colorLine")

        # draw the lines
        canvas.setStrokeColor(colorLine)
        y = self.max.y - spacing # start at top
        while y > 0:
            canvas.line(0, y, self.max.x, y)
            y -= spacing
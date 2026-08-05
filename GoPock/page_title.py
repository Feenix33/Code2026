from page import Page, PageFactory
from reportlab.lib.units import inch
# import pprint


@PageFactory.register("cover")
@PageFactory.register("title")
class PageTitle(Page):
    def __init__(self, title="Pocket Planner", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title


    def draw(self, canvas):
        titlefont = self.get_style("fontTitle")
        bodyfont = self.get_style("font")
        lastfont = self.get_style("font")
        lastfont.size *= 0.8

        line1 = self.get_style("line1")
        line2 = self.get_style("line2")
        line3 = self.get_style("line3")
        

        ystart = self.max.y*0.70
        yend = self.max.y*0.30
        ypt = ystart
        self.useCanvasFont(canvas, titlefont)
        canvas.drawCentredString(self.mid.x, ypt, self.title)

        ypt -= (titlefont.size * 1.2) * 2
        self.useCanvasFont(canvas, self.get_style("font"))
        lines = [line1, line2, line3]
        for line in lines:
            if line is not None:
                canvas.drawCentredString(self.mid.x, ypt, line)
            ypt -= self.next_line(canvas)

        #draw bounding box
        xbgn = 0.25 * inch
        xend = self.max.x - xbgn
        linespec = self.get_style("linespec")
        self.setLineSpec(canvas, linespec)

        #rect is (x, y, width, height) line is (x, y, x, y)
        # canvas.rect(xbgn, ystart, xend-xbgn, ystart-ypt, fill=0) 
        def myrect(x1, y1, x2, y2):
            canvas.rect(x1, y1, x2-x1, y2-y1, fill=0)

        ystart += titlefont.size * 1.4
        myrect(xbgn, ystart, xend, ypt)
        # double border
        mgn = 4
        myrect(xbgn-4, ystart+4, xend+4, ypt-4)

from pages.base import Page
from pages.factory import PageFactory
from models.page_details import GridPageDetail
from reportlab.lib.units import inch
from models.data_classes import Point

import logging
logger = logging.getLogger(__name__)

@PageFactory.register(
    "grid",
    detail_class=GridPageDetail
)

class GridPage(Page):
    def __init__(self, config, booklet_style):
        super().__init__(config, booklet_style)
        if self.detail.grid == Point(0.0, 0.0):
            self.grid = Point(self.detail.spacing * inch, self.detail.spacing * inch)
        else:
            self.grid = self.detail.grid # initialize grid
            if self.grid.x == 0.0:
                self.grid.x = self.detail.spacing
            self.grid.x *= inch
            if self.grid.y == 0:
                self.grid.y = self.detail.spacing
            self.grid.y *= inch
    

    def draw(self):
        if self.config.title:
            ypos = self._draw_title() #- self.grid.y
        else:
            ypos = self.max.y - self.grid.y

        # set the line style
        self._set_Line_format_default()
        
        # compute number of lines in the grid (minus 1)
        nvert = int((self.max.x-2*self.style.margin)/ self.grid.x)
        nhorz = int (ypos / self.grid.y)

        # compute limits of drawing
        width = nvert * self.grid.x
        height = nhorz * self.grid.y
        xmin = (self.max.x - width) / 2
        xmax = xmin + width
        ymin = ypos
        ymax = ypos - height # note that ymax is smaller than ymin because grid is upside down

        # draw the horizontals
        # ypos = ymin
        for y in range(nhorz+1):
            self.canvas.line(xmin, ypos, xmax, ypos)
            ypos -= self.grid.y

        # draw the verticals
        xpos = xmin
        for x in range(nvert+1):
            self.canvas.line(xpos, ymin, xpos, ymax)
            xpos += self.grid.x
        
        # xmin, xmax = self.style.margin, self.max.x - self.style.margin
        # ymin, ymax = 0, ypos
        # for y in range(int(ymin), int(ymax), int(self.grid.y)):
        #     self.canvas.line(xmin, y, xmax, y)
        # # for x in range(int(xmin), int(xmax), int(self.grid.x)):
        # #     self.canvas.line(x, ymin, x, ymax)
        # nv = int(self.max.x / self.grid.x) + 1 # number of vertical lines
        # print (nv)
        # xpos = (self.max.x - (nv-1)*self.grid.x) / 2
        # for _ in range(nv):
        #     self.canvas.line(xpos, ymin, xpos, ymax)
        #     xpos += self.grid.x




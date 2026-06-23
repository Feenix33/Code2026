from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen.canvas import Canvas

from data_classes import PageStyle, BookletStyle, Point
from page import Page

class Booklet:
    def __init__(self):
        self.docSize = landscape(letter)
        self.style = PageStyle()
        self.config = BookletStyle()
        # Controls whether pages may be added automatically when content overflows
        self.addPages = False
        self.pages = []

    def add_page(self, page=None):
        page.book = self
        self.pages.append(page)
        return page

    def computePaneCorners(self):
        width, height = self.docSize
        margin = self.config.margin
        fWidth = (width / 4) - margin * 2
        fHeight = (height / 2) - margin * 2

        f0 = Point(0 * fWidth + 1 * margin, 0 * fHeight + 1 * margin)
        f1 = Point(1 * fWidth + 3 * margin, 0 * fHeight + 1 * margin)
        f2 = Point(2 * fWidth + 5 * margin, 0 * fHeight + 1 * margin)
        f3 = Point(3 * fWidth + 7 * margin, 0 * fHeight + 1 * margin)
        corners = [f0, f1, f2, f3, f0]
        return corners

    def render(self):
        self.corners = self.computePaneCorners()
        self.margin = self.config.margin
        self.sizewh = Point( (self.docSize[0] - 8 * self.margin) / 4, (self.docSize[1] - 4 * self.margin) / 2 )
        # Page.max.x = (self.docSize[0] - 8 * margin) / 4
        # Page.max.y = (self.docSize[1] - 4 * margin) / 2
        # Page.mid.x = Page.max.x / 2
        # Page.mid.y = Page.max.y / 2
        self.canvas = Canvas(self.config.nameOut, pagesize=self.docSize)

        self.n = 0
        for page in self.pages:
            if page is not None:
                page.render(self.canvas, rotate=((self.n%8) not in [0, 1, 2, 3]), corner=self.corners[self.n % 4], sizewh=self.sizewh)
            self.n += 1
            if self.n >= 8:
                self.canvas.showPage()
                self.n= 0
                # import sys
                # print(f"DEBUG {sys._getframe().f_code.co_name}() n={n}")

        self.canvas.save()
    
    def insertOverflow(self, page):
        import sys
        # print(f"DEBUG {sys._getframe().f_code.co_name}(page.debugID) Attempting page insertion n={self.n}")
        page.renderEnd(self.canvas, rotate=((self.n%8) not in [0, 1, 2, 3]), corner=self.corners[self.n % 4], sizewh=self.sizewh)
        self.n += 1
        if self.n >= 8:
            self.canvas.showPage()  
            self.n= 0
        page.renderStart(self.canvas, rotate=((self.n%8) not in [0, 1, 2, 3]), corner=self.corners[self.n % 4], sizewh=self.sizewh)

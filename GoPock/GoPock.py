"""
exCanvasFrame.py
Build a document with canvas and frames
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
import reportlab.lib.enums
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Spacer, Paragraph, PageBreak, Image
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Point:
    x: float
    y: float


class Style:
    def __init__(self, parent=None, **values):
        self.parent = parent
        self.values = values

    def get(self, name):
        if name in self.values:
            return self.values[name]

        if self.parent:
            return self.parent.get(name)

        raise KeyError(name)

class Page(ABC):
    DEFAULT_colorFrame = colors.blue
    DEFAULT_colorGrid = colors.lightgrey
    mid = Point(0,0) # mid.x, mid.y for center of page
    max = Point(0,0) # max.x, max.y for top right corner of page
 
    def __init__(self, booklet, style=None, **kwargs):
        #kwargs = self._convert_types(kwargs)
        self.book = booklet

        self.style = Style(
            parent=booklet.style
        )

        if style:
            self.style.values.update(style)
        
 
    @abstractmethod
    def draw(self, canvas):
        pass

    def render(self, canvas, rotate, corner):
        #print (f"Rendering page with title {self.title} at corner {corner} with rotate={rotate}")
        canvas.saveState()
        if rotate: 
            width, height = canvas._pagesize
            canvas.translate(width/2, height/2)
            canvas.rotate(180)
            canvas.translate(-width/2, -height/2)
        canvas.translate(corner.x, corner.y)

        #frame drawing logic
        if self.style.get("drawFrame") and self.style.get("colorFrame") is not None:
            canvas.setStrokeColor(self.style.get("colorFrame"))
            canvas.rect(0,0, Page.max.x, Page.max.y)
        
        self.draw(canvas)
        canvas.restoreState()
 
    def buildParagraphStyle(self, name='CurrentStyle',
            textColor=colors.black,
            backColor=colors.white,
            alignment=reportlab.lib.enums.TA_LEFT,
            align=None,
            firstLineIndent=0,
            leftIndent=0,
            bulletIndent=0,
            fontName='Times', #'Helvetica',
            fontSize=10,
            spaceBefore=0,
            spaceAfter=None,
            leading=None):
        if leading == None: leading = int(fontSize * 1.2)
        if spaceAfter == None: spaceAfter = int(fontSize * 1.2)
        tempAlign = alignment if align == None else self.alignmentStrToEnum(align.lower())
        return ParagraphStyle(
            name=name,
            backColor = backColor,
            textColor = textColor,
            alignment = tempAlign,
            firstLineIndent = firstLineIndent,
            leftIndent=leftIndent,
            bulletIndent=bulletIndent,
            fontName=fontName,
            fontSize=fontSize,
            spaceBefore=spaceBefore,
            spaceAfter=spaceAfter,
            leading=leading)


class PageWord(Page):
    def __init__(self, booklet, style=None, title="Generic PageWord", **kwargs):
        super().__init__(booklet, style, **kwargs)
        self.title = title


    def draw(self, canvas):
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(Page.mid.x, Page.mid.y, self.title)

class TextPage(Page):
    def __init__(self, booklet, text="", style=None, title="Generic TextPage", **kwargs):
        super().__init__(booklet, style, **kwargs)
        self.text = text
        self.title = title

    def draw(self, canvas):
        mgn = 10
        frame = Frame(mgn, mgn, Page.max.x - mgn, Page.max.y - mgn, showBoundary=1)
        currentStyle = self.buildParagraphStyle()
        obj = Paragraph(self.text, currentStyle)
        frame.add(obj, canvas)


class Booklet:
    def __init__(self):
        self.style = Style(
            title="Default Title",
            drawFrame=False,
            colorFrame=colors.black,
            colorGrid=colors.lightgrey,
            margin = 10,
            fontSize = 10,
            fontName = "Helvetica",
        )
        self.docSize = landscape(letter) 
        self.nameOut = "GoPock.pdf"
        self.pages = []
        #print ("Booklet initialized")
        pass

    def add_page(self, page=None):
        if page is None:
            page = Page(self)

        self.pages.append(page)
        return page
  
    def computePaneCorners(self):
        width, height = self.docSize
        margin = self.style.get("margin")
        # 6 5 4 3 upside down
        # 7 0 1 2
        fWidth = (width / 4) - margin*2
        fHeight = (height / 2) - margin*2

        f0 = Point(0*fWidth+1*margin, 0*fHeight+1*margin)
        f1 = Point(1*fWidth+3*margin, 0*fHeight+1*margin)
        f2 = Point(2*fWidth+5*margin, 0*fHeight+1*margin)
        f3 = Point(3*fWidth+7*margin, 0*fHeight+1*margin)
        corners = [f0,f1,f2,f3, f0]
        #print("Page corners computed")
        return corners

    def render(self):
        #print ("Rendering the booklet")

        self.corners = self.computePaneCorners()
        margin = self.style.get("margin")
        Page.max.x = (self.docSize[0] - 8*margin) / 4
        Page.max.y = (self.docSize[1] - 4*margin) / 2
        Page.mid.x = Page.max.x / 2
        Page.mid.y = Page.max.y / 2
        self.canvas = Canvas(self.nameOut, pagesize=self.docSize)
        #self.drawFoldlines()
        n = 0
        for page in self.pages:
            if page is not None:
                #print (f"Rendering page {n}")
                page.render(self.canvas, rotate=(n not in [0,1,2,3]), corner=self.corners[n%4])
            n += 1
        
        self.canvas.save()

def main():
    booklet = Booklet()
    booklet.add_page(
        PageWord(booklet, 
                 title="Word Page"))
    booklet.add_page(
        PageWord(booklet, 
                title="Bravo 2"))
    
    booklet.add_page(
        TextPage(booklet, 
                 style={
                    "colorFrame": colors.blue,
                    "drawFrame": True
                 }, 
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."))

    booklet.add_page(
        TextPage(booklet, 
                 text="2 <i>Lorem ipsum</i> dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."*2))

    booklet.add_page(
        PageWord(booklet, 
                 title="Second Word Page"))
    booklet.add_page(
        PageWord(booklet, 
                 title="Bravo Two2"))
    
    booklet.add_page(
        TextPage(booklet, 
                 style={
                    "colorFrame": colors.blue,
                    "drawFrame": True
                 }, 
                 text="3 <b>Lorem ipsum dolor</b> sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "*3))
    



    booklet.render()

if __name__ == '__main__':
    main()

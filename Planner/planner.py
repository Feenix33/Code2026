"""
Pocket planner 8-pg
72 points per inch

fonts: Helvetica, Times, Courier
Alignment: 0-TA_LEFT 1-center 2-right 4-justify

This order:
    3R   2R
    4    1

Eight is 
7 6 5 4 upside down
8 1 2 3

COMMANDS
.font <font params> adjust the current font
.newpage    force a framebreak (page because pocket docs)
.spacer     add a spacer of current font size
.file       Read in a file and process it, ignore config in the file 

CONFIG
.frames     Show frames
.fold       Show folds 
.margin #   Size of margins
.separator  Separator/spacer after every paragraph
.version    Version number

PAGES
.grid <spacing> <color>
.lines <spacing> <color>
.day <start> <last> <spacing> <date>
.week <start>
.month <start>
.year <year>
.todo <title> <spacing>
.shop <title>


FONT PARAMETERS
            textColor=colors.black,
            backColor=colors.white,
            alignment=reportlab.lib.enums.TA_LEFT,
            align=None,
            firstLineIndent=0,
            leftIndent=0,
            bulletIndent=0,
            fontName='Helvetica',
            fontSize=10,
            spaceBefore=0,
            spaceAfter=None,
            leading=None):

NOTES:
- The padding is between the border and the text in the prototype:
    Frame(x1, y1, width,height, leftPadding=6, bottomPadding=6, rightPadding=6, topPadding=6, id=None, showBoundary=0)

"""

import argparse
import sys
import os
import datetime
import re
import unicodedata
from reportlab.lib.pagesizes import A4, landscape, letter, portrait
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
import reportlab.lib.enums 
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Spacer, Paragraph, PageBreak, Image
from dataclasses import dataclass
from abc import ABC, abstractmethod
import shlex

@dataclass
class Point:
    x: float
    y: float

def to_reportlab_color(val):
    if not isinstance(val, str):
        return val
    
    clean_val = val.replace('colors.','').strip().lower()
    if clean_val.startswith('#') or clean_val.startswith('#'):
        return colors.HexColor(clean_val)
    try: # handle named colors
        print (f"Trying to convert color value '{val}' to a ReportLab color")
        return getattr(colors, clean_val, colors.yellowgreen)
    except AttributeError:
        print (f"ValueError(Unknown color: {val} using black")
        return colors.black
    
class Page(ABC):
    mid = Point(0,0) # mid.x, mid.y for center of page
    max = Point(0,0) # max.x, max.y for top right corner of page
    fontsize = 10

    def __init__(self, **kwargs):
        kwargs = self._convert_types(kwargs)

        # Handle defaults
        if 'fontsize' in kwargs:
            self.fontsize = int(kwargs.pop('fontsize'))
                                      
        for key,value in kwargs.items():
            setattr(self, key, value)

    CONVERTERS = {
        'colorFrame': to_reportlab_color,
        'date': lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').date(),
        'daystart': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
    }

    def _convert_types(self, params):
        for key, values in params.items():
            if key in self.CONVERTERS:
                try:
                    params[key] = self.CONVERTERS[key](values)
                except Exception as e:
                    print(f"Error converting parameter '{key}' with value '{values}': {e}")
                    raise
        return params
    
    @abstractmethod
    def draw(self, canvas):
        pass

    def render(self, canvas, rotate, corner):
        print (f"Rendering page with title {self.title} at corner {corner} with rotate={rotate}")
        canvas.saveState()
        if rotate: 
            width, height = canvas._pagesize
            canvas.translate(width/2, height/2)
            canvas.rotate(180)
            canvas.translate(-width/2, -height/2)
        canvas.translate(corner.x, corner.y)
        colorFrame = getattr(self, 'colorFrame', None)
        if colorFrame is not None:
            print (f"Drawing frame for page with title {self.title} using color {colorFrame}")
            canvas.setStrokeColor(self.colorFrame)
            canvas.rect(0,0, Page.max.x, Page.max.y)
        self.draw(canvas)
        canvas.restoreState()


    
class BlankPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        print(f"Blank page with title {self.title}")
        pass

class GridPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        pass

class WordPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        canvas.setFont("Helvetica", self.fontsize)
        title = getattr(self, 'title', 'Word Page')
        canvas.drawCentredString(Page.mid.x, Page.mid.y, title)

class PageFactory:
    _registry = {
        'blank': BlankPage,
        'grid': GridPage,
        'word':  WordPage,
    }

    @classmethod
    def create_page(cls, page_type, **kwargs):
        page_class = cls._registry.get(page_type.lower())
        if page_class is None:
            raise ValueError(f"Unknown page type: {page_type}")
        return page_class(**kwargs)

class PlannerParser:
    @staticmethod
    def parse_line(line, factory):
        tokens = shlex.split(line)
        if not tokens:
            return None
        
        page_type = tokens[0].lower()
        kv_pairs = tokens[1:]
        kwargs = {}
        for kv in kv_pairs:
            if '=' in kv:
                key, value = kv.split('=', 1)
                kwargs[key] = value.rstrip(',')
            else:
                print(f"Warning: Ignoring invalid token '{kv}' in line: {line}")
        return factory.create_page(page_type, **kwargs) 


class Planner: 
    def __init__(self,nameOut="output.pdf", docSize=letter, marginSize=0.2*inch, showFrames=True, drawFolds=True, separator=False):
        self.docSize = docSize
        self.margin = marginSize # how big is the margin for each frame
        self.showFrames = showFrames # show the frame borders
        self.drawFolds = drawFolds # draw the fold lines or not
        self.canvas = None
        self.nameOut = nameOut
        self.fontSize = None
        self.separator = separator # put a spacer after every paragraph
        self.author = None # Metadata
        self.title = None # Metadata
        self.subject = None # Metadata
        self.keywords = None # Metadata
        self.version = None
        self.page1 = PageFactory.create_page('blank', colorFrame=colors.black, title="Page 1")
        self.page2 = PlannerParser.parse_line('word colorFrame=colors.blue, fontsize=24 title="Second Page"', PageFactory)
        self.page3 = PlannerParser.parse_line('word colorFrame=colors.orange, title="Page 3"', PageFactory)
 
    
    def create(self):
        self.docSize = landscape(self.docSize) 
        if self.fontSize == None:
            self.fontSize = 8
        self.corners = self.computePaneCorners()
        Page.max.x = (self.docSize[0] - 8*self.margin) / 4
        Page.max.y = (self.docSize[1] - 4*self.margin) / 2
        Page.mid.x = Page.max.x / 2
        Page.mid.y = Page.max.y / 2

        #Pane computation max, mid
        Page.max.x = (self.docSize[0] - 8*self.margin) / 4
        Page.max.y = (self.docSize[1] - 4*self.margin) / 2
        Page.mid.x = Page.max.x / 2
        Page.mid.y = Page.max.y / 2

        self.canvas = Canvas(self.nameOut, pagesize=self.docSize)
        self.frameN = 0
        if self.drawFolds: self.drawFoldlines() #self.canvas)
        self.page1.render(self.canvas, False, self.corners[1])
        self.page2.render(self.canvas, False, self.corners[2])
        self.page3.render(self.canvas, True, self.corners[0])

    def computePaneCorners(self):
        width, height = self.docSize
        margin = self.margin
        # 6 5 4 3 upside down
        # 7 0 1 2
        fWidth = (width / 4) - margin*2
        fHeight = (height / 2) - margin*2

        f0 = Point(0*fWidth+1*margin, 0*fHeight+1*margin)
        f1 = Point(1*fWidth+3*margin, 0*fHeight+1*margin)
        f2 = Point(2*fWidth+5*margin, 0*fHeight+1*margin)
        f3 = Point(3*fWidth+7*margin, 0*fHeight+1*margin)
        corners = [f0,f1,f2,f3]
        return corners

    def drawFoldlines(self):
        self.canvas.saveState()
        self.canvas.setDash(1,5) # on off
        self.canvas.line(0, self.docSize[1]/2, self.docSize[0], self.docSize[1]/2)
        self.canvas.setStrokeColor('red')
        for x in [2.75, 5.5, 8.25]: #TODO adjust to doc size
            self.canvas.line(x*inch, 0*inch, x*inch, 8.5*inch)
        self.canvas.restoreState()

    def makePlanner(self, inConfig):
        self.create()
        self.build()
        
    def build(self):
        if self.author != None: self.canvas.setAuthor(self.author)
        if self.title != None: self.canvas.setTitle(self.title)
        if self.subject != None: self.canvas.setSubject(self.subject)
        if self.keywords != None: self.canvas.setKeywords(self.keywords)
        self.canvas.save()


##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### 


def main():
    #Read command line arguments
    config = None
    outputFilename = 'Planner.pdf'

    booklet = Planner(nameOut=outputFilename)
    booklet.makePlanner(config)

if __name__ == '__main__':
    main()

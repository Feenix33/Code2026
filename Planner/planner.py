"""
Pocket planner 8-pg
72 points per inch

fonts: Helvetica, Times-Roman, Courier

Eight is 
7 6 5 4 upside down
8 1 2 3



TODO:
- daily
x- split format
x- lines no lines
-- line style dots or dash
-- start time
-- increment 30 or 60 minutes
x- hours right or left
x- leading zeros in hours
-- controls for all the above

- title font size
- bold title
- weekly two page spread
- weekly horizontal 5-day
- read from file
- monthly calendar
- yearly
- dots page
- image page
- some default icons w/on/off control
- dice page

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
        #print (f"Trying to convert color value '{val}' to a ReportLab color")
        return getattr(colors, clean_val, colors.yellowgreen)
    except AttributeError:
        print (f"ValueError(Unknown color: {val} using black")
        return colors.black
    
class Page(ABC):
    mid = Point(0,0) # mid.x, mid.y for center of page
    max = Point(0,0) # max.x, max.y for top right corner of page
    fontName = "Courier" # "Helvetica" "Times-Roman"
    
    def __init__(self, **kwargs):
        kwargs = self._convert_types(kwargs)

        # Handle defaults
        if 'fontsize' in kwargs:
            self.fontsize = int(kwargs.pop('fontsize'))
        else:
            self.fontsize = 10
        if 'drawFrame' in kwargs:
            self.drawFrame = kwargs.pop('drawFrame')
        else:
            self.drawFrame = True
                                      
        for key,value in kwargs.items():
            setattr(self, key, value)

    CONVERTERS = {
        'colorFrame': to_reportlab_color,
        'colorGrid': to_reportlab_color,
        'date': lambda v: datetime.datetime.strptime(v, '%Y-%m-%d').date(),
        'daystart': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'time': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'gridX': lambda v: int(v),
        'gridY': lambda v: int(v),
        'spacing': lambda v: float(v),
        'drawFrame': lambda v: v.lower() in ['true', '1', 'yes']
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
        #print (f"Rendering page with title {self.title} at corner {corner} with rotate={rotate}")
        canvas.saveState()
        if rotate: 
            width, height = canvas._pagesize
            canvas.translate(width/2, height/2)
            canvas.rotate(180)
            canvas.translate(-width/2, -height/2)
        canvas.translate(corner.x, corner.y)

        #frame drawing logic
        drawFrame = getattr(self, 'drawFrame', True)
        colorFrame = getattr(self, 'colorFrame', None)
        if drawFrame and colorFrame is not None:
            canvas.setStrokeColor(self.colorFrame)
            canvas.rect(0,0, Page.max.x, Page.max.y)
        
        self.draw(canvas)
        canvas.restoreState()
    
class BlankPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        #print(f"Blank page with title {self.title}")
        pass

class WordPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        fontName = getattr(self, 'fontName', Page.fontName)
        canvas.setFont(fontName, self.fontsize)
        title = getattr(self, 'title', 'Word Page')
        canvas.drawCentredString(Page.mid.x, Page.mid.y, title)

class GridPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #print(f"Grid color = {self.colorGrid}")

    def draw(self, canvas):
        #print(f"Drawing grid page with title {self.title} and drawFrame={self.drawFrame}")
        spacingX, spacingY = self._calculate_spacing()
        self._draw_grid_lines(canvas, spacingX, spacingY)

    def _calculate_spacing(self):
        """Calculate grid spacing based on gridX, gridY, or default spacing."""
        gridX = getattr(self, 'gridX', None)
        gridY = getattr(self, 'gridY', None)
        
        # Both None: use default spacing
        if gridX is None and gridY is None:
            spacing = getattr(self, 'spacing', 0.25) * inch
            return spacing, spacing
        
        # Only gridX: use it for both dimensions
        if gridX is not None and gridY is None:
            spacingX = Page.max.x / gridX
            return spacingX, spacingX
        
        # Only gridY: use it for both dimensions
        if gridY is not None and gridX is None:
            spacingY = Page.max.y / gridY
            return spacingY, spacingY
        
        # Both set: calculate independently
        spacingX = Page.max.x / gridX
        spacingY = Page.max.y / gridY
        return spacingX, spacingY

    def _draw_grid_lines(self, canvas, spacingX, spacingY):
        """Draw vertical and horizontal grid lines."""
        color = getattr(self, 'colorGrid', colors.lightgrey)
        canvas.setStrokeColor(color)
        
        for x in range(0, int(Page.max.x), int(spacingX)):
            canvas.line(x, 0, x, Page.max.y)
        
        for y in range(int(Page.max.y), 0, -int(spacingY)):
            canvas.line(0, y, Page.max.x, y)

class LinesPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        spacing = getattr(self, 'spacing', 0.25) * inch
        color = getattr(self, 'colorGrid', colors.lightgrey)
        canvas.setStrokeColor(color)
        
        yStart = int(Page.max.y)
        #print(f"Lines title: {self.title} with fontsize {self.fontsize} and spacing {spacing}")
        if self.title is not None:
            fontName = getattr(self, 'fontName', Page.fontName)
            canvas.setFont(fontName, self.fontsize)
            canvas.drawCentredString(Page.mid.x, yStart - (self.fontsize*1.5), self.title)
            yStart -= self.fontsize * 3

        for y in range(int(yStart), 0, -int(spacing)):
            canvas.line(0, y, Page.max.x, y)

class ListPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'check' in kwargs: self.check = kwargs['check'].lower()
        if 'checkbox' in kwargs: self.check = kwargs['checkbox'].lower()

    def draw(self, canvas):
        spacing = getattr(self, 'spacing', 0.25) * inch
        color = getattr(self, 'colorGrid', colors.lightgrey)
        canvas.setStrokeColor(color)
        checkbox = getattr(self, 'check', 'box') in ['box', 'checkbox', 'square']

        yStart = int(Page.max.y)
        if self.title is not None:
            canvas.setFont(self.fontName, self.fontsize)
            canvas.drawCentredString(Page.mid.x, yStart - (self.fontsize*1.5), self.title)
            yStart -= self.fontsize * 3

        checkbox_size = self.fontsize * 0.8
        margin = int (checkbox_size * 0.5)
        for y in range(int(yStart), int(checkbox_size/2), -int(spacing)):
            # Draw checkbox
            if checkbox:
                canvas.rect(margin, y - checkbox_size/2, checkbox_size, checkbox_size)
            else:
                canvas.circle(margin + checkbox_size/2, y, checkbox_size/2, stroke=1, fill=0)
            # Draw line for text
            canvas.line(checkbox_size + (margin*2), y - checkbox_size*0.8, Page.max.x-margin, y - checkbox_size*0.8)

class Daily(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        today = getattr(self, 'date', datetime.date.today())
        strToday = dayString(today, format="lll dd mmm yyyy")
        time_cur = getattr(self, 'time', datetime.time(7, 30))
        time_inc = getattr(self, 'timeInc', 30) # minutes

        if isinstance(time_cur, str):
            time_cur = datetime.datetime.strptime(time_cur  , '%H:%M').time()

        y = int(Page.max.y)
        justify = getattr(self, 'justify', 'center').lower()
        justify = 'splitDW'

        canvas.setFont(self.fontName, self.fontsize*1.5)
        if justify == 'left':
            canvas.drawString(10, y - (self.fontsize*1.5), strToday)
        elif justify == 'center':
            canvas.drawCentredString(Page.mid.x, y - (self.fontsize*1.5), strToday)
        elif justify == 'right':
            canvas.drawRightString(Page.max.x - 10, y - (self.fontsize*1.5), strToday)
        elif justify == 'splitWD':
            canvas.drawString(10, y - (self.fontsize*1.5), dayString(today, format="lll"))
            canvas.drawRightString(Page.max.x - 10, y - (self.fontsize*1.5), dayString(today, format="dd mmm"))
        elif justify == 'splitDW':
            canvas.drawString(10, y - (self.fontsize*1.5), dayString(today, format="dd mmm"))
            canvas.drawRightString(Page.max.x - 10, y - (self.fontsize*1.5), dayString(today, format="lll"))
        canvas.line(0, y - (self.fontsize*1.5) - 5, Page.max.x, y - (self.fontsize*1.5) - 5)
        y -= self.fontsize * 3
        canvas.setFont(self.fontName, self.fontsize)

        while y > int(self.fontsize/2):
            #time_label = time_cur.strftime("%I:%M").lstrip('0').lower()
            time_label = time_cur.strftime("%I:%M").lower()
            #canvas.drawString(10, y, time_label)
            offset = self.fontsize * 0.25
            #linestart = 10 + canvas.stringWidth(time_label, self.fontName, self.fontsize) + 5
            #canvas.line(linestart, y - offset, Page.max.x, y - offset)

            canvas.drawRightString(Page.max.x - 10, y, time_label)
            linestart = Page.max.x - 10 - canvas.stringWidth(time_label, self.fontName, self.fontsize) - 5
            canvas.line(10, y - offset, linestart, y - offset)

            time_cur = (datetime.datetime.combine(datetime.date.today(), time_cur)
                        + datetime.timedelta(minutes=int(time_inc))).time()
            y -= self.fontsize * 1.25

class PageFactory:
    _registry = {
        'blank': BlankPage,
        'grid': GridPage,
        'word':  WordPage,
        'lines': LinesPage,
        'line': LinesPage,
        'list': ListPage,
        'daily': Daily
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
        #self.showFrames = showFrames # show the frame borders
        self.drawFolds = drawFolds # draw the fold lines or not
        self.canvas = None
        self.nameOut = nameOut
        self.author = None # Metadata
        self.title = None # Metadata
        self.subject = None # Metadata
        self.keywords = None # Metadata

        self.pages = [None]*8
        #self.pages[0] = PageFactory.create_page('word', fontName="Times-Roman", colorFrame=colors.black, title="Page 1")
        self.pages[0] = PlannerParser.parse_line('daily justify=left date=2026-05-11 time=07:00', PageFactory)
        self.pages[1] = PlannerParser.parse_line('list fontName=Courier fontsize=18 colorFrame=colors.blue, title="GrocerieS"', PageFactory)
        self.pages[2] = PlannerParser.parse_line('list checkbox=square  spacing=0.25 drawFrame=False title="Shopping List"', PageFactory)
        self.pages[3] = PlannerParser.parse_line('grid colorFrame=colors.green colorGrid=blue title="4 GridPage"', PageFactory)
        self.pages[4] = PlannerParser.parse_line('grid drawFrame=False colorFrame=red, gridX=4 gridY=5 title="Grid 4"', PageFactory)
         
    
    def create(self):
        self.docSize = landscape(self.docSize) 
        #if self.fontSize == None:
        #    self.fontSize = 8
        self.corners = self.computePaneCorners()
        Page.max.x = (self.docSize[0] - 8*self.margin) / 4
        Page.max.y = (self.docSize[1] - 4*self.margin) / 2
        Page.mid.x = Page.max.x / 2
        Page.mid.y = Page.max.y / 2

        self.canvas = Canvas(self.nameOut, pagesize=self.docSize)
        #self.frameN = 0
        if self.drawFolds: self.drawFoldlines() #self.canvas)
        n = 0
        for page in self.pages:
            if page is not None:
                page.render(self.canvas, rotate=(n not in [0,1,2,3]), corner=self.corners[n%4])
            n += 1

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
        corners = [f0,f1,f2,f3, f0]
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

def dayString(date, format="ddmmmyyyy"):
    if isinstance(date, datetime.datetime):
        date = date.date()
    elif isinstance(date, str):
        date = datetime.datetime.fromisoformat(date).date()
    elif not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date, datetime.datetime, or ISO date string")

    day_name = date.strftime("%A")
    month_name = date.strftime("%B")
    month_abbrev = date.strftime("%b")
    day_num = date.day

    token_map = {
        'l': day_name.capitalize(),
        'lll': day_name[:3].capitalize(),
        'LLL': day_name[:3].upper(),
        'dd': f"{day_num:02d}",
        'd': str(day_num),
        'mmmm': month_name,
        'mmm': month_abbrev.capitalize(),
        'MMM': month_abbrev.upper(),
        'yy': date.strftime("%y"),
        'yyyy': date.strftime("%Y"),
    }

    # Use regex to replace tokens without affecting replacements
    pattern = re.compile(r'\b(' + '|'.join(re.escape(token) for token in sorted(token_map, key=len, reverse=True)) + r')\b')
    result = pattern.sub(lambda m: token_map[m.group(1)], format)
    return result

##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### 

def main():
    #Read command line arguments
    config = None
    outputFilename = 'Planner.pdf'

    booklet = Planner(nameOut=outputFilename)
    booklet.makePlanner(config)

if __name__ == '__main__':
    main()

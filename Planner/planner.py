"""
Pocket planner 8-pg
72 points per inch

fonts: Helvetica, Times-Roman, Courier

Eight is 
7 6 5 4 upside down
8 1 2 3



TODO:
- title font size
- bold title
- monthly ref
- yearly
- generic title handling routine
- hex page
- image page
- some default icons w/on/off control
- dice page
- cut line
- organize the colors
- monthly tracker (+fun formats?)
- grid w/column headings and row number (left or right) (spreadsheet)
- grid landscape w/column headings
- alternative rotation for landscape mode
- expense page 

TODO:
change font function
Date pages need consolodated force monday and use offset parameter
Generic draw title function for all pages
The calendar pages have a common routine for left, center, right drawing


TODO Potential common attributes:
spacing
Line style (dash, dotted)
draw flags for line and frame
xmargin y margin
color Font
title font, size, color

"""

# import argparse
# import sys
import os
import datetime
from datetime import date
from dateutil import parser
import calendar
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

def parse_date_value(val):
    """Parse a date-like value into a datetime.date.

    Accepts datetime.date, datetime.datetime, or a string in a variety
    of common formats. Raises ValueError if parsing fails.
    """
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
        return val
    if isinstance(val, datetime.datetime):
        return val.date()
    if isinstance(val, str):
        s = val.strip()
        # Normalize common trailing punctuation
        s = s.strip().rstrip('.,')
        # Handle m/d, m/d/yy, mm/dd/yy, mm/dd/yyyy and variants where year is optional
        # Accept any non-digit separator (/, -, ., space)
        mmdy = re.match(r'^(?P<m>\d{1,2})\D+(?P<d>\d{1,2})(?:\D+(?P<y>\d{2,4}))?$', s)
        if mmdy:
            mm = int(mmdy.group('m'))
            dd = int(mmdy.group('d'))
            ygrp = mmdy.group('y')
            if ygrp is None or ygrp == '':
                year = datetime.date.today().year
            else:
                if len(ygrp) == 2:
                    year = 2000 + int(ygrp)
                else:
                    year = int(ygrp)
            try:
                return datetime.date(year, mm, dd)
            except Exception:
                # fall through to other parsing attempts
                pass

        # Try ISO format first
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            pass

        # Try a list of common formats
        fmts = [
            '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
            '%m-%d-%Y', '%m/%d/%Y', '%b %d %Y', '%b %d, %Y',
            '%B %d %Y', '%B %d, %Y', '%b%d%Y', '%d %b %Y', '%d %B %Y'
        ]
        for fmt in fmts:
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except Exception:
                continue

        # YYYYMMDD
        m = re.match(r'^(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2})$', s)
        if m:
            return datetime.date(int(m.group('y')), int(m.group('m')), int(m.group('d')))

        # Try python-dateutil if available for more fuzzy parsing
        try:
            from dateutil import parser as _parser
            return _parser.parse(s).date()
        except Exception:
            pass

    raise ValueError(f"Unrecognized date format: {val}")

def to_reportlab_color(val):
    if not isinstance(val, str):
        return val
    
    clean_val = val.replace('colors.', '').strip().lower()
    if clean_val.startswith('#'):
        return colors.HexColor(clean_val)
    try:  # handle named colors
        return getattr(colors, clean_val, colors.yellowgreen)
    except AttributeError:
        print(f"ValueError(Unknown color: {val} using black")
        return colors.black

#str2bool =  #lambda v: v.lower() in ['true', '1', 'yes']
str2bool = lambda v: (
    v if isinstance(v, bool)
    else str(v).strip().lower() in {"true", "1", "yes"}
)

class Page(ABC):
    DEFAULT_colorFrame = None
    DEFAULT_colorGrid = colors.lightgrey

    mid = Point(0,0) # mid.x, mid.y for center of page
    max = Point(0,0) # max.x, max.y for top right corner of page
    fontName = "Courier" # "Helvetica" "Times-Roman"
    
    def __init__(self, **kwargs):
        kwargs = self._convert_types(kwargs)
        self.colorFrame = kwargs.pop('colorFrame', self.DEFAULT_colorFrame)
        self.colorGrid = kwargs.pop('colorGrid', self.DEFAULT_colorGrid)
        # Common attributes for all pages
        self.title = kwargs.pop('title', None)
        self.date = kwargs.pop('date', datetime.date.today())
        # font settings
        self.fontsize = int(kwargs.pop('fontsize', 10))
        self.fontName = kwargs.pop('fontName', Page.fontName)
        self.colorFont = kwargs.pop('colorFont', colors.black)
        # margins (points)
        self.xMargin = kwargs.pop('xMargin', 10)
        self.yMargin = kwargs.pop('yMargin', 10)
        if 'drawFrame' in kwargs:
            self.drawFrame = kwargs.pop('drawFrame')
        else:
            self.drawFrame = True
                                      
        for key,value in kwargs.items():
            setattr(self, key, value)
        
        self.spacew = reportlab.pdfbase.pdfmetrics.stringWidth(' ', self.fontName, self.fontsize)/2 #half a space width

    CONVERTERS = {
        'colorFrame': to_reportlab_color,
        'colorGrid': to_reportlab_color,
        'colorFont': to_reportlab_color,
        'date': parse_date_value,
        'daystart': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'startTime': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'endTime': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'time': lambda v: datetime.datetime.strptime(v, '%H:%M').time(),
        'gridX': lambda v: int(v),
        'gridY': lambda v: int(v),
        'spacing': lambda v: float(v),
        'dash': lambda v: int(v),
        'drawFrame': lambda v: v.lower() in ['true', '1', 'yes'],
        'drawLines': lambda v: v.lower() in ['true', '1', 'yes'],
        'forceMon':  lambda v: v.lower() in ['true', '1', 'yes'],
        'forceMonday':  lambda v: v.lower() in ['true', '1', 'yes'],
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

    def setDash(self, canvas):
        dash = getattr(self, 'dash', None)
        if dash is not None:
            canvas.setDash(dash)
            dashOn = getattr(self, 'dashOn', dash) % 10
            dashOff = getattr(self, 'dashOff', dash) / 10
            canvas.setDash(dashOn, dashOff)

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
        if self.drawFrame and self.colorFrame is not None:
            canvas.setStrokeColor(self.colorFrame)
            canvas.rect(0,0, Page.max.x, Page.max.y)
        
        self.draw(canvas)
        canvas.restoreState()
    
    def startLandscape(self, canvas):
        canvas.saveState()
        self.inLandscape = True
        canvas.translate(Page.mid.x, Page.mid.y)
        canvas.rotate(90)
        canvas.translate(-Page.mid.y, -Page.mid.x)
        Page.mid = Point(Page.mid.y, Page.mid.x)
        Page.max = Point(Page.max.y, Page.max.x)

    
    def stopLandscape(self, canvas):
        canvas.restoreState()
        Page.mid = Point(Page.mid.y, Page.mid.x)
        Page.max = Point(Page.max.y, Page.max.x)
    
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
        canvas.setFont(self.fontName, self.fontsize)
        title = self.title if self.title is not None else 'Word Page'
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
        canvas.setStrokeColor(self.colorGrid)
        
        for x in range(0, int(Page.max.x), int(spacingX)):
            canvas.line(x, 0, x, Page.max.y)
        
        for y in range(int(Page.max.y), 0, -int(spacingY)):
            canvas.line(0, y, Page.max.x, y)

class DotPage(GridPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        spacingX, spacingY = self._calculate_spacing()
        self._draw_dots(canvas, spacingX, spacingY)

    def _draw_dots(self, canvas, spacingX, spacingY):
        """Draw dots at grid intersections instead of lines."""
        canvas.setFillColor(self.colorGrid)
        dot_radius = 1  # radius of the dots
        for x in range(0, int(Page.max.x), int(spacingX)):
            for y in range(0, int(Page.max.y), int(spacingY)):
                canvas.circle(x, y, dot_radius, stroke=0, fill=1)

class LinesPage(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        spacing = getattr(self, 'spacing', 0.25) * inch
        color = self.colorGrid
        dash = getattr(self, 'dash', None)
        Page.setDash(self, canvas)
        canvas.setStrokeColor(color)
        
        yStart = int(Page.max.y)
        #print(f"Lines title: {self.title} with fontsize {self.fontsize} and spacing {spacing}")
        if self.title is not None:
            fontName = self.fontName
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
        canvas.setStrokeColor(self.colorGrid)
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
        today = self.date
        #strLeft, strCenter, strRight = dailyHeader(today, formatStr=getattr(self, 'format', "ddmmm++yyyy"))
        strLeft, strCenter, strRight = buildDateHeader(today, formatStr=getattr(self, 'format', "%b %d\t\t%a"))
        time_cur = getattr(self, 'startTime', datetime.time(7, 30))
        time_inc = getattr(self, 'timeInc', 30) # minutes
        end_time = getattr(self, 'endTime', datetime.time(23, 0))
        timeSide = getattr(self, 'timeSide', 'left').lower()

        if isinstance(time_cur, str):
            time_cur = datetime.datetime.strptime(time_cur  , '%H:%M').time()

        y = int(Page.max.y)

        canvas.setFont(self.fontName, self.fontsize*1.5)
        if strLeft != '':
            canvas.drawString(10, y - (self.fontsize*1.5), strLeft)
        if strCenter != '':
            canvas.drawCentredString(Page.mid.x, y - (self.fontsize*1.5), strCenter)
        if strRight != '':
            canvas.drawRightString(Page.max.x - 10, y - (self.fontsize*1.5), strRight)
        canvas.line(0, y - (self.fontsize*1.5) - 5, Page.max.x, y - (self.fontsize*1.5) - 5)
        y -= self.fontsize * 4
        canvas.setFont(self.fontName, self.fontsize)

        Page.setDash(self, canvas)
        drawLines = getattr(self, 'drawLines', True)

        while y > int(self.fontsize/2) and time_cur < end_time:
            time_label = time_cur.strftime("%I:%M").lower()
            offset = self.fontsize * 0.25
            if timeSide == 'right':
                canvas.drawRightString(Page.max.x - 10, y, time_label)
                if drawLines:
                    linestart = Page.max.x - 10 - canvas.stringWidth(time_label, self.fontName, self.fontsize) - 5
                    canvas.line(10, y - offset, linestart, y - offset)
            else:
                canvas.drawString(10, y, time_label)
                if drawLines:
                    linestart = 10 + canvas.stringWidth(time_label, self.fontName, self.fontsize) + 5
                    canvas.line(linestart, y - offset, Page.max.x, y - offset)

            time_cur = (datetime.datetime.combine(datetime.date.today(), time_cur)
                        + datetime.timedelta(minutes=int(time_inc))).time()
            y -= self.fontsize * 1.25

class Weekly(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.title is None:
            self.title = 'Weekly Planner'

    def drawWeeklyFrames(self, canvas, isWeekend=False):
        canvas.setStrokeColor(self.colorGrid)
        canvas.rect(0, 0, Page.max.x, Page.max.y)
        canvas.line(0, Page.max.y/3, Page.max.x, Page.max.y/3)
        canvas.line(0, 2*Page.max.y/3, Page.max.x, 2*Page.max.y/3)
        if isWeekend:
            canvas.line(Page.max.x/2, Page.max.y/3, Page.max.x/2, 0)

    def draw(self, canvas):
        isWeekend = getattr(self, 'weekend', False)
        self.drawWeeklyFrames(canvas, isWeekend)
        formatStr = getattr(self, 'format', "%b%d\t%w")

        fontName = self.fontName
        fontSize = self.fontsize
        canvas.setFont(fontName, fontSize)
        
        lineHt = self.fontsize * 1.25
        dayVal = self.date
        #print(f"Weekly page with date {dayVal} and format '{formatStr}'")
        try:
            dayNum = parse_date_value(dayVal)
        except Exception as e:
            print(f"Warning: couldn't parse date '{dayVal}': {e}")
            dayNum = datetime.date.today()
        theDay = getMonday(dayNum)
        if isWeekend:
            theDay = theDay + datetime.timedelta(days=3)
             # start on Sunday if weekend mode
        ypos = Page.max.y - lineHt
        lstr, cstr, rstr = buildDateHeader(theDay, formatStr=formatStr)
        canvas.drawString(10, ypos, lstr)
        canvas.drawRightString(Page.max.x - 10, ypos, cstr)

        theDay = theDay + datetime.timedelta(days=1)
        ypos = ypos - (Page.max.y/3)
        lstr, cstr, rstr = buildDateHeader(theDay, formatStr=formatStr)
        canvas.drawString(10, ypos, lstr)
        canvas.drawRightString(Page.max.x - 10, ypos, cstr)

        theDay = theDay + datetime.timedelta(days=1)
        ypos = ypos - (Page.max.y/3)
        lstr, cstr, rstr = buildDateHeader(theDay, formatStr=formatStr)
        if isWeekend:
            canvas.drawString(10, ypos, lstr)
            canvas.drawRightString(Page.max.x/2 - 10, ypos, cstr)
            theDay = theDay + datetime.timedelta(days=1)
            lstr, cstr, rstr = buildDateHeader(theDay, formatStr=formatStr)
            canvas.drawString(Page.max.x/2 + 10, ypos, lstr)
            canvas.drawRightString(Page.max.x - 10, ypos, cstr)
        else:
            canvas.drawString(10, ypos, lstr)
            canvas.drawRightString(Page.max.x - 10, ypos, cstr)

        pass

class WorkWeek(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, canvas):
        self.startLandscape(canvas)

        today = self.date

        if hasattr(self, 'offset'): 
            today = offsetDate(today, self.offset)

        if getattr(self, "forceMon", False) or getattr(self, "forceMonday", True):
            today = nextMonday(today)
        ypos = int(Page.max.y) - self.fontsize*1.5
        xmgn = self.xMargin
        ymgn = self.yMargin
        xpos = xmgn
        dx = (Page.max.x - 2*xmgn)/5

        if self.title != None:
            strLeft, strCenter, strRight = buildDateHeader(today, formatStr=self.title)
            #strLeft, strCenter, strRight = buildDateHeader(today, formatStr=getattr(self, 'title', "\t%b %d\t"))

            if strLeft != '':
                canvas.drawString(xmgn, ypos, strLeft)
            if strCenter != '':
                canvas.drawCentredString(Page.mid.x, ypos, strCenter)
            if strRight != '':
                canvas.drawRightString(Page.max.x - xmgn, ypos, strRight)
            
            ypos -= self.fontsize

        # draw the grid lines for the five days
        canvas.setStrokeColor(self.colorGrid)
        headerBox = getattr(self, "headerBox", False)
        if headerBox:
            xpos = xmgn
            for x in range(5):  
                canvas.rect(xpos, ypos-self.fontsize*1.5, dx, self.fontsize*1.5)
                xpos += dx

        # draw the day headers
        temp = ypos
        ypos -= self.fontsize * 1.5
        xpos = xmgn
        for x in range(6):
            canvas.line(xpos, ypos, xpos, ymgn)
            xpos += dx
        xpos = Page.max.x - xmgn
        canvas.line(xmgn, ypos, xpos, ypos)
        canvas.line(xmgn, ymgn, xpos, ymgn)  # bottom of grid

        ypos = temp
        ypos -= self.fontsize * 1.2
        xpos = xmgn
        formatStr = getattr(self, 'format', "%d\t\t%w")
        for d in range(5):
            day = today + datetime.timedelta(days=(d))
            strLeft, strCenter, strRight = buildDateHeader(day, formatStr=formatStr)
            if strLeft != '':
                canvas.drawString(xpos+self.spacew, ypos, strLeft)
            if strCenter != '':
                canvas.drawCentredString(xpos+(dx/2), ypos, strCenter)
            if strRight != '':
                canvas.drawRightString(xpos+dx-self.spacew, ypos, strRight)
            xpos += dx
            
  
        self.stopLandscape(canvas)
        pass

class Monthly(Page):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.title is None:
            self.title = "%B %Y"
        self.doDays = str2bool(getattr(self, 'doDays', True))

    def draw(self, canvas):
        self.startLandscape(canvas)
        maxy = Page.max.y
        
        aday = getMonthStart("2026-07-01")
        #print (f"aday = {aday} and is weekday {aday.weekday()}")

        strLeft, strCenter, strRight = buildDateHeader(aday, formatStr=self.title)
        if strLeft != '':
            canvas.drawString(0+2, maxy-self.fontsize, strLeft)
        if strCenter != '':
            canvas.drawCentredString(Page.mid.x, maxy-self.fontsize, strCenter)
        if strRight != '':
            canvas.drawRightString(Page.max.x-2, maxy-self.fontsize, strRight)
        maxy -= self.fontsize*1.75

        canvas.setFont(self.fontName, self.fontsize*0.75)
        self.fontsize *= 0.6
        dw = Page.max.x / 7

        #draw day labels
        if self.doDays:
            for i in range(7):
                dayLabel = calendar.day_abbr[i]
                canvas.drawCentredString((i+0.5)*dw, maxy, dayLabel)
            maxy -= self.fontsize * 0.5

        dh = maxy / 5

        for i in range(0, 8):
            canvas.line(i*dw, 0, i*dw, maxy)
        for i in range (0, 6):
            canvas.line(0, i*dh, Page.max.x, i*dh)
          
        dayValue = 1
        onWeekday = 0
        tgtWeekday = aday.weekday()
        maxDay = calendar.monthrange(aday.year, aday.month)[1]
        for i in range (0,5):
            for j in range(0,7):
                if onWeekday >= tgtWeekday and dayValue <= maxDay:
                    canvas.drawString(j*dw+2, maxy - (i*dh) - (self.fontsize), f"{dayValue}")
                    dayValue += 1
                onWeekday += 1
        
        self.stopLandscape(canvas)

class PageFactory:
    _registry = {
        'blank': BlankPage,
        'grid': GridPage,
        'word':  WordPage,
        'lines': LinesPage,
        'line': LinesPage,
        'list': ListPage,
        'daily': Daily,
        'weekly': Weekly,
        'workweek': WorkWeek,
        'work': WorkWeek,
        'monthly': Monthly,
        'month': Monthly,
        'dot': DotPage,
        'dots': DotPage,
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

        self.init_default_pages()

    
    def init_default_pages(self):
        """Initialize eight default Planner pages as line pages."""
        #self.pages = [PageFactory.create_page('lines', colorGrid=colors.grey) for _ in range(8)]
        self.pages = [PageFactory.create_page('blank', colorFrame=colors.yellow) for _ in range(8)]

    def readDescription(self, filename=None):
        """Load page descriptions from a file.

        If no filename is provided or the file does not exist, the default
        eight line pages remain in place.
        """
        self.init_default_pages()
        if not filename or not os.path.exists(filename):
            return

        assigned = [False] * 8
        description_count = 0
        with open(filename, 'r', encoding='utf-8') as fh:
            for raw_line in fh:
                #print(f"Reading line: {raw_line.strip()}")
                if description_count >= 8:
                    break

                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue

                page_number = None
                line_body = line
                parts = line.split(None, 1)
                if parts and parts[0].isdigit():
                    page_number = int(parts[0])
                    line_body = parts[1].strip() if len(parts) > 1 else ''

                if not line_body:
                    continue

                try:
                    page = PlannerParser.parse_line(line_body, PageFactory)
                except Exception as e:
                    print(f"Warning: could not parse line '{line}': {e}")
                    continue

                if page is None:
                    continue

                if page_number is not None and 1 <= page_number <= 8:
                    target_index = page_number % 8
                    self.pages[target_index] = page
                    assigned[target_index] = True
                else:
                    for idx in range(8):
                        if not assigned[idx]:
                            self.pages[idx] = page
                            assigned[idx] = True
                            break

                description_count += 1

    def echoConfig(self):
        """Print a human-readable representation of the 8 planner pages."""
        print("Planner Configuration:")
        print("=" * 60)
        for idx, page in enumerate(self.pages):
            page_num = idx + 1
            if page is None:
                print(f"Page {page_num}: <None>")
            else:
                page_type = page.__class__.__name__
                print(f"Page {page_num}: {page_type}")
                
                # Print relevant attributes
                for attr, value in sorted(page.__dict__.items()):
                    if not attr.startswith('_'):
                        print(f"  {attr}: {value}")
        print("=" * 60)

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

    def makePlanner(self):
        self.create()
        self.build()
        
    def build(self):
        if self.author != None: self.canvas.setAuthor(self.author)
        if self.title != None: self.canvas.setTitle(self.title)
        if self.subject != None: self.canvas.setSubject(self.subject)
        if self.keywords != None: self.canvas.setKeywords(self.keywords)
        self.canvas.save()

def OLDdayString(date, format="ddmmmyyyy"):
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

def OLDdailyHeader(date, formatStr="+ddmmmyy+"):
    """
    Parse a date and format string to return three strings: left, center, right.
    
    Format codes:
    - d: day of month (1-31)
    - dd: day of month (01-31)
    - m: month number (1-12)
    - mm: month number (01-12)
    - mmm: month abbreviation (Jan-Dec, first letter capitalized)
    - MMM: month abbreviation (JAN-DEC, all caps)
    - mmmm: month name (January-December, first letter capitalized)
    - w: day of week single letter (M, T, W, R for Thu, F, J for Sat, S)
    - www: day of week abbreviation (Mon-Sun, first letter capitalized)
    - WWW: day of week abbreviation (MON-SUN, all caps)
    - wwww: day of week full name (Monday-Sunday)
    - n: week number (ISO week starting Monday, 1-53)
    - nn: week number (01-53)
    - yyyy: 4-digit year (e.g., 2026)
    - yy: 2-digit year (e.g., 26)
    - +: separator between left, center, right fields
    
    The + character separates left, center, and right fields:
    - "+ddmmmyy+" results in left='', center='ddmmmyy', right=''
    - "++ddmmmyy" results in left='', center='', right='ddmmmyy'
    - "ddmmmyy++" results in left='ddmmmyy', center='', right=''
    
    Returns:
        tuple: (leftStr, centerStr, rightStr)
    """
    if isinstance(date, str):
        date = datetime.datetime.fromisoformat(date).date()
    elif isinstance(date, datetime.datetime):
        date = date.date()
    elif not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date, datetime.datetime, or ISO date string")
    
    # Split format string by '+' to get left, center, right
    parts = formatStr.split('+')
    leftFmt = parts[0] if len(parts) > 0 else ''
    centerFmt = parts[1] if len(parts) > 1 else ''
    rightFmt = parts[2] if len(parts) > 2 else ''
    
    def replaceTokens(fmt):
        if not fmt:
            return ''
        
        day_name = date.strftime("%A")
        month_name = date.strftime("%B")
        month_abbrev = date.strftime("%b")
        day_num = date.day
        month_num = date.month
        year_num = date.year
        
        # Day of week single letter codes
        dow_single_map = {
            'Monday': 'M',
            'Tuesday': 'T',
            'Wednesday': 'W',
            'Thursday': 'R',
            'Friday': 'F',
            'Saturday': 'J',
            'Sunday': 'S'
        }
        dow_single = dow_single_map.get(day_name, day_name[0].upper())
        
        # Day of week abbreviation
        dow_abbrev = day_name[:3]
        
        # Get week number (ISO week, week starting Monday)
        iso_calendar = date.isocalendar()
        week_num = iso_calendar[1]
        
        token_map = {
            'wwww': day_name,
            'WWW': day_name.upper(),
            'www': dow_abbrev.capitalize(),
            'w': dow_single,
            'mmmm': month_name,
            'MMM': month_abbrev.upper(),
            'mmm': month_abbrev.capitalize(),
            'mm': f"{month_num:02d}",
            'm': str(month_num),
            'yyyy': str(year_num),
            'yy': date.strftime("%y"),
            'dd': f"{day_num:02d}",
            'd': str(day_num),
            'nn': f"{week_num:02d}",
            'n': str(week_num),
        }
        
        # Sort by token length descending to match longer tokens first
        pattern = re.compile('(' + '|'.join(re.escape(token) for token in sorted(token_map.keys(), key=len, reverse=True)) + ')')
        result = pattern.sub(lambda m: token_map[m.group(1)], fmt)
        return result
    
    leftStr = replaceTokens(leftFmt)
    centerStr = replaceTokens(centerFmt)
    rightStr = replaceTokens(rightFmt)
    
    return leftStr, centerStr, rightStr

def buildDateHeader(date, formatStr="\t%d%b%y\t"):
    """Build a date header with left, center, and right fields.

    The format string is split using tab characters into three parts:
    left, center, and right. Each part is formatted with standard
    datetime.strftime directives.
    """
    if isinstance(date, str):
        try:
            date = parse_date_value(date)
        except Exception:
            date = datetime.datetime.fromisoformat(date).date()
    elif isinstance(date, datetime.datetime):
        date = date.date()
    elif not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date, datetime.datetime, or ISO date string")

    # Accept literal backslash-t escapes from config files as actual tab separators.
    formatStr = formatStr.replace('\\t', '\t')
    parts = formatStr.split('\t')
    parts += [''] * (3 - len(parts))
    left_fmt, center_fmt, right_fmt = parts[:3]

    # Support an additional custom token for a single-letter weekday.
    # Use '%w' in the format string to request the single capital
    # letter for the day of the week: M=Monday, T=Tuesday, W=Wednesday,
    # R=Thursday, F=Friday, S=Saturday, U=Sunday.
    def _format_part(fmt):
        if not fmt:
            return ''

        placeholder = '__DOW_LETTER__'
        replaced = False
        fmt_for_strftime = fmt

        # Prefer explicit "%w" (user-visible) but also accept bare 'w'
        if '%w' in fmt_for_strftime:
            fmt_for_strftime = fmt_for_strftime.replace('%w', placeholder)
            replaced = True
        """
        cme I got rid of this, I don't want this, we want to be able to put w
        elif 'w' in fmt_for_strftime:
            fmt_for_strftime = fmt_for_strftime.replace('w', placeholder)
            replaced = True
        """

        # Use strftime for the rest of the formatting
        result = date.strftime(fmt_for_strftime)

        # If we replaced a token, substitute the single-letter weekday
        if replaced:
            # date.weekday(): Monday=0 .. Sunday=6
            dow_map = {0: 'M', 1: 'T', 2: 'W', 3: 'R', 4: 'F', 5: 'S', 6: 'U'}
            letter = dow_map.get(date.weekday(), '?')
            result = result.replace(placeholder, letter)

        return result

    left = _format_part(left_fmt)
    center = _format_part(center_fmt)
    right = _format_part(right_fmt)

    return left, center, right

def nextMonday(today):
    daysAhead = 0 - today.weekday()
    if daysAhead < 0: daysAhead += 7
    return today + datetime.timedelta(days=daysAhead)

def getMonday(date, dayOffset=0):
    """Given a date, return the Monday of that week with an optional day offset."""
    if isinstance(date, str):
        try:
            date = parse_date_value(date)
        except Exception:
            date = datetime.datetime.fromisoformat(date).date()
    elif isinstance(date, datetime.datetime):
        date = date.date()
    elif not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date, datetime.datetime, or ISO date string")
    
    # Calculate the Monday of the week
    monday = date - datetime.timedelta(days=date.weekday())
    
    # Apply the day offset
    target_date = monday + datetime.timedelta(days=dayOffset)
    
    return target_date

def offsetDate(aDate, offset):
    # Scenario 1: Offset is already an integer (add as days)
    if isinstance(offset, int):
        return aDate + datetime.timedelta(days=offset)
    
    # Scenario 2: Offset is a string that represents a plain integer (e.g., "5")
    if isinstance(offset, str) and offset.strip().isdigit():
        return aDate + datetime.timedelta(days=int(offset))
    
    # Scenario 3: Offset is a complex string (e.g., "2d 3w")
    if not isinstance(offset, str):
        raise TypeError("Offset must be an integer or a string.")
        
    total_days = 0
    
    # Regex breakdown:
    # (\d+) looks for one or more digits
    # \s* allows for optional spaces between the number and the unit
    # ([a-zA-Z]+) captures the unit letters (e.g., "w", "weeks", "d")
    matches = re.findall(r'(\d+)\s*([a-zA-Z]+)', offset)
    
    for amount_str, unit in matches:
        amount = int(amount_str)
        unit = unit.lower()
        
        if unit in ['d', 'day', 'days']:
            total_days += amount
        elif unit in ['w', 'wk', 'week', 'wks', 'weeks']:
            total_days += amount * 7
        else:
            raise ValueError(f"Unknown time unit found: '{unit}' passed to function offsetDate")
            
    return aDate + datetime.timedelta(days=total_days)

def getMonthStart(hint=None) -> date:
    # Scenario 1: No hint provided -> Return 1st of current month
    if hint is None:
        today = date.today()
        return date(today.year, today.month, 1)
    
    # Scenario 2: Hint is already a date (or datetime) object
    if isinstance(hint, date):
        return date(hint.year, hint.month, 1)
    
    # Scenario 3: Hint is an integer (month number 1-12)
    if isinstance(hint, int):
        if not (1 <= hint <= 12):
            raise ValueError("Month integer must be between 1 and 12.")
        return date(date.today().year, hint, 1)
    
    # Scenario 4: Hint is a string (could be a name, a date format, mm/yy, etc.)
    if isinstance(hint, str):
        cleaned_hint = hint.strip()
        
        # Guard rail: handle standalone integer strings safely (e.g., "5")
        if cleaned_hint.isdigit():
            month_num = int(cleaned_hint)
            if not (1 <= month_num <= 12):
                raise ValueError("Month integer string must be between 1 and 12.")
            return date(date.today().year, month_num, 1)
            
        try:
            # dateutil.parser.parse is incredibly smart. 
            # default=date.today() ensures missing info (like year) falls back to today.
            parsed_dt = parser.parse(cleaned_hint, default=date.today())
            return date(parsed_dt.year, parsed_dt.month, 1)
        except (ValueError, OverflowError):
            raise ValueError(f"Could not parse the date hint: '{hint}'")

    raise TypeError("Invalid hint type. Expected None, date, int, or str.")


def TEST_parse_date_value():
    today_year = datetime.date.today().year
    cases = [
        ("5/18", datetime.date(today_year, 5, 18)),
        ("05/18", datetime.date(today_year, 5, 18)),
        ("5/18/26", datetime.date(2026, 5, 18)),
        ("05/18/2026", datetime.date(2026, 5, 18)),
        ("5-18", datetime.date(today_year, 5, 18)),
        ("5.18", datetime.date(today_year, 5, 18)),
    ]

    for s, expected in cases:
        parsed = parse_date_value(s)
        print(f"parse_date_value('{s}') -> {parsed}")
        assert parsed == expected, f"Expected {expected} for '{s}', got {parsed}"

    # invalid date should raise
    try:
        parse_date_value("13/40")
        raise AssertionError("parse_date_value('13/40') should have raised")
    except ValueError:
        print("parse_date_value('13/40') correctly raised ValueError")

    print("All parse_date_value tests passed!")

def TEST_buildDateHeader_single_letter():
    # Monday 2026-05-25 should return 'M' using the '%w' token
    d = datetime.date(2026, 5, 25)
    left, center, right = buildDateHeader(d, '\t%w\t')
    print(f"buildDateHeader single-letter -> left:'{left}' center:'{center}' right:'{right}'")
    assert center == 'M', f"Expected 'M' for 2026-05-25, got '{center}'"
    # Sunday 2026-05-31 should return 'U'
    s = datetime.date(2026, 5, 31)
    _, center2, _ = buildDateHeader(s, '\t%w\t')
    assert center2 == 'U', f"Expected 'U' for 2026-05-31, got '{center2}'"
    # Regression: strings read from config files may contain literal backslash-t escapes.
    _, center3, _ = buildDateHeader(s, '\\t%d')
    assert center3 == '31', f"Expected '31' for literal escape string, got '{center3}'"
    print("All buildDateHeader single-letter tests passed!")

##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### 

def main():
    #Read command line arguments
    outputFilename = 'Planner.pdf'

    #TEST_parse_date_value()
    booklet = Planner(nameOut=outputFilename)
    booklet.readDescription('input.txt')
    #booklet.echoConfig()
    booklet.makePlanner()

if __name__ == '__main__':
    main()

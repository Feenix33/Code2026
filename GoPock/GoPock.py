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
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Font:
    name: str = "Helvetica"
    size: int = 12
    color: str = "black"

@dataclass
class Style:
    font : Font = field(default_factory=Font)
    # margin: int = 4
    drawFrame: bool = False
    colorFrame: colors.Color = colors.darkblue
    colorGrid: colors.Color = colors.lightgrey

@dataclass
class BookletStyle:
    margin: int = 10
    nameOut: str = "GoPock.pdf"
    
@dataclass
class PageSpec:
    page_type: str
    attrs: dict
    line_number: int

class PageFactory:
    # PAGE_TYPES = {
    #     "daily": DailyPage,
    #     "weekly": WeeklyPage,
    #     "monthly": MonthlyPage,
    #     "list": ListPage,
    # }
    _registry = {}

    @classmethod
    def register(cls, keyword):
        def decorator(page_class):
            cls._registry[keyword] = page_class
            return page_class
        return decorator
    
    @classmethod
    def create(cls, page_type, **attrs):
        # print(f"PageFactory: Creating page of type '{page_type}' with attributes {attrs}")
        page_class = cls._registry.get(page_type)
        if page_class is None:
            print(
                f"WARNING: Unknown page type '{page_type}'"
            )
            return None
        return page_class(**attrs)

class Page(ABC):
    DEFAULT_colorFrame = colors.blue
    DEFAULT_colorGrid = colors.lightgrey
    mid = Point(0,0) # mid.x, mid.y for center of page
    max = Point(0,0) # max.x, max.y for top right corner of page
 

    def __init__(self):
        self.book = None
        self.overrides = {}

    @abstractmethod
    def draw(self, canvas):
        pass

    def get_style(self, path):
        # print (f"Getting style for path '{path}'")
        # Page override?
        if path in self.overrides:
            # print (f"Found override for path '{path}': {self.overrides[path]}")
            return self.overrides[path]
        # Otherwise use book default
        return get_nested_attr(
            self.book.style,
            path
        )

    def render(self, canvas, rotate, corner):
        #print (f"Rendering page with title {self.title} at corner {corner} with rotate={rotate}")
        # print("BOOK STYLE ID:", id(self.book.style))
        # print("PAGE STYLE ID:", id(self.style) if hasattr(self, "style") else None)
        canvas.saveState()
        if rotate: 
            width, height = canvas._pagesize
            canvas.translate(width/2, height/2)
            canvas.rotate(180)
            canvas.translate(-width/2, -height/2)
        canvas.translate(corner.x, corner.y)

        #frame drawing logic
        if self.get_style("drawFrame") and self.get_style("colorFrame") is not None:
            canvas.setStrokeColor(self.get_style("colorFrame"))
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

@PageFactory.register("word")
class PageWord(Page):
    def __init__(self, title="Generic Word Page", **kwargs):
        super().__init__()
        self.title = title


    def draw(self, canvas):
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(Page.mid.x, Page.mid.y, self.title)

@PageFactory.register("text")
class TextPage(Page):
    def __init__(self, text="", title="Generic Text Page", **kwargs):
        super().__init__()
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
        self.docSize = landscape(letter) 
        # self.nameOut = "GoPock.pdf"
        self.style = Style()
        self.config = BookletStyle()
        self.pages = []
        #print ("Booklet initialized")
        pass

    def add_page(self, page=None):
        page.book = self
        self.pages.append(page)
        return page
  
    def computePaneCorners(self):
        width, height = self.docSize
        margin = self.config.margin
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

        corners = self.computePaneCorners()
        margin = self.config.margin
        Page.max.x = (self.docSize[0] - 8*margin) / 4
        Page.max.y = (self.docSize[1] - 4*margin) / 2
        Page.mid.x = Page.max.x / 2
        Page.mid.y = Page.max.y / 2
        self.canvas = Canvas(self.config.nameOut, pagesize=self.docSize)
        #self.drawFoldlines()
        n = 0
        for page in self.pages:
            if page is not None:
                #print (f"Rendering page {n}")
                page.render(self.canvas, rotate=(n not in [0,1,2,3]), corner=corners[n%4])
            n += 1
        
        self.canvas.save()

def set_nested_attr(obj, path, value):
    print("SETTING:", path, "=", value, "on", obj)

    parts = path.split(".")
    current = obj

    for part in parts[:-1]:
        print("  traversing:", part, "->", getattr(current, part))
        current = getattr(current, part)

    #print("  setting final:", parts[-1])
    setattr(current, parts[-1], value)

def build_book(book, specs, page_factory):
    for spec in specs:
        if spec.page_type == "book":
            for key, value in spec.attrs.items():
                try:
                    # print(f"Setting book config '{key}' to '{value}'")
                    set_nested_attr(
                        book.config,
                        key,
                        value
                    )
                except AttributeError:
                    print(
                        f"WARNING line "
                        f"{spec.line_number}: "
                        f"unknown book setting "
                        f"'{key}'"
                    )
            continue

        # Handle defaults
        if spec.page_type == "defaults":
            for key, value in spec.attrs.items():
                # print(f"Setting book style '{key}' to '{value}'")
                try:
                    set_nested_attr(
                        book.style,
                        key,
                        value
                    )
                except AttributeError:
                    print(
                        f"WARNING line "
                        f"{spec.line_number}: "
                        f"unknown style attribute "
                        f"'{key}'"
                    )
            continue

        #
        # Create page
        #
        print (f"Creating page of type '{spec.page_type}' with attributes {spec.attrs}")
        page = page_factory.create(
            spec.page_type,
            **spec.attrs
        )
        page.overrides = spec.attrs

        if page is None:
            print(
                f"WARNING line "
                f"{spec.line_number}: "
                f"unknown page type "
                f"'{spec.page_type}'"
            )
            continue
        book.add_page(page)
        pprint.pprint(page.__dict__)
    # print("\n----- Final Book State -----")
    # pprint.pprint(book.__dict__)

#########
# Utility Functions
########
import shlex

def get_nested_attr(obj, path):
    current = obj
    for part in path.split("."):
        # print (f"Accessing attribute '{part}' of object {current}")
        current = getattr(current, part)
    return current

def convert_value(value):
    """Convert strings into int, float, bool when appropriate."""

    value = value.strip()

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


def parse_attributes(text):
    """
    Parse:
        title="Shopping List" font.size=12

    into:
        {
            "title": "Shopping List",
            "font.size": 12
        }
    """

    attrs = {}
    tokens = shlex.split(text)

    for token in tokens:
        if "=" not in token:
            continue

        key, value = token.split("=", 1)
        attrs[key] = convert_value(value)
    return attrs

##############################

import shlex
def read_page_specs(filename):

    specs = []

    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    line_number = 0

    while line_number < len(lines):

        raw_line = lines[line_number]
        line = raw_line.strip()
        line_number += 1

        if not line:
            continue

        if line.startswith("#"):
            continue

        spec_start_line = line_number
        #
        # Multi-line block
        #
        if line.endswith("{"):

            page_type = line[:-1].strip()
            attrs = {}

            while line_number < len(lines):
                block_line = lines[line_number].strip()
                line_number += 1
                if block_line == "}":
                    break

                if not block_line:
                    continue

                if block_line.startswith("#"):
                    continue

                attrs.update(
                    parse_attributes(block_line)
                )
        #
        # Single-line entry
        #
        else:
            parts = shlex.split(line)
            page_type = parts[0]
            attrs_text = line[len(page_type):]
            attrs = parse_attributes(attrs_text)

        specs.append(
            PageSpec(
                page_type=page_type,
                attrs=attrs,
                line_number=spec_start_line
            )
        )
    return specs


import pprint
def main():
    booklet = Booklet()
    pprint.pprint(booklet.config)
    specs = read_page_specs("input.txt")
    print("----- After parsing -----")
    pprint.pprint(booklet.config)
    pprint.pprint(specs)

    build_book(
        booklet,
        specs,
        PageFactory
    )
    booklet.render()

if __name__ == '__main__':
    main()

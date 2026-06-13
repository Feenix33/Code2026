from abc import ABC, abstractmethod
import reportlab.lib.enums
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph
from reportlab.lib import colors

from data_classes import Point, Font
from utils import buildThreePart, get_nested_attr


# class Font:
#     name: str = "Helvetica"
#     size: int = 10
#     color: str = "black"

class PageFactory:
    _registry = {}

    @classmethod
    def register(cls, keyword):
        def decorator(page_class):
            cls._registry[keyword] = page_class
            return page_class
        return decorator

    @classmethod
    def create(cls, page_type, **attrs):
        page_class = cls._registry.get(page_type)
        if page_class is None:
            print(f"WARNING: Unknown page type '{page_type}'")
            return None
        return page_class(**attrs)

class Page(ABC):
    # DEFAULT_colorFrame = colors.blue
    # DEFAULT_colorGrid = colors.lightgrey
    mid = Point(0, 0)
    max = Point(0, 0)
    PageSequence = 1

    def __init__(self):
        self.book = None
        self.overrides = {}
        # Debug ID for each page
        self.debugID = "[" + self.__class__.__name__ + "_" + str(Page.PageSequence) + "]"
        Page.PageSequence += 1


    @abstractmethod
    def draw(self, canvas):
        pass

    def get_style(self, path):
        if path in self.overrides:
            return self.overrides[path]

        # First try page-specific defaults / page instance attributes
        try:
            return get_nested_attr(self, path)
        except AttributeError:
            pass

        # Then fall back to the book-wide shared style
        try:
            base_attr = get_nested_attr(self.book.style, path)
        except AttributeError:
            return None
        
        # Check if there are nested overrides for this path (e.g., "fontTitle.size")
        prefix = path + "."
        nested_overrides = {}
        for key, value in self.overrides.items():
            if key.startswith(prefix):
                nested_key = key[len(prefix):]
                nested_overrides[nested_key] = value
        
        # If we found nested overrides, apply them to a copy of the attribute
        if nested_overrides:
            from dataclasses import is_dataclass, replace
            import copy
            
            if is_dataclass(base_attr):
                # For dataclass objects (like Font), use dataclasses.replace()
                base_attr = replace(base_attr, **nested_overrides)
            else:
                # For other objects, create a shallow copy and setattr
                base_attr = copy.copy(base_attr)
                for key, value in nested_overrides.items():
                    setattr(base_attr, key, value)
        
        return base_attr

    def render(self, canvas, rotate, corner):
        canvas.saveState()
        if rotate:
            width, height = canvas._pagesize
            canvas.translate(width / 2, height / 2)
            canvas.rotate(180)
            canvas.translate(-width / 2, -height / 2)
        canvas.translate(corner.x, corner.y)

        if self.get_style("drawFrame") and self.get_style("colorFrame") is not None:
            canvas.setStrokeColor(self.get_style("colorFrame"))
            canvas.rect(0, 0, Page.max.x, Page.max.y)

        # print(f"Page max: {Page.max.x}, {Page.max.y} and mid: {Page.mid.x}, {Page.mid.y}")
        self.draw(canvas)
        canvas.restoreState()

    def buildParagraphStyle(
        self,
        name='CurrentStyle',
        textColor=colors.black,
        backColor=colors.white,
        alignment=reportlab.lib.enums.TA_LEFT,
        align=None,
        firstLineIndent=0,
        leftIndent=0,
        bulletIndent=0,
        fontName='Times',
        fontSize=10,
        spaceBefore=0,
        spaceAfter=None,
        leading=None,
    ):
        if leading is None:
            leading = int(fontSize * 1.2)
        if spaceAfter is None:
            spaceAfter = int(fontSize * 1.2)
        tempAlign = alignment if align is None else self.alignmentStrToEnum(align.lower())
        return ParagraphStyle(
            name=name,
            backColor=backColor,
            textColor=textColor,
            alignment=tempAlign,
            firstLineIndent=firstLineIndent,
            leftIndent=leftIndent,
            bulletIndent=bulletIndent,
            fontName=fontName,
            fontSize=fontSize,
            spaceBefore=spaceBefore,
            spaceAfter=spaceAfter,
            leading=leading,
        )

    def alignmentStrToEnum(self, align):
        mapping = {
            'left': reportlab.lib.enums.TA_LEFT,
            'center': reportlab.lib.enums.TA_CENTER,
            'right': reportlab.lib.enums.TA_RIGHT,
            'justify': reportlab.lib.enums.TA_JUSTIFY,
        }
        return mapping.get(align, reportlab.lib.enums.TA_LEFT)

    def useCanvasFont(self, canvas, font: Font):
        canvas.setFont(font.name, font.size)
        canvas.setFillColor(font.color)

    def printCanvasThreePart(self, canvas, y, formatStr=None, titleStr=None, date=None):
        strLeft, strCenter, strRight = buildThreePart(formatStr, titleStr, date)
        if strLeft != '':
            canvas.drawString(10, y - (canvas._fontsize*1.5), strLeft)
        if strCenter != '':
            canvas.drawCentredString(Page.mid.x, y - (canvas._fontsize*1.5), strCenter)
        if strRight != '':
            canvas.drawRightString(Page.max.x - 10, y - (canvas._fontsize*1.5), strRight)
        # canvas.line(0, y - (canvas._fontsize*1.5) - 5, Page.max.x, y - (canvas._fontsize*1.5) - 5)
        return y - canvas._fontsize * 4
    
@PageFactory.register("blank")
class PageBlank(Page):
    def __init__(self, **kwargs):
        super().__init__()

    def draw(self, canvas):
        pass

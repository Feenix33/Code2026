from abc import ABC, abstractmethod
import reportlab.lib.enums
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph
from reportlab.lib import colors

from data_classes import Point
from utils import get_nested_attr

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
    DEFAULT_colorFrame = colors.blue
    DEFAULT_colorGrid = colors.lightgrey
    mid = Point(0, 0)
    max = Point(0, 0)

    def __init__(self):
        self.book = None
        self.overrides = {}

    @abstractmethod
    def draw(self, canvas):
        pass

    def get_style(self, path):
        if path in self.overrides:
            return self.overrides[path]
        return get_nested_attr(self.book.style, path)

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

from dataclasses import dataclass, field
from reportlab.lib import colors

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Font:
    name: str = "Helvetica"
    size: int = 10
    color: str = "black"

@dataclass
class Style:
    font: Font = field(default_factory=Font)
    fontTitle: Font = field(default_factory=lambda: Font(size=12, color="blue"))
    titleFormat: str = "\t%s"
    date: str = None
    drawFrame: bool = False
    colorFrame: colors.Color = colors.red
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

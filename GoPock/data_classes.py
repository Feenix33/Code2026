from dataclasses import dataclass, field
from reportlab.lib import colors

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
    font: Font = field(default_factory=Font)
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

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
class LineSpec:
    color: colors.Color = colors.lightgrey
    width: float = 1.0
    dash: int = 0  # 10s = on 1s = off

@dataclass
class CheckboxSpec:
    color: colors.Color = colors.black
    symbol: str = "X"

@dataclass
class PageStyle:
    font: Font = field(default_factory=Font)
    fontTitle: Font = field(default_factory=lambda: Font(size=13, color=colors.black))
    titleFormat: str = "\t%s"
    date: str = None
    drawFrame: bool = False
    colorFrame: colors.Color = colors.red
    # colorGrid: colors.Color = colors.lightgrey
    colorLine: colors.Color = colors.lightgrey
    line: LineSpec = field(default_factory=LineSpec)

@dataclass
class BookletStyle:
    margin: int = 10
    nameOut: str = "GoPock.pdf"
    useRecipeAbbreviations: bool = False

@dataclass
class PageSpec:
    page_type: str
    attrs: dict
    line_number: int

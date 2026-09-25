from dataclasses import dataclass, field
# from models.styles import BookletStyle, PageStyle
from models.data_classes import Point, Token

@dataclass
class LinesPageDetail:
    spacing: float = 0.25  # inches from one line to next
    
@dataclass
class GridPageDetail:
    spacing: float = 0.25  # inches for the grid and make them square
    grid: Point = field(default_factory=lambda: Point(0.0, 0.0)) # override the spacing, if one is 0, then use spacing

@dataclass
class ListPageDetail:
    spacing: float = 0.0        # inches from one line to next else use font size
    number: int = 0             # max number of items 0 = infinite
    checkbox: str = 'x'         # x=boxes o=circles
    drawlines: bool = True      # draw lines or not
    mylist: list[str] = field(default_factory=list)

@dataclass
class TextPageDetail:
    spacer: bool = False  # put space between lines
    blanks: bool = False # if a line is blank, add a blank line between lines
    firstline: bool = False # if true, then the first line is a title

@dataclass
class MarkdownPageDetail:
    bogus: bool = False # placeholder

@dataclass
class RoffPageDetail:
    bogus: bool = False # placeholder

@dataclass
class DailyPageDetail:
    start: str = "7:00"
    end: str = "18:00"
    increment: int = 60
    day: str = None
    stretch: bool = True
    dividers: bool = True

@dataclass
class CalendarPageDetail:
    month: int | None = None
    year: int | None = None
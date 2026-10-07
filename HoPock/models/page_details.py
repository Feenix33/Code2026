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
class TrackMonthPageDetail:
    count: int = 0             # max number of items 0 = infinite
    checkbox: str = None        # x=boxes o=circles
    habits: str = None          # habits separated by | 
    label: bool = True          # put numbers in the boxes
    habitcount: str = None      # string representing how many boxes

@dataclass
class TrackWeekPageDetail:
    number: int = 0             # max number of items 0 = infinite
    checkbox: str = None        # x=boxes o=circles
    habits: str = None          # habits separated by | 
    header: bool = True         # print the DOW header
    dow: bool = False           # print DOW in the boxes
    portrait: bool = False      # default to draw landscape

@dataclass
class TextPageDetail:
    spacer: bool = False  # put space between lines
    blanks: bool = False # if a line is blank, add a blank line between lines
    firstline: bool = False # if true, then the first line is a title
    title_style: str = "title"      # style for the title
    body_style: str = "body"     # style for the body
    joinlines: bool = False        # if reading a file and this is true, join lines until a blank line is reached

@dataclass
class MarkdownPageDetail:
    bogus: bool = False # placeholder

@dataclass
class RoffPageDetail:
    bogus: bool = False # placeholder

@dataclass
class DailyPageDetail:
    start: str = "7:00"     # start time
    end: str = "18:00"      # end time
    increment: int = 60     # increment between start and end time
    day: str = None         # today's date
    stretch: bool = True    # auto change font size to fit 
    dividers: bool = True   # print lines to divide hours
    dayformat: str = "\t{dd} {mmmm} {yyyy} " #None   # format string for day headers/titles NOT IMPLEMENTED

@dataclass
class WeeklyPageDetail:
    day: str = None         # This is week, shifts to monday
    dayformat: str = " {ddd}\t\t{dd}{mmm} " #None   # format string for day headers/titles
    flipformat: bool = False    # flip the format string on the second page

@dataclass
class CoverPageDetail:
    box2text: str = None    # Text for box 2
    box3text: str = None    # Text for box 3
    titleyper: float = 0.875 # y percent pos of title 7/8
    box2yper: float = 0.5  # y percent pos of title 1/2
    box3yper: float = 0.25  # y percent pos of box3 1/4
    titleht: float = 0.25    # y percent of title box size
    titlefill: str = None   # fill color
    titlebox: bool = True   # draw the box around the title

@dataclass
class RecipePageDetail:
    blanks: bool = True             # if a line is blank, add a blank line between lines
    firstline: bool = False         # if true, then the first line is a title
    clean: bool = True              # Process through the cleaner
    spacer: bool = False            # put space between lines
    title_style: str = "title"      # style for the title
    body_style: str = "nospace"     # style for the body

@dataclass
class CalendarPageDetail:
    month: int | None = None
    year: int | None = None

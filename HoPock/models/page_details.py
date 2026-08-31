from dataclasses import dataclass, field
# from models.styles import BookletStyle, PageStyle
from models.data_classes import Point

@dataclass
class LinesPageDetail:
    spacing: float = 0.25  # inches from one line to next
    
@dataclass
class GridPageDetail:
    spacing: float = 0.25  # inches for the grid and make them square
    grid: Point = field(default_factory=lambda: Point(0.0, 0.0)) # override the spacing, if one is 0, then use spacing
    
@dataclass
class DailyPageDetail:
    start: str = "8:00"
    end: str = "17:00"
    increment: int = 30

@dataclass
class CalendarPageDetail:
    month: int | None = None
    year: int | None = None
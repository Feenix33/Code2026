from dataclasses import dataclass, field
from models.styles import BookletStyle, PageStyle

@dataclass
class LinesPageDetail:
    spacing: float = 0.25  # inches from one line to next
    
@dataclass
class DailyPageDetail:
    start: str = "8:00"
    end: str = "17:00"
    increment: int = 30

@dataclass
class CalendarPageDetail:
    month: int | None = None
    year: int | None = None
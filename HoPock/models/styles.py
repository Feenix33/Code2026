"""
Presentation styles
Note that the booklet style is the defaults for the booklet
The page style is the overrides of the booklet defaults
"""

from dataclasses import dataclass, field

@dataclass
class Font:
    name: str | None = None
    size: int | None = None
    color: str | None = None

@dataclass
class BookletStyle:
    font: Font = field(default_factory=lambda: Font(
        name = "Helvetica",
        size = 8,
        color = "black"
    ))
    border: int = 10


@dataclass
class PageStyle:
    font: Font = field(default_factory=Font)   # override font for this page
    showpage: int = 0   # show page number or not (for testing)


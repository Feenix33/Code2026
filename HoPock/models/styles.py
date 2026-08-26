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
class Line:
    color: str = "black"
    width: float = 1.0
    dash: int = 0  # 10s = on 1s = off


@dataclass
class BookletStyle:
    # Booklet parameters that should be global and not overriden by pages
    border: int = 10

    # Page parameters, can be overridden. Should see all of these in PageStyle
    font: Font = field(default_factory=lambda: Font(
        name = "Helvetica",
        size = 8,
        color = "black"
    ))
    showpage: int = 0   # show page number or not (for testing)


@dataclass
class PageStyle:
    # All these fields should be in the Booklet Style class 
    font: Font = field(default_factory=Font)   # override font for this page
    showpage: int = 0   # show page number or not (for testing)


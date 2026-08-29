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
    width: int = 1
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
    # font for title
    titlefont: Font = field(default_factory=lambda: Font(name = "Helvetica", size = 12, color = "blue"))

    # generic line for most drawing
    line: Line = field(default_factory=lambda: Line(color = "black", width = 1, dash = 0))

    # frame line (if used)
    frame: Line = field(default_factory=lambda: Line(color = "grey", width = 1, dash = 0))

    margin: int = 10 # margin inside the frame (another for each frame in booklet config)
    title: str = None #page title
    showframe: bool = False  # show the frame using frame Line
    showpage: bool = False   # show page number or not (for testing)


@dataclass
class PageStyle:
    # All these fields should be in the Booklet Style class 
    font: Font = field(default_factory=Font)   # page font
    titlefont: Font = field(default_factory=Font)   # page font
    line: Line = field(default_factory=Line)   # general line
    frame: Line = field(default_factory=Line)   # frame line

    margin: int = None # margin 
    showframe: bool = None # show the frame
    showpage: bool = None  # show page number or not (for testing)
    


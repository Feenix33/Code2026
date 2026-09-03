"""
config class
The definition get mapped into config classes
"""
from dataclasses import dataclass, field
from models.styles import BookletStyle, PageStyle
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape

import pprint

@dataclass
class PageConfig:
    page_type: str
    style: PageStyle | None = None  # common style itmes
    detail: object | None = None # extended itmes for each page
    titletext: str = None # page title
    # file: str = None  # file for content 
    file: str | Path | None = None
    text: list[str] = field(default_factory=list) # array of text to print
    # data_dir: str | None = None  # directory for data files - Added to simplify visibility to page class

 

@dataclass
class BookletConfig:
    pages: list[PageConfig]
    style: BookletStyle = field(default_factory=BookletStyle)
    panels: int = 8  # number of panels on a sheet -- should be 2, 4, 8
    outfile: str = "pocket.pdf"
    pagesize: tuple [float, float] = landscape(letter)
    margin: int = 10  # margin around all the frames. for 8 panel, there are 8 horiz and 4 vertical
    data_dir: str | None = None  # directory for data files
    addpages: bool = True  # add pages if a processor needs more space






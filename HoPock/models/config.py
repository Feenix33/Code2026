"""
config class
The definition get mapped into config classes
"""
from dataclasses import dataclass, field
from models.styles import BookletStyle, PageStyle
from reportlab.lib.pagesizes import letter, landscape
import pprint

@dataclass
class PageConfig:
    page_type: str
    style: PageStyle | None = None  # common style itmes
    detail: object | None = None # extended itmes for each page
    title: str = None # page title
    file: str = None  # file for content 
    text: list[str] = field(default_factory=list) # array of text to print
 

@dataclass
class BookletConfig:
    pages: list[PageConfig]
    style: BookletStyle = field(default_factory=BookletStyle)
    panels: int = 8  # number of panels on a sheet -- should be 2, 4, 8
    outfile: str = "pocket.pdf"
    pagesize: tuple [float, float] = landscape(letter)
    margin: int = 10  # margin around all the frames. for 8 panel, there are 8 horiz and 4 vertical

    # def __str__(self) -> str:
    #     return pprint(self.obj, depth=2, indent=4)
        # return pprint.pformat(self.obj)
    #     rtn = f"\nBOOKLET CONFIG\n" + "-"*40 + '\n'
    #     rtn += f"panels={self.panels} outfile={self.outfile}\n"
    #     n = 1
    #     for page in self.pages:
    #         rtn += f"{n} {page.page_type.upper()}: "
    #         rtn += f"{page.style}  text_len={len(page.text)}"
    #         rtn += "\n"
    #         n += 1
    #     rtn += "\n BOOKLET STYLE\n" + {self.style}
    #     return rtn








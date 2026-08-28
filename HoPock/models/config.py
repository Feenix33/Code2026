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
    style: PageStyle | None = None
    text: list[str] = field(default_factory=list)
    file: str = None
    detail: object | None = None


@dataclass
class BookletConfig:
    pages: list[PageConfig]
    style: BookletStyle = field(default_factory=BookletStyle)
    panels: int = 8
    outfile: str = "pocket.pdf"
    pagesize: tuple [float, float] = landscape(letter)
    margin: int = 10  # margin around all the frames. for 8 panel, there are 8 horiz and 4 vertical

    def __str__(self) -> str:
        return pprint.pformat(self.obj)
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








"""
config class
The definition get mapped into config classes
"""
from dataclasses import dataclass, field
from models.styles import BookletStyle, PageStyle
from reportlab.lib.pagesizes import letter, landscape

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
    output: str = "pocket.pdf"
    pagesize: tuple [float, float] = letter
    margin: int = 10


    def __str__(self) -> str:
        rtn = f"\nBOOKLET CONFIG\n" + "-"*40 + '\n'
        rtn += f"panels={self.panels} output={self.output}\n"
        n = 1
        for page in self.pages:
            rtn += f"{n} {page.page_type.upper()}: "
            rtn += f"{page.style}  text_len={len(page.text)}"
            rtn += "\n"
            n += 1
        return rtn








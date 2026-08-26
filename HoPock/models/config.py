"""
config class
The definition get mapped into config classes
"""
from dataclasses import dataclass, field
from models.styles import BookletStyle, PageStyle

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
    format: int = 8
    output: str = "pocket.pdf"

    def __str__(self) -> str:
        rtn = f"BOOKLET CONFIG\n"
        rtn += f"format={self.format} output={self.output}\n"
        n = 1
        for page in self.pages:
            rtn += f"{n} {page.page_type.upper()}: "
            rtn += f"{page.style}  text_len={len(page.text)}"
            rtn += "\n"
            n += 1
        return rtn








"""
exConfig.py
Experiment with configuration and data structures with inheritance
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Font:
    name: str = "Times New Roman"
    size: int = 12

@dataclass
class Margin:
    top: float = 1.0
    bottom: float = 1.0
    left: float = 1.0
    right: float = 1.0

class Style:
    def __init__(self, parent=None, **values):
        self.parent = parent
        self.values = values

    def get(self, name):
        if name in self.values:
            return self.values[name]

        if self.parent:
            return self.parent.get(name)

        raise KeyError(name)

class Book:
    def __init__(self):
        self.style = Style(
            font=Font("Arial", 12),
            margin=Margin(1, 1, 1, 1)
        )
        self.pages = []
    
    def add_page(self, page=None):
        if page is None:
            page = Page(self)

        self.pages.append(page)
        return page
    
    def render(self):
        # begine render logic
        print(f"Rendering the book")
        for page in self.pages:
            page.render(None)
        # add end render logic

class Page:
    def __init__(self, book, style=None):
        self.book = book

        self.style = Style(
            parent=book.style
        )

        if style:
            self.style.values.update(style)

    @abstractmethod
    def render(self, renderer):
        pass

class TextPage(Page):
    def __init__(self, book, text="", style=None):
        super().__init__(book, style)
        self.text = text

    def render(self, canvas=None):
        font = self.style.get("font")
        margin = self.style.get("margin")

        #canvas.set_font(font.name, font.size)

        # canvas.draw_text(
        #     margin.left,
        #     margin.top,
        #     "Hello World"
        # )
        print (f"Render set font: {font.name} {font.size}: {self.text}")


def main():
    book = Book()

    book.add_page(TextPage(book))

    book.add_page(TextPage(
        book,
        text="Hello, World!",
        style={
            "font": Font("Courier New", 14)
        }
    ))

    canvas = None
    book.render()

if __name__ == '__main__':
    main()

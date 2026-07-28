from page import Page, PageFactory
from data_classes import Font
from reportlab.pdfbase.pdfmetrics import stringWidth
import random
import re

@PageFactory.register("dice")
class PageDice(Page):
    def __init__(self, title="", **kwargs):
        super().__init__()
        # Set defaults
        self.title = title

    def get_style(self, path):
        style = super().get_style(path)
        if path == "font" and style is not None:
            from dataclasses import replace
            from data_classes import Font

            if isinstance(style, Font) and "font.name" not in self.overrides:
                return replace(style, name="Courier")
        return style

    def notworkingget_style(self, path):
        if path != "font":
            return super().get_style(path)

        base_font = None
        if self.book is not None and getattr(self.book, "style", None) is not None:
            base_font = super().get_style(path)

        if base_font is None:
            base_font = Font(name="Courier", size=8)

        nested_overrides = {
            key[len("font."):]: value
            for key, value in self.overrides.items()
            if key.startswith("font.")
        }
        if nested_overrides:
            from dataclasses import replace
            return replace(base_font, **nested_overrides)

        if path in self.overrides:
            return self.overrides[path]

        return base_font

    def parse_dice_string(self, s):
        if not isinstance(s, str):
            return 1, 6

        # Standardize to lowercase and split by 'd'
        parts = s.lower().split('d')

        # A valid split must result in exactly two parts (left and right)
        if len(parts) != 2:
            return 1, 6

        left, right = parts[0].strip(), parts[1].strip()

        try:
            # Convert left side (default to 1 if empty)
            x = int(left) if left else 1
            # Convert right side (default to 6 if empty)
            y = int(right) if right else 6
            return x, y
        except ValueError:
            # Returns defaults if strings contain non-digit characters
            return 1, 6

    def draw(self, canvas):
        # operating parameters
        dice_string = self.get_style("dice") or "1d6"
        throws, die = self.parse_dice_string(dice_string)
        prtw = len(str(throws * die))  # print width
        maxstring = ("8" * prtw) + " "
 
        self.useCanvasFont(canvas, self.get_style("fontTitle"))
        titleFormat = self.get_style("titleFormat")
        pageDate = self.get_style("date")
        y = self.max.y - self.next_line(canvas)
        title = self.title
        if title is None or len(title) == 0:
            title = dice_string
        self.printCanvasThreePart(canvas, y, formatStr=titleFormat, titleStr=title, date=pageDate)
        y -= self.next_line(canvas,2)

        myfont = self.get_style("font")
        self.useCanvasFont(canvas, myfont)

        w = stringWidth(maxstring, myfont.name, myfont.size)
        times = int((self.max.x - 20) / w) # how many throws on a row

        while y > canvas._leading:
            dice_row = ""
            for n in range(times):
                roll = 0
                for _ in range(throws):
                    roll += random.randint(1, die)
                dice_row += f"{roll:{prtw}d} "
            canvas.drawString(10, y, dice_row)
            y -= self.next_line(canvas)
        # print (dice_row)

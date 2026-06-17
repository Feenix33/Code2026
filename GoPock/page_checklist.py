from page import Page, PageFactory
from reportlab.lib.units import inch
from data_classes import CheckboxSpec, LineSpec
from dataclasses import field
import sys
# import pprint

@PageFactory.register("list")
@PageFactory.register("checklist")
class PageChecklist(Page):
    def __init__(self, title=None, spacing=0.3, checkboxSpec=None, count=1000, **kwargs):
        super().__init__()
        self.title = title
        self.spacing = spacing
        if checkboxSpec is None:
            self.checkbox = CheckboxSpec()
        else:
            self.checkbox = checkboxSpec
        self.count = count
        # print(f"DEBUG {self.debugID} FCN({sys._getframe().f_code.co_name}): {vars(self)}")

    def draw(self, canvas):
        spacing = self.get_style("spacing") * inch
        # colorLine = self.get_style("colorLine")
        # print(f"DEBUG {self.debugID} {vars(self)}")
        linespec = self.get_style("line")
        checkspec = self.get_style("checkbox")

        # draw the title
        if self.title is not None:
            yt = self.standardTitle(canvas, self.max.y - spacing)*1.2
        else:
            yt = 0
    
        # draw the lines
        yStart = self.max.y - 2*spacing -yt
        # while y > 0:
        #     canvas.line(0, y, self.max.x, y)
        #     y -= spacing

        # checkbox_size = self.fontsize * 0.8
        pagefont = self.get_style("font")
        if pagefont is not None:
            self.useCanvasFont(canvas, pagefont)
        checkbox_size = spacing * 0.6

        if checkspec.symbol in ["X", "x","✓", "✔"]:
            checkbox = 'x'
        elif checkspec.symbol in ["O", "o", "○", "0"]:
            checkbox = 'o'
        else:
            checkbox = None

        checkline = LineSpec(color=checkspec.color, width=1, dash=0)
        margin = int (checkbox_size * 0.5)
        linecount = 0
        for y in range(int(yStart), int(checkbox_size/2), -int(spacing)):
            # Draw checkbox
            self.setLineSpec(canvas, checkline)
            if checkbox == 'x':
                canvas.rect(margin, y - checkbox_size/2, checkbox_size, checkbox_size)
            elif checkbox == 'o':
                canvas.circle(margin + checkbox_size/2, y, checkbox_size/2, stroke=1, fill=0)
            # Draw line for text
            self.setLineSpec(canvas, linespec)
            canvas.line(checkbox_size + (margin*2), y - checkbox_size*0.8, self.max.x-margin, y - checkbox_size*0.8)

            linecount += 1
            if linecount >= self.count:
                break
"""
markdown processor
Simplistic markdown processor
Handled commands:
# Heading1
## Heading2 - HeadingN
* bullet list
+ bullet list
1 numbered list
''' code block

*italics* _italics_
**bold** __bold__
**_bold italic_**
~~strikethrough~~

"""
from processors.base import Processor
from collections import deque
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from processors.reportlab_style_gen import ReportLabStyleProvider

class MarkdownProcessor(Processor):

    def process(self, text, styles:ReportLabStyleProvider, titletext=None, **kwargs):
        fifo = deque()

        sty_body = styles.get("body")
        sty_heading1 = styles.get("heading1")
        sty_heading2 = styles.get("heading2")

        if titletext and len(titletext) > 0:
            fifo.append(Paragraph(titletext, styles.get("Title")))

        for line in text:
            command = line.split(" ", 1)[0]
            remainder = line.split(" ", 1)[1]
            if command == "#":
                style = sty_heading1
                line = remainder
            elif command.startswith("##"):
                style = sty_heading2
                line = remainder
            else:
                style = sty_body
            fifo.append(Paragraph(line, style))
        return fifo
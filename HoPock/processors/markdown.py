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
> Indent block

*italics* _italics_
**bold** __bold__
**_bold italic_**
~~strikethrough~~

Notes:
The heading command goes to the end of the line
Regular text keeps pulling lines until there are two CR. If there is one, then they text lines are part of the same paragraph
Code block symbol at the beginning and end of a line, each CR is a 'paragraph'
Potential alternative is [links] could be rendered underlined
Appears that combining text into a paragraph also is for bullets. To end a bullet need the next bullet or two CR (i.e. blank line)
Multiple blank line CRs are joined in the output. Blank line rendered as space between paras
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
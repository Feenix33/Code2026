"""
Plain text processor
"""
from processors.base import Processor
from collections import deque
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from processors.reportlab_style_gen import ReportLabStyleProvider

"""
Note that this worked
         fifo.append(Paragraph(line, styles.get("body", spaceAfter=20)))
"""
class PlainTextProcessor(Processor):

    #def process(self, text, rlstyles:ReportLabStyles, titletext=None, space_after=None, first_line=False, blanks=False, **kwargs):
    def process(self, text, styles:ReportLabStyleProvider, titletext=None, first_line=False, blanks=False, **kwargs):
        """
        first_line: the text buffer first line is title
        blanks: if text has a blank line, put in a spacer
        """

        fifo = deque()

        startq = 0

        # spacer_height = rlstyles.body.fontSize
        spacer_height = styles.get("body").fontSize

        # Handle title string if passed
        if titletext and len(titletext) > 0:
            line = titletext
            fifo.append(Paragraph(line, styles.get("title")))
            # startq += 1

        # process the first line
        if first_line and len(text) > 0:
            line = text[0]
            # fifo.append(Paragraph(line, rlstyles.title))
            fifo.append(Paragraph(line, styles.get("title")))
            startq += 1

        for line in text[startq:]:
            if len(line) == 0:
                if blanks:
                    # logger.debug("XXXXX TextPage.draw: Empty line")
                    fifo.append(Spacer(0, spacer_height))
            else:
                # fifo.append(Paragraph(line, rlstyles.body))
                fifo.append(Paragraph(line, styles.get("body")))

        return fifo
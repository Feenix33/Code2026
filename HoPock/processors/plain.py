"""
Plain text processor
"""
from processors.base import Processor
from collections import deque
from models.reportlab_styles import ReportLabStyles
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak

class PlainTextProcessor(Processor):

    def process(self, text, rlstyles:ReportLabStyles, titletext=None, space_after=None, first_line=False, blanks=False, **kwargs):
        """
        space_after: modify the style to add spaceAfter if not defined
        first_line: the text buffer first line is title
        blanks: if text has a blank line, put in a spacer
        """
        # Handle the space_after parameter 
        if space_after is not None:
            rlstyles.body_style.space_after = rlstyles.body_style.fontSize
            rlstyles.title_style.space_after = rlstyles.title_style.fontSize

        fifo = deque()

        spacer_height = rlstyles.body_style.fontSize

        # Handle title string if passed
        if titletext and len(titletext) > 0:
            line = titletext
            fifo.append(Paragraph(line, rlstyles.title_style))

        # process the first line
        if first_line and len(text) > 0:
            line = text[0]
            fifo.append(Paragraph(line, rlstyles.title_style))
            # add check if need to add a spacer here

        for line in text[1:]:
            if len(line) == 0:
                if blanks:
                    # logger.debug("XXXXX TextPage.draw: Empty line")
                    fifo.append(Spacer(0, spacer_height))
            else:
                fifo.append(Paragraph(line, rlstyles.body_style))

        return fifo
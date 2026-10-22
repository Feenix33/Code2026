"""
Plain text processor
"""
from processors.base import Processor
from collections import deque
from reportlab.platypus import Frame, Paragraph, Spacer #, PageBreak
from processors.reportlab_style_gen import ReportLabStyleProvider
from utility import string_to_args

import logging
logger = logging.getLogger(__name__)

"""
Note that this worked
         fifo.append(Paragraph(line, styles.get("body", spaceAfter=20)))
"""

class SimpleTextProcessor(Processor):
    def process(self, text, styles:ReportLabStyleProvider, first_line=False, blanks=False, 
                title_style_name="title", body_style_name="body", **kwargs):
        """
        first_line: the text buffer first line is title
        blanks: if text has a blank line, put in a spacer
        title_style: Name of the title style
        body_style: Name of the body style

        """

        fifo = deque()
        startq = 0

        style_body = styles.get(body_style_name)
        style_title = styles.get(title_style_name)#, **title_overrides)
        spacer_height = style_body.fontSize

        # process the first line
        if first_line and len(text) > 0:
            line = text[0]
            fifo.append(Paragraph(line, style_title))
            startq += 1

        for line in text[startq:]:
            if len(line) == 0:
                if blanks:
                    fifo.append(Spacer(0, spacer_height))
            else:
                fifo.append(Paragraph(line, style_body))

        return fifo
